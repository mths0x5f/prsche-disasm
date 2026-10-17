"""Four omitted heap-consumer boundary candidates, evidence before any index edit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

import capstone
from capstone.x86 import X86_OP_IMM

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/270-heap-consumer-index'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CANDIDATES=((0x5697d0,0x5697e6),(0x569a40,0x569a6a),(0x569b10,0x569b3b),(0x56a1f0,0x56a37f))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def main():
    assert not (RUN/'preflight.json').exists(),'completed preflight immutable'
    RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path):
        path=Path(path).resolve();name=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        pins[name]=digest(path);return path
    for p in [__file__,ROOT/'research/binary-index/manual-functions.jsonl',ROOT/'research/binary-index/README.md',
              ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
              ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence/summary.json',
              ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence/gap-windows.json',
              ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py',ROOT/'scripts/research/audit-v2-x86-call-chain-258.py']:
        pin(p)
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    helper=module('helper221_270','scripts/research/experiment-v2-readonly-scalars-221.py')
    pebytes=module('pe270','scripts/research/audit-v2-x86-call-chain-258.py').original_bytes
    image=pin(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    sections=helper.sections(image)
    def offset(va):
        s=next(s for s in sections if s['va']<=va<s['va']+s['rawsize']);return s['raw']+va-s['va']
    catalog=[json.loads(line) for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf8').splitlines()]
    ranges=sorted((int(a,16),int(b,16),r['entry_va']) for r in catalog for a,b in r['ranges'])
    def owners(pc):return [v for a,b,v in ranges if a<=pc<=b]
    targets={a for a,b in CANDIDATES};direct_refs={a:[] for a in targets};reloc_refs={a:[] for a in targets}
    # Scan raw executable bytes for candidates; without an indexed boundary a
    # matching E8/E9 sequence is navigation only and is never promoted to a caller.
    for sec in sections:
        if not sec['flags']&0x20000000:continue
        raw=image[sec['raw']:sec['raw']+sec['rawsize']]
        for opcode in [0xe8,0xe9]:
            pos=raw.find(bytes([opcode]))
            while pos>=0:
                if pos+5<=len(raw):
                    pc=sec['va']+pos;target=(pc+5+struct.unpack_from('<i',raw,pos+1)[0])&0xffffffff
                    if target in targets:direct_refs[target].append(dict(pc=f'{pc:08x}',bytes=raw[pos:pos+5].hex(),mnemonic='call' if opcode==0xe8 else 'jmp',
                        catalog_owners=owners(pc),instruction_boundary_proven=False,navigation_only=True))
                pos=raw.find(bytes([opcode]),pos+1)
    pe=struct.unpack_from('<I',image,0x3c)[0];base=struct.unpack_from('<I',image,pe+52)[0]
    rva,size=struct.unpack_from('<II',image,pe+24+96+5*8);pos,end=offset(base+rva),offset(base+rva)+size
    while pos<end:
        page,length=struct.unpack_from('<II',image,pos);assert length>=8 and length%2==0 and pos+length<=end
        for p in range(pos+8,pos+length,2):
            word=struct.unpack_from('<H',image,p)[0]
            if word>>12!=3:continue
            site=base+page+(word&0xfff);target=struct.unpack_from('<I',image,offset(site))[0]
            if target in targets:reloc_refs[target].append(dict(site=f'{site:08x}',target=f'{target:08x}',catalog_owners=owners(site)))
        pos+=length
    indexed_direct={a:[] for a in targets}
    for lineno,line in enumerate((ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text(encoding='utf8').splitlines(),1):
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(CALL|JMP) 0x([0-9a-f]+)$',line)
        if m and int(m[4],16) in targets:indexed_direct[int(m[4],16)].append(dict(pc=m[1],bytes=m[2],mnemonic=m[3],line=lineno,catalog_owners=owners(int(m[1],16))))
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    rows=[];listing=[]
    for start,last in CANDIDATES:
        raw=pebytes(image,f'{start:08x}',last-start+1);ins=list(decoder.disasm(raw,start))
        assert sum(i.size for i in ins)==len(raw) and ins[-1].mnemonic=='ret' and ins[-1].address==last
        starts={i.address for i in ins};calls=[];branches=[];bad=[]
        for i in ins:
            if i.mnemonic=='call':
                assert i.operands[0].type==X86_OP_IMM;target=i.operands[0].imm
                calls.append(dict(pc=f'{i.address:08x}',target=f'{target:08x}',indexed_callee_owners=owners(target)))
            elif i.mnemonic.startswith('j'):
                assert i.operands[0].type==X86_OP_IMM;target=i.operands[0].imm
                branches.append(dict(pc=f'{i.address:08x}',target=f'{target:08x}',internal_boundary=target in starts))
                if target not in starts:bad.append(f'{i.address:08x}')
        assert not bad
        preceding=pebytes(image,f'{start-32:08x}',32);padding=len(preceding)-len(preceding.rstrip(b'\x90\xcc'))
        prior_end=start-padding-1
        following=pebytes(image,f'{last+1:08x}',16);trailing=len(following)-len(following.lstrip(b'\x90\xcc'))
        previous=max((r for r in ranges if r[1]<start),key=lambda r:r[1]);nextrow=min((r for r in ranges if r[0]>last),key=lambda r:r[0])
        text='; CANDIDATE '+f'{start:08x}'+' navigation only, no function entry accepted\n'+'\n'.join(
            f'{i.address:08x}  {i.bytes.hex()}  {i.mnemonic.upper()} {i.op_str}' for i in ins)+'\n'
        listing.append(text)
        rows.append(dict(candidate_entry=f'{start:08x}',candidate_end=f'{last:08x}',bytes=len(raw),body_sha256=hashlib.sha256(raw).hexdigest(),
            source_instruction_sha256=hashlib.sha256(text.encode('utf8')).hexdigest(),hex=raw.hex(),instructions=len(ins),calls=calls,branches=branches,
            preceding32_hex=preceding.hex(),preceding_padding_bytes=padding,preceding_raw_byte=f'{image[offset(prior_end)]:02x}',preceding_raw_pc=f'{prior_end:08x}',
            following16_hex=following.hex(),trailing_padding_bytes=trailing,
            nearest_prior_indexed_range=dict(start=f'{previous[0]:08x}',end=f'{previous[1]:08x}',entry=previous[2]),
            nearest_next_indexed_range=dict(start=f'{nextrow[0]:08x}',end=f'{nextrow[1]:08x}',entry=nextrow[2]),
            incoming_indexed_edges=indexed_direct[start],incoming_raw_E8_E9_candidates=direct_refs[start],incoming_HIGHLOW=reloc_refs[start],
            closed_internal_instruction_graph=True,authoritative_external_entry_proof=bool(indexed_direct[start] or reloc_refs[start]),
            disposition='hold_no_authoritative_entry_reference'))
    twins=[]
    fourth=rows[-1]
    for va in [0x53cbc0,0x571f90]:
        raw=pebytes(image,f'{va:08x}',400);ins=list(decoder.disasm(raw,va));ours=list(decoder.disasm(bytes.fromhex(fourth['hex']),0x56a1f0))
        assert len(ins)==len(ours)
        differences=[]
        for a,b in zip(ins,ours):
            if a.bytes!=b.bytes:differences.append(dict(relative_pc=a.address-va,indexed=a.bytes.hex(),candidate=b.bytes.hex(),indexed_instruction=a.mnemonic+' '+a.op_str,candidate_instruction=b.mnemonic+' '+b.op_str))
        twins.append(dict(indexed_entry=f'{va:08x}',bytes=400,instructions=len(ins),different_instructions=differences))
    (RUN/'candidate-listing.asm').write_text('\n'.join(listing),encoding='utf8',newline='\n')
    for name,h in pins.items():assert digest(ROOT/name)==h,('input drift',name)
    result=dict(kind='heap-consumer-boundary-preflight',original_sha256=SHA,rows=rows,indexed_twins=twins,
                focused_listing_sha256=digest(RUN/'candidate-listing.asm'),input_sha256=pins,before_after_guards=True,
                old_index_modified=False,supplemental_index_created=False,compiler_commands=0,native_commands=0,
                disposition='coordinator_review_required_no_index_edit',
                limits=['Contiguous decode,RET,padding and closed CFG are structural evidence, not alone an authoritative external functionentry.',
                        'RawE8/E9 matches outsideindexedboundaries are navigation candidates only.',
                        'No storage/implementation/ABI/functionacceptance is added.'])
    (RUN/'preflight.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(rows=[{k:r[k] for k in ['candidate_entry','candidate_end','bytes','incoming_indexed_edges','incoming_raw_E8_E9_candidates','incoming_HIGHLOW']} for r in rows],index_edited=False)))


if __name__=='__main__':main()

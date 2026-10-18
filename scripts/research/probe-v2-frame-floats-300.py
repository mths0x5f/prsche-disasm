"""Bounded original PE audit for frame float cells; no implementation side effects."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import capstone

ROOT=Path(__file__).resolve().parents[2]
PE=ROOT/'local/game/Porsche.exe'
INDEX=ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl'
ASM=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm'
TARGETS=(0x005b2764,0x005b47d8)
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def load_module(path):
    spec=importlib.util.spec_from_file_location('pe300',path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def main():
    pe=load_module(ROOT/'scripts/research/audit-v2-physical-file-storage-279.py')
    data,base,sections,file_offset,relocs=pe.parse_pe(PE)
    assert hashlib.sha256(data).hexdigest()==SHA
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    refs={t:[] for t in TARGETS}
    for line in INDEX.read_text(encoding='utf8').splitlines():
        row=json.loads(line)
        if not re.fullmatch(r'[0-9a-fA-F]{8}',row['to_va']):continue
        target=int(row['to_va'],16)
        if target in refs:refs[target].append(row)
    instruction_sites={t:[] for t in TARGETS}
    near=[]
    pattern=re.compile(r'^([0-9a-f]{8})  ([0-9a-f]+)  (.*)$')
    for line in ASM.read_text(encoding='utf8').splitlines():
        match=pattern.match(line)
        if not match:continue
        pc=int(match[1],16);raw=bytes.fromhex(match[2])
        ins=list(decoder.disasm(raw,pc))
        if len(ins)!=1 or ins[0].size!=len(raw):continue
        for op in ins[0].operands:
            if op.type!=capstone.x86.X86_OP_MEM or op.mem.base or op.mem.index:continue
            address=op.mem.disp & 0xffffffff
            for target in TARGETS:
                if not (target-16<=address<=target+16):continue
                item=dict(pc=f'{pc:08x}',address=f'{address:08x}',bytes=raw.hex(),
                          mnemonic=ins[0].mnemonic,width=op.size,
                          read=bool(op.access&capstone.CS_AC_READ),write=bool(op.access&capstone.CS_AC_WRITE))
                if address==target:instruction_sites[target].append(item)
                elif address<target+4 and address+op.size>target:near.append(dict(target=f'{target:08x}',**item))
    result={}
    for target in TARGETS:
        section=next(s for s in sections if s['va']<=target-base<s['va']+s['vsize'])
        offset=file_offset(target,4);bits=data[offset:offset+4]
        needle=target.to_bytes(4,'little');positions=[];pos=data.find(needle)
        while pos>=0:
            positions.append(pos);pos=data.find(needle,pos+1)
        occurrences=[]
        for pos in positions:
            containing=[x for x in instruction_sites[target]
                        if file_offset(int(x['pc'],16))<=pos<file_offset(int(x['pc'],16))+len(bytes.fromhex(x['bytes']))]
            at=next((s for s in sections if s['raw']<=pos<s['raw']+s['raw_size']),None)
            va=base+at['va']+pos-at['raw'] if at else None
            occurrences.append(dict(file_offset=f'{pos:08x}',va=f'{va:08x}' if va else None,
                                    HIGHLOW=bool(va and va-base in relocs),
                                    indexed_instruction=[x['pc'] for x in containing]))
        result[f'{target:08x}']=dict(section=section['name'],section_flags=f'{section["chars"]:08x}',
                                     original_bits=bits.hex(),relocations_inside_cell=[f'{base+r:08x}' for r in relocs if target<=base+r<target+4],
                                     index_refs=refs[target],indexed_instructions=instruction_sites[target],
                                     literal_occurrences=occurrences,
                                     interior_literals={f'+{i}':data.count((target+i).to_bytes(4,'little')) for i in (1,2,3)})
    output=dict(schema=1,original_sha256=SHA,cells=result,cross_boundary_direct_operands=near)
    run=ROOT/'iterations/v2/001-original-recovery/runs/300-frame-float-data'
    run.mkdir(parents=True,exist_ok=True)
    path=run/'original-evidence.json'
    if path.exists():raise FileExistsError('Evidence is immutable')
    path.write_text(json.dumps(output,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({key:dict(bits=value['original_bits'],refs=len(value['index_refs']),
                               instructions=len(value['indexed_instructions']),
                               raw=len(value['literal_occurrences']),
                               unmatched=sum(not item['indexed_instruction'] for item in value['literal_occurrences']),
                               unrelocated=sum(not item['HIGHLOW'] for item in value['literal_occurrences']))
                      for key,value in result.items()}))

if __name__=='__main__':main()

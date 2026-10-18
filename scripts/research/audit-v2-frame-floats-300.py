"""Independent read-only audit of Run300 PE evidence, COFF bytes and receipts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

import capstone

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/300-frame-float-data'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
EXPECTED={'005b47d8':('.p3lim','0000fa45','?frame_limit_005b47d8@porsche@@3MB',9),
          '005b2764':('.p3step','00401c46','?frame_step_005b2764@porsche@@3MB',26)}
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_shared_manifests import ManifestReader

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value

def coff_sections(path):
    raw=Path(path).read_bytes();machine,n,_,symtab,syms,opt,_=struct.unpack_from('<HHLLLHH',raw)
    assert machine==0x14c and opt==0
    sections={}
    for i in range(n):
        at=20+i*40;name=raw[at:at+8].rstrip(b'\0').decode('ascii')
        size,pos,_,_,relocs,_,flags=struct.unpack_from('<IIIIHHI',raw,at+16)
        sections[name]=dict(bytes=raw[pos:pos+size].hex(),size=size,relocations=relocs,flags=flags)
    return sections

def main():
    summary=load(RUN/'summary.json');validation=load(RUN/'validation.json')
    evidence=load(RUN/'original-evidence.json')
    assert summary['original_sha256']==evidence['original_sha256']==SHA
    assert validation['summary_sha256']==digest(RUN/'summary.json')
    reader=ManifestReader(ROOT)
    reader.verify({'input_manifest':summary['input_manifest']},expected_hash_mode='raw')
    reader.verify({'source_manifest':summary['source_manifest']},scope='source',expected_hash_mode='raw')
    receipt_path=ROOT/summary['compile_receipt']['path'];receipt=load(receipt_path)
    assert digest(receipt_path)==summary['compile_receipt']['sha256'] and receipt['exit_code']==0
    assert digest(ROOT/receipt['log'])==receipt['log_sha256']
    for name,expected in summary['output_sha256'].items():assert digest(ROOT/name)==expected
    pe=module('pe300audit',ROOT/'scripts/research/audit-v2-physical-file-storage-279.py')
    raw,base,sections,offset,relocs=pe.parse_pe(ROOT/'local/game/Porsche.exe')
    assert hashlib.sha256(raw).hexdigest()==SHA
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    assert evidence['cross_boundary_direct_operands']==[]
    for address,(section_name,bits,symbol,count) in EXPECTED.items():
        va=int(address,16);cell=evidence['cells'][address]
        sec=next(s for s in sections if s['va']<=va-base<s['va']+s['vsize'])
        assert sec['name']=='.rdata' and sec['chars']&0x40000000 and not sec['chars']&0x80000000
        assert raw[offset(va,4):offset(va,4)+4].hex()==bits==cell['original_bits']
        assert len(cell['index_refs'])==len(cell['indexed_instructions'])==len(cell['literal_occurrences'])==count
        assert cell['relocations_inside_cell']==[] and not any(cell['interior_literals'].values())
        locations=[]
        for item in cell['indexed_instructions']:
            pc=int(item['pc'],16);code=bytes.fromhex(item['bytes'])
            assert raw[offset(pc,len(code)):offset(pc,len(code))+len(code)]==code
            ins=list(decoder.disasm(code,pc));assert len(ins)==1 and ins[0].size==len(code)
            mem=[op for op in ins[0].operands if op.type==capstone.x86.X86_OP_MEM]
            assert len(mem)==1 and mem[0].size==4 and (mem[0].mem.disp&0xffffffff)==va
            assert mem[0].access&capstone.CS_AC_READ and not mem[0].access&capstone.CS_AC_WRITE
        needle=va.to_bytes(4,'little');pos=raw.find(needle)
        while pos>=0:
            locations.append(pos);pos=raw.find(needle,pos+1)
        assert sorted(locations)==sorted(int(row['file_offset'],16) for row in cell['literal_occurrences'])
        for item in cell['literal_occurrences']:
            assert item['HIGHLOW'] and len(item['indexed_instruction'])==1
            assert int(item['va'],16)-base in relocs
        assert all(row['type']=='READ' for row in cell['index_refs'])
        assert summary['original_read_sites'][address]==count
    obj=ROOT/summary['game_object']['path'];assert digest(obj)==summary['game_object']['sha256']
    sec=coff_sections(obj)
    for address,(name,bits,_,_) in EXPECTED.items():
        row=sec[name];assert row['size']==4 and row['bytes']==bits and row['relocations']==0
        assert row['flags']&0x40000000 and not row['flags']&0x80000000
    coff=module('coff300audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
    expected_symbols=sorted(row[2] for row in EXPECTED.values())
    symbols=coff.coff_symbols(obj)
    assert symbols==summary['symbols'] and symbols['defined']==expected_symbols and not symbols['undefined']
    summary295=load(ROOT/'iterations/v2/001-original-recovery/runs/295-frame-helpers/summary.json')
    tail=ROOT/next(row['path'] for row in summary295['game_objects'] if row['path'].endswith('00482e50.obj'))
    assert sorted(coff.coff_symbols(tail)['undefined'])==expected_symbols
    report=dict(schema=1,passed=True,original_sha256=SHA,summary_sha256=digest(RUN/'summary.json'),
                native_coff_bits=8,original_indexed_reads=35,read_only_symbols=2,compile_batches=1,
                game_link_not_run=True)
    output=RUN/'audit.json'
    if output.exists():
        if load(output)!=report:raise ValueError('Existing immutable audit differs')
    else:
        output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(report))

if __name__=='__main__':main()

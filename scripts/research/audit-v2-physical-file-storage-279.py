"""Run279 read-only preflight for the physical-file globals."""
import hashlib, json, struct
from pathlib import Path
import capstone

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/279-physical-file-storage'
PE_PATH=ROOT/'local/game/Porsche.exe'
PE_SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
TARGETS=(0x006af080,0x006af084)

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_bytes())

def parse_pe(path):
    data=Path(path).read_bytes(); pe=struct.unpack_from('<I',data,0x3c)[0]
    n=struct.unpack_from('<H',data,pe+6)[0]; oh=struct.unpack_from('<H',data,pe+20)[0]; magic=struct.unpack_from('<H',data,pe+24)[0]
    image_base=struct.unpack_from('<I',data,pe+24+28)[0]; sec_off=pe+24+oh; sections=[]
    for k in range(n):
        q=sec_off+40*k; name=data[q:q+8].split(b'\0',1)[0].decode('ascii')
        vs,va,raw_size,raw=struct.unpack_from('<IIII',data,q+8); chars=struct.unpack_from('<I',data,q+36)[0]
        sections.append({'name':name,'va':va,'vsize':vs,'raw_size':raw_size,'raw':raw,'chars':chars})
    def file_offset(va,size=1):
        rva=va-image_base
        for s in sections:
            if s['va']<=rva and rva+size<=s['va']+s['raw_size']:
                return s['raw']+rva-s['va']
        return None
    # IMAGE_DIRECTORY_ENTRY_BASERELOC is data-directory index 5.
    dd=pe+24+96+5*8 if magic==0x10b else pe+24+112+5*8
    reloc_rva,reloc_size=struct.unpack_from('<II',data,dd); relocs=[]; pos=file_offset(image_base+reloc_rva)
    end=pos+reloc_size
    while pos is not None and pos+8<=end:
        page,block=struct.unpack_from('<II',data,pos)
        if not page or block<8: break
        for j in range((block-8)//2):
            ent=struct.unpack_from('<H',data,pos+8+2*j)[0]
            if ent>>12==3: relocs.append(page+(ent&0xfff))
        pos+=block
    return data,image_base,sections,file_offset,set(relocs)

def catalog(path):
    out=[]
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        if line.strip(): out.append(json.loads(line))
    return out

def main():
    RUN.mkdir(parents=True,exist_ok=True)
    data,base,sections,file_offset,relocs=parse_pe(PE_PATH)
    assert digest(PE_PATH)==PE_SHA
    functions=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
    funcs=catalog(functions); cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); cs.detail=True
    indexed={t:[] for t in TARGETS}; target_instr_spans=[]
    for f in funcs:
        ranges=f.get('ranges',[])
        if len(ranges)!=1: continue
        start,end=(int(x,16) for x in ranges[0]); off=file_offset(start,end-start+1)
        if off is None: continue
        ins=list(cs.disasm(data[off:off+end-start+1],start))
        for i in ins:
            for o in i.operands:
                t=o.mem.disp&0xffffffff if o.type==capstone.x86.X86_OP_MEM and o.mem.base==0 and o.mem.index==0 else None
                if t not in TARGETS: continue
                access='write' if o.access&capstone.CS_AC_WRITE else 'read'
                sites=[x+base for x in relocs if i.address<=x+base<i.address+i.size]
                indexed[t].append({'pc':f'{i.address:08x}','function_va':f['entry_va'],'bytes':bytes(i.bytes).hex(),'instruction':f'{i.mnemonic} {i.op_str}','operand_size':o.size,'access':access,'HIGHLOW_sites':[f'{x:08x}' for x in sites]})
                target_instr_spans.append((off+i.address-start,off+i.address-start+i.size,t))
    cells={}
    for t in TARGETS:
        raw=data.find(t.to_bytes(4,'little')); positions=[]
        while raw>=0:
            positions.append(raw); raw=data.find(t.to_bytes(4,'little'),raw+1)
        sec=next(s for s in sections if s['va']<=t-base<s['va']+s['vsize'])
        delta=t-base-sec['va']; cells[f'{t:08x}']={'address':f'{t:08x}','width':4,'section':sec['name'],'section_characteristics':f'{sec["chars"]:08x}','section_delta':f'{delta:x}','raw_initial_bytes':None if delta>=sec['raw_size'] else data[sec['raw']+delta:sec['raw']+delta+4].hex(),'virtual_initial_zero':delta>=sec['raw_size'],'HIGHLOW_inside_cell':[f'{base+r:08x}' for r in relocs if t<=base+r<t+4],'raw_little_endian_occurrences':len(positions),'indexed_MEM4_refs':indexed[t],'indexed_ref_count':len(indexed[t]),'unindexed_raw_occurrences':len(positions)-sum(any(a<=p<b for a,b,_ in target_instr_spans) for p in positions)}
        in_spans=[p for p in positions if any(a<=p<b for a,b,_ in target_instr_spans)]
        gaps=[p for p in positions if p not in in_spans]
        def literal_count(value):
            b=value.to_bytes(4,'little'); i=data.find(b); n=0
            while i>=0: n+=1; i=data.find(b,i+1)
            return n
        cells[f'{t:08x}']['unindexed_raw_file_offsets']=[f'{p:08x}' for p in gaps]
        cells[f'{t:08x}']['interior_address_literal_occurrences']={f'+{k}':literal_count(t+k) for k in (1,2,3)}
    pins={}
    for p in [PE_PATH,functions,ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/defined-data.jsonl',ROOT/'iterations/v2/001-original-recovery/runs/224-canonical-owner-bindings/summary.json',ROOT/'iterations/v2/001-original-recovery/runs/250-writable-scalar-batch/preflight.json',ROOT/'iterations/v2/001-original-recovery/runs/254-writable-scalar-batch/summary.json',ROOT/'iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json',ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/files.cpp',ROOT/'iterations/v2/001-original-recovery/source/include/porsche/files.hpp']:
        pins[p.relative_to(ROOT).as_posix()]=digest(p)
    s={'schema':1,'run':279,'kind':'physical-file-storage-preflight','original_sha256':PE_SHA,'input_sha256':pins,'cells':cells,'source_owner':{'wip_source':'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/files.cpp','declaration':'iterations/v2/001-original-recovery/source/include/porsche/files.hpp','native_mangles':['?physical_count_006af080@porsche@@3HA','?physical_files_006af084@porsche@@3PAUPhysicalFile@1@A']},'accepted_canonical_evidence':'Run224 object inventory contains both mangles; this preflight does not grant allocation or acceptance.','current_274_symbol_note':'Run274 coordinator evidence reports no defined symbols containing either address; not rescanned here.','limits':['raw byte occurrences outside catalog instruction spans are unindexed gaps','physical_files is a pointer to 32-byte PhysicalFile records; adjacent 8-byte cells are not one scalar','no storage ownership/allocation or behavioral acceptance claim']}
    (RUN/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8',newline='\n')
    readme='''# Run 279 — physical-file storage preflight\n\n- `006af080` is a signed 32-bit count and `006af084` is a `PhysicalFile*` declaration in the current WIP `files.cpp`/`files.hpp`; Run224 records the corresponding canonical mangles.\n- Both addresses are adjacent 4-byte virtual-zero cells in writable `.data`; no HIGHLOW relocation lies inside either cell.\n- Exact indexed direct MEM4 references, raw-byte occurrences and unindexed gaps are recorded per cell in `summary.json`; pointer-record width and possible adjacent 8-byte base are kept separate.\n- This is navigation evidence only. WIP/canonical status, raw symbol consumers, whole-program address-taking and storage allocation remain blocked pending the listed gaps.\n'''
    (RUN/'README.md').write_bytes(readme.encode('utf-8'))
    print(json.dumps({'passed':True,'cells':{k:v['indexed_ref_count'] for k,v in cells.items()},'unindexed_raw':{k:v['unindexed_raw_occurrences'] for k,v in cells.items()}}))
if __name__=='__main__': main()

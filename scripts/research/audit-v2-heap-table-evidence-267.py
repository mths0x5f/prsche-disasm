"""Bounded, read-only heap-table evidence; no implementation or compilation."""
import bisect
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

import capstone
from capstone.x86 import X86_OP_MEM,X86_OP_IMM

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,END=0x6b4f20,0x6b4f60
TABLE='?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def storage_symbol(path,name):
    data=Path(path).read_bytes();machine,count,_,table,nsyms,optional,_=struct.unpack_from('<HHIIIHH',data)
    assert machine==0x14c and optional==0
    strings=data[table+nsyms*18:];symbols=[];i=0
    while i<nsyms:
        p=table+i*18;raw,value,section,typ,storage,aux=struct.unpack_from('<8sIhHBB',data,p)
        if raw[:4]==bytes(4):
            offset=struct.unpack_from('<I',raw,4)[0];symbol=strings[offset:].split(b'\0',1)[0].decode('ascii')
        else:symbol=raw.rstrip(b'\0').decode('ascii')
        symbols.append(dict(name=symbol,value=value,section=section,type=typ,storage=storage,aux=aux));i+=1+aux
    found=[r for r in symbols if r['name']==name and r['storage']==2 and r['section']>0]
    if not found:return dict(defined=False)
    assert len(found)==1
    row=found[0];p=20+(row['section']-1)*40
    secname=data[p:p+8].rstrip(b'\0').decode('ascii');size,raw,nreloc=struct.unpack_from('<III',data,p+16)
    # Offset24 is PointerToRelocations, not NumberOfRelocations.
    nreloc=struct.unpack_from('<H',data,p+32)[0];flags=struct.unpack_from('<I',data,p+36)[0]
    peers=sorted((r for r in symbols if r['section']==row['section'] and r['storage']==2),key=lambda r:r['value'])
    next_value=min([r['value'] for r in peers if r['value']>row['value']]+[size])
    return dict(defined=True,symbol=row,section=dict(name=secname,bytes=size,raw_offset=raw,relocations=nreloc,flags=f'{flags:08x}',
                    writable=bool(flags&0x80000000),executable=bool(flags&0x20000000)),
                extent_to_next_external=next_value-row['value'],same_section_external_symbols=peers,
                first64=(data[raw+row['value']:raw+row['value']+64] if raw else bytes(64)).hex())


def main():
    assert not (RUN/'summary.json').exists(),'completed267 immutable'
    RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('pin',path);pins[relative(path)]=h;return path
    helper=module('helper221_for267','scripts/research/experiment-v2-readonly-scalars-221.py')
    coff=module('coff267','scripts/research/build-v2-compile-corpus.py')
    definitions=module('definitions245_for267','scripts/research/plan-v2-link-frontier-245.py')
    for p in [__file__,ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py',ROOT/'scripts/research/build-v2-compile-corpus.py',
              ROOT/'scripts/research/plan-v2-link-frontier-245.py',ROOT/'scripts/research/experiment-v2-writable-scalars-250.py',
              ROOT/'scripts/research/screen-v2-writable-scalars-254.py',ROOT/'research/binary-index/README.md',ROOT/'research/binary-index/manual-functions.jsonl']:
        pin(p)
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();sections=helper.sections(image)
    def offset(va):
        sec=next(s for s in sections if s['va']<=va< s['va']+s['rawsize']);return sec['raw']+va-sec['va']
    def bytes_at(va,n):return image[offset(va):offset(va)+n]
    sec=next(s for s in sections if s['va']<=BASE and END<=s['va']+s['size'])
    assert sec['name']=='.data' and sec['flags']&0xc0000000==0xc0000000 and not(sec['flags']&0x20000000)
    assert BASE>=sec['va']+sec['rawsize'] and END<=sec['va']+sec['size']
    initial=dict(va=f'{BASE:08x}',bytes=64,hex=bytes(64).hex(),source='PE loader zero-filled virtual tail, not file bytes',section=sec)
    pe=struct.unpack_from('<I',image,0x3c)[0];base=struct.unpack_from('<I',image,pe+52)[0]
    rva,size=struct.unpack_from('<II',image,pe+24+96+5*8);pos,end=offset(base+rva),offset(base+rva)+size
    references=[];in_cell=[];reloc_count=0
    while pos<end:
        page,length=struct.unpack_from('<II',image,pos);assert length>=8 and length%2==0 and pos+length<=end
        for p in range(pos+8,pos+length,2):
            word=struct.unpack_from('<H',image,p)[0]
            if word>>12!=3:continue
            reloc_count+=1;site=base+page+(word&0xfff);target=struct.unpack('<I',bytes_at(site,4))[0]
            if BASE<=target<=END:references.append(dict(site=f'{site:08x}',target=f'{target:08x}'))
            if site<END and site+4>BASE:in_cell.append(dict(site=f'{site:08x}',target=f'{target:08x}'))
        pos+=length
    assert not in_cell
    catalog_path=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl')
    catalog=[json.loads(line) for line in catalog_path.read_text(encoding='utf8').splitlines()]
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))['functions']
    registered={r['entry_va']:r for r in registry if r.get('module')=='Porsche.exe'}
    ranges=sorted((int(a,16),int(b,16),r['entry_va']) for r in catalog for a,b in r.get('ranges',[]));starts=[a for a,b,v in ranges]
    def owners(pc):
        at=bisect.bisect_right(starts,pc)
        return sorted({v for a,b,v in ranges[max(0,at-8):at] if a<=pc<=b})
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    sites=sorted(int(r['site'],16) for r in references);by_site={int(r['site'],16):r for r in references};listed=set();listing_rows=[]
    listing=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for lineno,line in enumerate(listing.read_text(encoding='utf8').splitlines(),1):
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.+)$',line)
        if not m:continue
        pc=int(m[1],16);length=len(m[2])//2;at=bisect.bisect_left(sites,pc)
        selected=[]
        while at<len(sites) and sites[at]<pc+length:selected.append(sites[at]);at+=1
        if not selected:continue
        raw=bytes.fromhex(m[2]);assert bytes_at(pc,len(raw))==raw
        instructions=list(decoder.disasm(raw,pc));assert len(instructions)==1 and instructions[0].size==len(raw)
        i=instructions[0];ops=[]
        for op in i.operands:
            if op.type==X86_OP_MEM:
                ops.append(dict(kind='memory',width=op.size,access=op.access,base=i.reg_name(op.mem.base) if op.mem.base else None,
                    index=i.reg_name(op.mem.index) if op.mem.index else None,scale=op.mem.scale,displacement=f'{op.mem.disp&0xffffffff:08x}'))
            elif op.type==X86_OP_IMM:ops.append(dict(kind='immediate',width=op.size,value=f'{op.imm&0xffffffff:08x}'))
        own=owners(pc)
        row=dict(pc=m[1],bytes=m[2],instruction=m[3],line=lineno,catalog_owners=own,
                 accepted_owners=[v for v in own if v in registered],operands=ops,HIGHLOW=[by_site[s] for s in selected])
        listing_rows.append(row);listed.update(selected)
    gaps=[by_site[s] for s in sites if s not in listed]
    gap_candidates=[]
    for gap in gaps:
        site=int(gap['site'],16);candidates=[]
        for start in range(site-15,site+1):
            raw=bytes_at(start,20);ins=next(decoder.disasm(raw,start),None)
            if ins and ins.address<=site and site+4<=ins.address+ins.size:
                if site in [start+ins.disp_offset,start+ins.imm_offset]:
                    candidates.append(dict(pc=f'{start:08x}',bytes=ins.bytes.hex(),instruction=ins.mnemonic+' '+ins.op_str,
                                           catalog_owners=owners(start),navigation_only=True))
        gap_candidates.append(dict(**gap,overlapping_decode_candidates=candidates))
    # Full original windows proving extent, actual indexed store, clear and alias.
    windows={
      'slot_scan_00569a70':(0x569a70,28),
      'heap_init_store_005698ea':(0x5698ea,27),
      'heap_init_arena_pointer_00569842':(0x569842,29),
      'slot_clear_005699f0':(0x5699f0,72),
      'primary_heap_alias_005aef80':(0x5aef80,75),
      'preceding_object_end_0053cbc0':(0x53cbc0,56),
      'preceding_object_end_00571f90':(0x571f90,56),
    }
    evidence=[]
    for name,(pc,n) in windows.items():
        raw=bytes_at(pc,n);ins=list(decoder.disasm(raw,pc));assert sum(i.size for i in ins)==n,(name,n)
        evidence.append(dict(name=name,start=f'{pc:08x}',bytes=n,hex=raw.hex(),instructions=[dict(pc=f'{i.address:08x}',bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins]))
    source_root=ROOT/'iterations/v2/001-original-recovery/source';source_hits=[];definitions_found=[]
    for path in source_root.rglob('*'):
        if path.suffix not in ['.cpp','.hpp','.inc']:continue
        text=path.read_text(encoding='utf8')
        if not re.search(r'(?:6b4f(?:[2345][0-9a-f]|60)|heaps_006b4f20)',text,re.I):continue
        pin(path)
        hits=[dict(line=i,line_text=line.strip()) for i,line in enumerate(text.splitlines(),1) if re.search(r'(?:6b4f(?:[2345][0-9a-f]|60)|heaps_006b4f20)',line,re.I)]
        source_hits.append(dict(source=relative(path),hits=hits))
        code=definitions.remove_noncode(text)
        for m in re.finditer(r'(?m)^\s*(?!extern\b)OriginalHeap\s*\*\s*heaps_006b4f20\s*\[16\]\s*(?:\{\})?\s*;',code):
            definitions_found.append(dict(source=relative(path),line=code.count('\n',0,m.start())+1,private_fixture=path.name.endswith('_probe.cpp')))
    cached=[]
    for name in ['heap.obj','application_heap_init.obj']:
        path=pin(ROOT/'local/builds/v2/001-original-recovery/porsche_original.dir/Release'/name)
        cached.append(dict(object=relative(path),sha256=digest(path),symbols=coff.coff_symbols(path),table_storage=storage_symbol(path,TABLE)))
    private=ROOT/'local/builds/v2/001-original-recovery/application_heap_init_probe.dir/Release/application_heap_init_probe.obj'
    if private.exists():
        pin(private);cached.append(dict(object=relative(private),sha256=digest(private),private_fixture=True,symbols=coff.coff_symbols(private),table_storage=storage_symbol(private,TABLE)))
    assert cached[0]['table_storage']['defined'] and cached[0]['table_storage']['first64']==bytes(64).hex()
    assert cached[0]['table_storage']['extent_to_next_external']==64
    union=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/264-heap-release-union/summary.json'))
    frontier=[r for r in union['frontier'] if '6b4f' in r['symbol'].lower() and r.get('diagnostic_link_unresolved')]
    native_consumers=[]
    for row in frontier:
        for va in row['referring_object_vas']:
            result=next(r for r in union['results'] if r['va']==va);obj=pin(ROOT/result['object'],result['object_sha256'])
            symbols=coff.coff_symbols(obj);assert row['symbol'] in symbols['undefined']
            native_consumers.append(dict(consumer=va,object=relative(obj),sha256=digest(obj),undefined=row['symbol'],defined=symbols['defined']))
    globals_path=pin(ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export/globals.jsonl')
    metadata=[]
    for row in map(json.loads,globals_path.read_text(encoding='utf8').splitlines()):
        for variant in row.get('variants',[]):
            symbol=variant['symbol'];storage=symbol.get('storage','');m=re.fullmatch(r'([0-9a-f]{8}):(\d+)',storage)
            if m and int(m[1],16)<END+4 and int(m[1],16)+int(m[2])>BASE-4:
                metadata.append(row);break
    support_overlap=[]
    for summary in union.get('support_summaries',[]):
        packet=load(pin(ROOT/summary['path'],summary['sha256']))
        for obj in packet.get('support_objects',[]):
            for storage in obj.get('storage_sections',[]):
                for cell in storage.get('cells',[]):
                    va=cell.get('va');width=cell.get('bytes',4)
                    if va and int(va,16)<END and int(va,16)+width>BASE:support_overlap.append(dict(summary=summary['path'],cell=cell))
    accepted_heap=[r for r in registry if r.get('module')=='Porsche.exe' and r.get('source','').endswith(('/heap.cpp','/application_heap_init.cpp'))]
    for r in accepted_heap:pin(ROOT/r['verification_report'])
    assert not support_overlap
    for name,h in pins.items():assert digest(ROOT/name)==h,('before/after mutation',name)
    summary=dict(schema=1,kind='read-only-canonical-heap-table-evidence',original_sha256=SHA,target_va=f'{BASE:08x}',one_past=f'{END:08x}',
                 claimed_storage_bytes=64,initial_bits=initial,full_PE_HIGHLOW_count=reloc_count,table_or_endpoint_HIGHLOW=references,
                 in_cell_HIGHLOW=in_cell,indexed_operand_references=listing_rows,unindexed_operand_gaps=gap_candidates,
                 instruction_listing_coverage_complete=not gaps,function_catalog_coverage_gaps=[r['pc'] for r in listing_rows if not r['catalog_owners']],
                 windows=evidence,canonical_source_definitions=definitions_found,source_references=source_hits,cached_native_owners=cached,
                 accepted_canonical_heap_entries=accepted_heap,current_frontier=[{k:r.get(k) for k in ['symbol','va','category','referring_object_vas']} for r in frontier],
                 actual_current_native_consumers=native_consumers,ghidra_storage_metadata=metadata,existing_support_storage_overlap=support_overlap,
                 compiler_commands=0,native_execution_commands=0,new_accepted_functions=0,production_or_union_changed=False,input_sha256=pins,before_after_guards=True,
                 disposition='defer_for_unindexed_operand_gaps' if gaps else 'preflight_ready_for_coordinator_review',
                 limits=['64-byte table identity is proved by original pointer scan and canonical source/native owner, not byflags&15 alone.',
                         'PE virtualtail zeros prove loaderinitialbits, not a claim of filebackedzero bytes.',
                         'CachedwholeheapTU is inventory only; includes accepted algorithm definitions and cannot be added wholesale to union.',
                         'CurrentrawDAT_006b4f20 and canonicalarray shareoriginalbase; no alias/dataallocation implemented here.',
                         'No claim of original relative layout with adjacentglobals or absence of arbitrary runtimecomputed pointers.'])
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(passed=True,summary_sha256=digest(RUN/'summary.json'),input_pins=len(pins),before_after_guards=True,
          full_PE_relocations_checked=reloc_count,table_or_endpoint_references=len(references),listed_references=len(listed),unindexed_gaps=len(gaps),
          cached_native_objects=len(cached),compiler_commands=0,native_execution_commands=0))
    print(json.dumps(dict(disposition=summary['disposition'],refs=len(references),gaps=len(gaps),function_catalog_gaps=summary['function_catalog_coverage_gaps'],
                         canonical_storage_extent=cached[0]['table_storage']['extent_to_next_external'],pins=len(pins))))


if __name__=='__main__':main()

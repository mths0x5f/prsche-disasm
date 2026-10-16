"""Screen at most 24 Run248 scalar queue cells against actual PE, index, COFF and WIP owners."""
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import capstone
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'254-writable-scalar-batch'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):
    p=Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);o=importlib.util.module_from_spec(s);s.loader.exec_module(o);return o
def write(p,obj):Path(p).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    assert not (RUN/'screening.json').exists()
    RUN.mkdir(parents=True,exist_ok=True)
    pins={}
    def pin(p,expected=None):
        p=Path(p).resolve();sha=digest(p)
        assert expected is None or sha==expected,(p,sha,expected)
        pins[relative(p)]=sha;return p
    def guard():
        for p,sha in pins.items():assert digest(ROOT/p)==sha,('mutation',p)
    pin(Path(__file__));pin(Path(capstone.__file__))
    for dll in Path(capstone.__file__).parent.rglob('*capstone*.dll'):pin(dll)
    helper=module('helper254',pin(ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'))
    coff=module('coff254',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    selection=load(pin(RUNS/'248-next-scalar-selection/summary.json'))
    baseline=load(pin(RUNS/'243-canonical-reuse-union/summary.json'))
    pin(RUNS/'251-scalar-selection-corrections/summary.json')
    for name,sha in selection['input_sha256'].items():pin(ROOT/name,sha)
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    assert selection['original_sha256']==baseline['original_sha256']==SHA
    frontier={}
    for row in baseline['frontier']:
        if row.get('va'):frontier.setdefault(row['va'],[]).append(row)
    ordered=sorted(selection['not_selected_pool_vas'],key=lambda va:(-sum(len(r.get('referring_object_vas',[])) for r in frontier.get(va,[])),va))[:24]
    assert len(ordered)==24 and len(set(ordered))==24
    owner_vas=set()
    for run in ('221-readonly-scalar-storage','226-writable-scalar-storage','231-initialized-scalar-storage','242-shared-scalar-views','250-writable-scalar-batch'):
        summary=load(pin(RUNS/run/'summary.json'))
        for obj in summary.get('support_objects',[]):
            for sec in obj.get('storage_sections',[]):
                owner_vas.update(c['va'] for c in sec.get('cells',[]))
    sections=helper.sections(image)
    def offset(va):
        sec=next(s for s in sections if s['va']<=va<s['va']+s['rawsize'])
        return sec['raw']+va-sec['va']
    pe=struct.unpack_from('<I',image,0x3c)[0];base=struct.unpack_from('<I',image,pe+52)[0]
    rva,size=struct.unpack_from('<II',image,pe+24+96+5*8)
    pos,end=offset(base+rva),offset(base+rva)+size
    reloc_targets={va:[] for va in ordered};interior={va:[] for va in ordered};in_cell={va:[] for va in ordered}
    while pos<end:
        page,length=struct.unpack_from('<II',image,pos)
        assert length>=8 and length%2==0 and pos+length<=end
        for at in range(pos+8,pos+length,2):
            word=struct.unpack_from('<H',image,at)[0]
            if word>>12!=3:continue
            site=base+page+(word&0xfff)
            value=struct.unpack_from('<I',image,offset(site))[0]
            for va in ordered:
                n=int(va,16)
                if site<n+4 and site+4>n:in_cell[va].append(f'{site:08x}')
                if value==n:reloc_targets[va].append(site)
                elif n<value<n+4:interior[va].append(dict(site=f'{site:08x}',target=f'{value:08x}'))
        pos+=length
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    refs={va:[] for va in ordered};site_refs={va:[] for va in ordered};bad_index={va:[] for va in ordered}
    listing=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for line in listing.read_text(encoding='utf8').splitlines():
        targets=[va for va in ordered if '0x'+va in line.lower()]
        if not targets:continue
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        if not m:
            for va in targets:bad_index[va].append('parse:'+line[:80])
            continue
        pc,raw=int(m[1],16),bytes.fromhex(m[2])
        if image[offset(pc):offset(pc)+len(raw)]!=raw:
            for va in targets:bad_index[va].append('PE_byte_mismatch:'+m[1])
            continue
        ins=list(decoder.disasm(raw,pc))
        if len(ins)!=1 or ins[0].size!=len(raw):
            for va in targets:bad_index[va].append('decode:'+m[1])
            continue
        ins=ins[0]
        for va in targets:
            n=int(va,16)
            mem=[op for op in ins.operands if op.type==capstone.x86.X86_OP_MEM and (op.mem.disp&0xffffffff)==n]
            if len(mem)!=1 or mem[0].size!=4 or mem[0].mem.base or mem[0].mem.index or ins.disp_size!=4 or mem[0].access not in (1,2,3):
                bad_index[va].append('non_exact_MEM4:'+m[1]);continue
            site=pc+ins.disp_offset
            refs[va].append(dict(pc=m[1],bytes=m[2],instruction=m[3],access=mem[0].access,HIGHLOW_site=f'{site:08x}'))
            site_refs[va].append(site)
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    registered={r.get('entry_va') for r in registry['functions'] if r.get('module')=='Porsche.exe'}
    rg=pin(Path(shutil.which('rg')))
    command=[str(rg),'-n','-i','|'.join(ordered),str(ROOT/'iterations/v2/001-original-recovery/source')]
    p=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
    assert p.returncode in (0,1)
    owner_log=RUN/'owner-scan.log';owner_log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
    owner_hits={va:[] for va in ordered}
    for line in owner_log.read_text(encoding='utf8').splitlines():
        for va in ordered:
            if va in line.lower():owner_hits[va].append(line)
    rows=[]
    for va in ordered:
        n=int(va,16);native=frontier.get(va,[]);reasons=[]
        sec=next((s for s in sections if s['va']<=n and n+4<=s['va']+s['size']),None)
        if sec is None or sec['name']!='.data' or sec['flags']&0xc0000000!=0xc0000000 or sec['flags']&0x20000000 or n<sec['va']+sec['rawsize']:reasons.append('not_writable_virtual_zero_DWORD')
        if va in owner_vas:reasons.append('existing_scalar_data_owner')
        if va in registered:reasons.append('registered_function_owner')
        if owner_hits[va]:reasons.append('source_or_WIP_address_occurrence')
        if in_cell[va]:reasons.append('in_cell_HIGHLOW')
        if interior[va]:reasons.append('interior_pointer_target')
        if bad_index[va]:reasons.append('non_exact_indexed_instruction')
        if sorted(site_refs[va])!=sorted(reloc_targets[va]):reasons.append('HIGHLOW_index_coverage_gap')
        if not refs[va]:reasons.append('no_exact_direct_MEM4')
        if len(native)!=1 or native[0]['observed_conflict'] or len(native[0].get('ghidra_variants',[]))!=1:reasons.append('native_symbol_ambiguity')
        else:
            variant=native[0]['ghidra_variants'][0]['symbol']
            if variant.get('bytes')!=4 or variant.get('storage')!=va+':4' or native[0]['symbol'] not in (f'?DAT_{va}@@3HA',f'?DAT_{va}@@3IA'):reasons.append('native_non_scalar_view')
        overlaps=[]
        for other in baseline['frontier']:
            ova=other.get('va')
            if not ova or ova==va or other.get('category')!='data':continue
            for variant in other.get('ghidra_variants',[]):
                width=variant['symbol'].get('bytes')
                if isinstance(width,int) and width>0 and int(ova,16)<n+4 and int(ova,16)+width>n:overlaps.append(dict(va=ova,width=width))
        if overlaps:reasons.append('cross_VA_native_overlap')
        consumers=[]
        if len(native)==1:
            for caller in native[0]['referring_object_vas']:
                result=next((r for r in baseline['results'] if r['va']==caller),None)
                if result is None:reasons.append('missing_native_consumer_record');continue
                obj=pin(ROOT/result['object'],result['object_sha256'])
                actual=coff.coff_symbols(obj)
                if native[0]['symbol'] not in actual['undefined'] or any(va in s for s in actual['defined']):reasons.append('actual_COFF_symbol_mismatch')
                for name in result['include_closure']:pin(ROOT/name,baseline['input_sha256'][name])
                consumers.append(dict(caller=caller,object=relative(obj),object_sha256=digest(obj),undefined=native[0]['symbol']))
        rows.append(dict(va=va,fanout=sum(len(r.get('referring_object_vas',[])) for r in native),symbol=native[0]['symbol'] if len(native)==1 else None,section=sec,initial_bits='00000000' if sec and n>=sec['va']+sec['rawsize'] else None,complete_HIGHLOW_sites=[f'{site:08x}' for site in reloc_targets[va]],direct_MEM4=refs[va],uncovered_HIGHLOW=[f'{site:08x}' for site in sorted(set(reloc_targets[va])-set(site_refs[va]))],in_cell_HIGHLOW=in_cell[va],interior_targets=interior[va],index_anomalies=bad_index[va],overlap_views=overlaps,owner_hits=owner_hits[va],native_consumers=consumers,reasons=sorted(set(reasons)),safe=not reasons))
    guard()
    report=dict(schema=1,kind='bounded-writable-scalar-screening',original_sha256=SHA,queue_pool=48,screened=24,rank_policy='actual Run243 referring-object fanout descending, VA ascending',ranked_vas=ordered,safe_vas=[r['va'] for r in rows if r['safe']],deferred_vas=[r['va'] for r in rows if not r['safe']],rows=rows,owner_scan=dict(command=command,exit_code=p.returncode,log=relative(owner_log),log_sha256=digest(owner_log)),input_sha256=pins,before_after_guards=True,compiler_commands=0,native_commands=0,limits=['Current direct MEM4 and native views only; computed aliases/whole layout/lifetime unknown','Run248 is navigation, not proof'])
    write(RUN/'screening.json',report)
    print(json.dumps(dict(screened=24,safe=len(report['safe_vas']),deferred=len(report['deferred_vas']),safe_vas=report['safe_vas'],defer_reasons={r['va']:r['reasons'] for r in rows if not r['safe']})))
if __name__=='__main__':main()

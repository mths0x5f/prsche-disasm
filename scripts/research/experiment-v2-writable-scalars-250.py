"""Eight exact virtual-zero writable DWORDs; bounded data-only native packet."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'iterations/v2/001-original-recovery/runs'
RUN = RUNS/'250-writable-scalar-batch'
OUT = ROOT/'local/experiments/v2-writable-scalars-250'
VAS = ('00690848','00656864','00656ac0','006a6450','00699c84','00699fe0')
DEFERRED = {'0065b928':'existing application_core_address_0065b928 WIP address view and two writes; bind canonical owner first',
            '006c0508':['005a9de1','005a9e0a','005a9e1c','005a9e29']}

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main(finalize):
    import capstone
    hp=ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'
    h=load('helper250',hp)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve()
        sha=h.digest(path)
        assert expected is None or sha==expected,(path,sha,expected)
        pins[path]=sha
        return path
    def guard():
        for p,sha in pins.items(): assert h.digest(p)==sha,('input mutation',p)
    def run(command,name):
        command=list(map(str,command))
        start=time.perf_counter()
        p=subprocess.run(command,cwd=OUT,capture_output=True,timeout=120,env={**os.environ,'VSLANG':'1033'})
        log=OUT/(name+'.log')
        log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
        receipt=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log=h.relative(log),log_sha256=h.digest(log))
        h.write(OUT/(name+'.execution.json'),receipt)
        return receipt
    assert not (RUN/'summary.json').exists()
    if finalize: assert (OUT/'compile.execution.json').exists()
    else:
        assert not (OUT/'compile.execution.json').exists(), 'Do not overwrite a captured compilation'
        OUT.mkdir(parents=True,exist_ok=True)
    RUN.mkdir(parents=True,exist_ok=True)
    pin(Path(__file__)); pin(hp)
    pin(ROOT/'scripts/research/experiment-v2-writable-scalars-226.py')
    audit=load('audit250',pin(RUNS/'226-writable-scalar-storage/audit.py'))
    coff=load('coff250',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    pin(Path(capstone.__file__))
    for dll in Path(capstone.__file__).parent.rglob('*capstone*.dll'): pin(dll)
    selection=json.loads(pin(RUNS/'248-next-scalar-selection/summary.json').read_bytes())
    for name,sha in selection['input_sha256'].items(): pin(ROOT/name,sha)
    assert {r['va'] for r in selection['eligible']}==set(VAS)|set(DEFERRED)
    selected={r['va']:r for r in selection['eligible'] if r['va'] in VAS}
    assert selection['original_sha256']==h.SHA
    image=pin(ROOT/'local/game/Porsche.exe',h.SHA).read_bytes()
    sections=h.sections(image)
    def offset(va):
        sec=next(s for s in sections if s['va']<=va< s['va']+s['rawsize'])
        return sec['raw']+va-sec['va']
    for va,row in selected.items():
        n=int(va,16)
        sec=next(s for s in sections if s['va']<=n and n+4<=s['va']+s['size'])
        assert sec['name']=='.data' and sec['flags']&0xc0000000==0xc0000000 and not sec['flags']&0x20000000
        assert n>=sec['va']+sec['rawsize'] and n+4<=sec['va']+sec['size']
        assert row['initial_bits']=='00000000' and row['initial_bits_source']=='virtual_zero_tail_of_PE_section'
        assert len(row['native_symbols'])==1 and row['native_symbols'][0]==f'?DAT_{va}@@3'+('IA' if va=='00699fe0' else 'HA')
        assert not row['in_cell_highlow'] and not row['cross_va_overlap'] and not row['same_va_alias']
    assert all(abs(int(a,16)-int(b,16))>=4 for a in VAS for b in VAS if a!=b)
    pe=struct.unpack_from('<I',image,0x3c)[0]
    base=struct.unpack_from('<I',image,pe+52)[0]
    rva,size=struct.unpack_from('<II',image,pe+24+96+5*8)
    pos,end=offset(base+rva),offset(base+rva)+size
    targets={va:[] for va in VAS}; interior=[]; in_cell=[]; deferred_sites=[]
    while pos<end:
        page,length=struct.unpack_from('<II',image,pos)
        assert length>=8 and length%2==0 and pos+length<=end
        for at in range(pos+8,pos+length,2):
            word=struct.unpack_from('<H',image,at)[0]
            if word>>12!=3: continue
            site=base+page+(word&0xfff)
            value=struct.unpack_from('<I',image,offset(site))[0]
            if value==int('006c0508',16): deferred_sites.append(f'{site:08x}')
            for va in VAS:
                n=int(va,16)
                if site<n+4 and site+4>n: in_cell.append((va,site))
                if n<=value<n+4:
                    if value!=n: interior.append((va,site,value))
                    else: targets[va].append(site)
        pos+=length
    assert not in_cell and not interior
    deferred_indexed=set()
    for row in next(r for r in selection['eligible'] if r['va']=='006c0508')['consumer_sites']:
        raw=bytes.fromhex(row['bytes'])
        displacement=raw.find(bytes.fromhex('08056c00'))
        assert displacement>=0
        deferred_indexed.add(int(row['pc'],16)+displacement)
    assert [s for s in deferred_sites if int(s,16) not in deferred_indexed]==DEFERRED['006c0508']
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); decoder.detail=True
    listing=pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    refs={va:[] for va in VAS}; covered={va:[] for va in VAS}
    for line in listing.read_text(encoding='utf8').splitlines():
        match=[va for va in VAS if '0x'+va in line.lower()]
        if not match: continue
        m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
        assert m,line
        pc,raw=int(m[1],16),bytes.fromhex(m[2])
        assert image[offset(pc):offset(pc)+len(raw)]==raw
        decoded=list(decoder.disasm(raw,pc))
        assert len(decoded)==1 and decoded[0].size==len(raw)
        ins=decoded[0]
        for va in match:
            n=int(va,16)
            mem=[op for op in ins.operands if op.type==capstone.x86.X86_OP_MEM and (op.mem.disp&0xffffffff)==n]
            assert len(mem)==1 and mem[0].size==4 and not mem[0].mem.base and not mem[0].mem.index
            assert ins.disp_size==4 and mem[0].access in (capstone.CS_AC_READ,capstone.CS_AC_WRITE,capstone.CS_AC_READ|capstone.CS_AC_WRITE)
            site=pc+ins.disp_offset
            assert site in targets[va]
            covered[va].append(site)
            refs[va].append(dict(pc=m[1],bytes=m[2],instruction=m[3],access=mem[0].access,HIGHLOW_site=f'{site:08x}'))
    for va,row in selected.items():
        assert sorted(covered[va])==sorted(targets[va]),(va, 'missing', [f'{s:08x}' for s in sorted(set(targets[va])-set(covered[va]))], 'extra', [f'{s:08x}' for s in sorted(set(covered[va])-set(targets[va]))])
        assert len(refs[va])==row['direct_ref_count']==len(row['consumer_sites'])
        assert sum(bool(r['access']&1) for r in refs[va])==row['read_count']+row['readwrite_count']
        assert sum(bool(r['access']&2) for r in refs[va])==row['write_count']+row['readwrite_count']
        assert {(r['pc'],r['bytes']) for r in refs[va]}=={(r['pc'],r['bytes']) for r in row['consumer_sites']}
    baseline_path=pin(RUNS/'243-canonical-reuse-union/summary.json')
    baseline=json.loads(baseline_path.read_bytes())
    consumer_proof={}
    for va,row in selected.items():
        native=[r for r in baseline['frontier'] if r.get('va')==va]
        assert len(native)==1 and native[0]['symbol']==row['native_symbols'][0] and not native[0]['observed_conflict']
        assert all(v['symbol']['bytes']==4 and v['symbol']['storage']==va+':4' for v in native[0]['ghidra_variants'])
        consumer_proof[va]=[]
        for caller in native[0]['referring_object_vas']:
            result=next(r for r in baseline['results'] if r['va']==caller)
            obj=pin(ROOT/result['object'],result['object_sha256'])
            actual=coff.coff_symbols(obj)
            assert row['native_symbols'][0] in actual['undefined']
            assert not any(va in s for s in actual['defined'])
            for name in result['include_closure']: pin(ROOT/name,baseline['input_sha256'][name])
            consumer_proof[va].append(dict(caller=caller,object=h.relative(obj),sha256=h.digest(obj),undefined=row['native_symbols'][0]))
        for other in baseline['frontier']:
            other_va=other.get('va')
            if not other_va or other_va==va or other.get('category')!='data': continue
            for variant in other.get('ghidra_variants',[]):
                width=variant['symbol'].get('bytes')
                assert not (isinstance(width,int) and width>0 and int(other_va,16)<int(va,16)+4 and int(other_va,16)+width>int(va,16))
    registry=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())
    assert not any(r.get('module')=='Porsche.exe' and r.get('entry_va') in VAS for r in registry['functions'])
    rg=pin(Path(shutil.which('rg')))
    owner=run([rg,'-n','-i','|'.join(VAS),ROOT/'iterations/v2/001-original-recovery/source'],'owner-scan') if not finalize else json.loads(pin(OUT/'owner-scan.execution.json').read_bytes())
    assert owner['exit_code']==1 and not (OUT/'owner-scan.log').read_bytes()
    toolroot=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86'
    compiler_report=json.loads(pin(RUNS/'202-float-bit-stores/summary.json').read_bytes())
    compiler=pin(toolroot/'cl.exe',compiler_report['compiler_sha256'])
    for name in ('c1xx.dll','c2.dll'): pin(toolroot/name)
    linker=pin(toolroot/'link.exe')
    kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    sources=[pin(RUN/'original_scalars.cpp'),pin(RUN/'scalar_fixture.cpp')]
    preflight=RUN/'preflight.json'
    if finalize: pin(preflight)
    else:
        h.write(preflight,dict(schema=1,original_sha256=h.SHA,selected_vas=list(VAS),deferred=DEFERRED,original_MEM4=refs,complete_HIGHLOW_sites={va:[f'{site:08x}' for site in targets[va]] for va in VAS},in_cell_HIGHLOW=[],interior_targets=[],native_consumer_proof=consumer_proof,owner_scan=owner,original_relative_layout_claim=False,input_sha256={h.relative(p):sha for p,sha in pins.items()},safe_for_bounded_storage=True,limits=['Direct references only; computed aliases and whole layout unknown']))
        pin(preflight)
    objects=OUT/'objects'
    if not finalize: objects.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/Zl','/W4','/utf-8','/MP6']
    assert not os.environ.get('CL') and not os.environ.get('_CL_')
    command=[compiler,*flags,'/Fo'+str(objects)+os.sep,*sources]
    if finalize:
        captured=json.loads(pin(OUT/'prepare.json').read_bytes())
        for name,sha in captured['input_sha256'].items(): pin(ROOT/name,sha)
        compiled=json.loads(pin(OUT/'compile.execution.json').read_bytes())
        assert compiled['command']==list(map(str,command))
        pin(ROOT/compiled['log'],compiled['log_sha256'])
    else:
        guard()
        h.write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={h.relative(p):sha for p,sha in pins.items()}))
        compiled=run(command,'compile')
    assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
    assert not re.search(rb'\b(?:warning|error) C\d+',(OUT/'compile.log').read_bytes())
    obj=objects/'original_scalars.obj'
    symbols=coff.coff_symbols(obj)
    expected={row['native_symbols'][0] for row in selected.values()}
    assert set(symbols['defined'])==expected and not symbols['undefined'] and not symbols['common']
    parsed=audit.coff(obj)
    storage=next(s for s in parsed['sections'] if s['name']=='.ogw$zb')
    assert storage['size']==24 and storage['chars']&0xc0000000==0xc0000000 and not storage['chars']&0x20000000
    assert not any(s['reloc_count'] or (s['size'] and s['chars']&0x20000000) for s in parsed['sections'])
    assert parsed['bytes'][storage['raw']:storage['raw']+24]==b'\0'*24
    cells=[]
    for va,row in selected.items():
        sym=next(s for s in parsed['symbols'] if s['name']==row['native_symbols'][0])
        assert parsed['sections'][sym['section']-1]['name']=='.ogw$zb'
        assert 0<=sym['value']<=20 and sym['value']%4==0
        cells.append(dict(va=va,symbol=sym['name'],native_offset=sym['value'],initial_bytes='00000000'))
    assert sorted(c['native_offset'] for c in cells)==list(range(0,24,4))
    exe=OUT/'scalar_fixture.exe'
    if finalize: linked=json.loads(pin(OUT/'fixture-link.execution.json').read_bytes())
    else: linked=run([linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'scalar_fixture.obj',kernel],'fixture-link')
    assert linked['exit_code']==0
    fixture_pe=audit.pe(exe)
    fsec=next(s for s in fixture_pe['sections'] if s['name']=='.ogw')
    assert fsec['chars']&0xc0000000==0xc0000000 and not fsec['chars']&0x20000000
    assert fixture_pe['bytes'][fsec['raw']:fsec['raw']+24]==b'\0'*24
    assert not any(fsec['va']<=r<fsec['va']+24 for r in fixture_pe['reloc_rvas'])
    if finalize: native=json.loads(pin(OUT/'fixture-native.execution.json').read_bytes())
    else: native=run([exe],'fixture-native')
    assert native['exit_code']==0
    guard()
    report=dict(schema=1,kind='original-writable-data',original_sha256=h.SHA,functions_added=0,data_symbols=6,physical_data_cells=6,deferred=DEFERRED,actual_compiler_batches=1,actual_compiled_TUs=2,compiled=compiled,fixture_link=linked,native_fixture=native,fixture_executable=h.relative(exe),fixture_executable_sha256=h.digest(exe),support_objects=[dict(id='writable-virtual-zero-cells-250',compiled=True,compiler_exit_code=0,generated_source=h.relative(sources[0]),generated_source_sha256=h.digest(sources[0]),object=h.relative(obj),object_sha256=h.digest(obj),dependency_sha256={h.relative(sources[0]):h.digest(sources[0])},symbols=symbols,storage_sections=[dict(name='.ogw$zb',bytes='00'*24,flags=f"{storage['chars']:08x}",relocations=0,cells=cells)])],input_sha256={h.relative(p):sha for p,sha in pins.items()},preflight=h.relative(preflight),preflight_sha256=h.digest(preflight),original_memory_instructions_verified=sum(map(len,refs.values())),original_relative_layout_claim=False,finalized_existing_compile=finalize,limits=['Six current native scalar views only; no original data meaning or algorithm','006c0508 deferred: four HIGHLOW targets absent from indexed direct MEM4; trace exact instructions first','0065b928 deferred: existing WIP address provider needs canonical binding review','Direct HIGHLOW/MEM4 coverage does not prove computed aliases, whole layout or lifetime','No game function or production integration'])
    h.write(RUN/'summary.json',report)
    h.write(RUN/'validation.json',dict(passed=True,summary_sha256=h.digest(RUN/'summary.json'),input_guards_before_after=True,guarded_inputs=len(pins),physical_data_cells=6,deferred=DEFERRED,functions_added=0,compiler_exit_code=compiled['exit_code'],fixture_link_exit=linked['exit_code'],native_fixture_exit=native['exit_code'],original_HIGHLOW_sites=sum(map(len,targets.values())),original_relative_layout_claim=False))
    print(json.dumps(dict(cells=6,refs=sum(map(len,refs.values())),compile_exit=compiled['exit_code'],compile_seconds=compiled['seconds'],link_exit=linked['exit_code'],native_exit=native['exit_code'],pins=len(pins))))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--finalize-existing',action='store_true')
    main(parser.parse_args().finalize_existing)

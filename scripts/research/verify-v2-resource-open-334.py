"""Native original wrapper/callback chain for Run334; no production providers.

Both /Od and /O2 /GS production objects use the same guarded fixture. Its only
transform cell definition is test-local. Mutable callees and dispatcher are
recording boundaries, not implementations of their complete OS/heap behavior.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/334-resource-open'
BASE=ROOT/'local/experiments/v2-resource-open-334'
SOURCE=RUN/'resource_open_334.cpp'
HEADER=RUN/'resource_open_334.hpp'
TEMPLATE=RUN/'resource_open_fixture_334.cpp.in'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CASES=30240

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
    p=Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True,type=int)
    parser.add_argument('--negative-controls',action='store_true')
    args=parser.parse_args()
    assert args.attempt>0
    out=BASE/f'{args.attempt:03d}'
    assert not out.exists(),f'Immutable attempt exists: {out}'
    out.mkdir(parents=True);(out/'dependencies').mkdir()
    utility_path=ROOT/'scripts/research/verify-v2-pr9-resource-313.py'
    utility=module('includes334',utility_path);utility.RUN=RUN
    coff_path=ROOT/'scripts/research/build-v2-compile-corpus.py'
    coff=module('coff334',coff_path)
    dependency_path=ROOT/'scripts/research/audio_recovery_provenance.py'
    dependencies_helper=module('deps334',dependency_path)
    pe=ROOT/'local/game/Porsche.exe';assert sha(pe)==SHA
    image=pe.read_bytes()
    wrapper=utility.pe_at(image,0x561ca0,63);callback=utility.pe_at(image,0x561ce0,276)
    assert hashlib.sha256(wrapper).hexdigest()=='62cde604a74b26595127dfe81c686105a5a0f1efa3adfd6457a1f3c930a3fec7'
    assert hashlib.sha256(callback).hexdigest()=='d28a032e01cdc7be73ca9ac517af5eec551131a8bbc5f906e46e075cd37f6828'
    originals=[]
    for va,data in [(0x561ca0,wrapper),(0x561ce0,callback),(0x533b90,utility.pe_at(image,0x533b90,89))]:
        originals.append(dict(va=f'{va:08x}',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),raw_hex=data.hex()))
    assert originals[2]['raw_hex'][2*(0x533bd5-0x533b90):][:4]=='8bc6'
    literals=[]
    for va,expected in [(0x5bcd00,b'\\real\\cmn\\hlsfile.c'),(0x5bcd38,b'FILE_load - unable to open file %s\n'),(0x5bcd5c,b'FILE_load - unable to reserve memory for file %s\n')]:
        raw=utility.pe_at(image,va,len(expected)+1);assert raw==expected+b'\0'
        literals.append(dict(va=f'{va:08x}',bytes=len(raw),raw_hex=raw.hex(),sha256=hashlib.sha256(raw).hexdigest()))
    fixture=out/'native_fixture.cpp'
    fixture.write_text(TEMPLATE.read_text().replace('@WRAPPER@',','.join(map(str,wrapper))).replace('@CALLBACK@',','.join(map(str,callback))),encoding='utf8',newline='\n')
    vc=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    sdk=Path('C:/Program Files (x86)/Windows Kits/10');kit='10.0.26100.0'
    cl=vc/'bin/Hostx64/x86/cl.exe';link=cl.parent/'link.exe'
    include_root=ROOT/'iterations/v2/001-original-recovery/source/include'
    includes=[RUN,include_root,vc/'include',*[sdk/'Include'/kit/x for x in ('ucrt','shared','um')]]
    libs=[vc/'lib/x86/libcmt.lib',vc/'lib/x86/libvcruntime.lib',vc/'lib/x86/oldnames.lib',sdk/'Lib'/kit/'ucrt/x86/libucrt.lib',sdk/'Lib'/kit/'um/x86/kernel32.lib']
    shared=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/shared_runtime_globals.cpp'
    group=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/resource_dispatch_globals.cpp'
    pins={}
    def pin(p):
        p=Path(p).resolve();h=sha(p)
        assert p not in pins or pins[p]==h,f'input drift: {p}'
        pins[p]=h
    def guard():
        for p,h in pins.items():assert sha(p)==h,f'input drift: {p}'
    for p in [Path(__file__),SOURCE,HEADER,TEMPLATE,pe,fixture,shared,group,utility_path,coff_path,dependency_path,cl,link,cl.parent/'c1xx.dll',cl.parent/'c2.dll',*libs,
              ROOT/'iterations/v2/001-original-recovery/runs/327-resource-open-callback-evidence/evidence.json',ROOT/'research/binary-index/resource-open-callback-327.json',ROOT/'local/experiments/v2-rea-resource-325/001/receipt.json']:
        pin(p)
    for src in (SOURCE,fixture,shared,group):
        for p in utility.local_includes(src):pin(p)
    receipts={}
    def run(name,command):
        guard();started=time.perf_counter()
        process=subprocess.run(list(map(str,command)),cwd=out,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
        log=out/(name+'.log');log.write_bytes(process.stdout+process.stderr)
        receipt=dict(command=list(map(str,command)),exit_code=process.returncode,seconds=round(time.perf_counter()-started,6),log=rel(log),log_sha256=sha(log))
        write(out/(name+'.execution.json'),receipt);receipts[name]=receipt
        guard();return receipt
    common=[cl,'/nologo','/c','/TP','/std:c++17','/Oi','/Gy','/GR-','/EHsc','/W4','/utf-8',*[p for inc in includes for p in ('/I',inc)]]
    units=[('game-od',SOURCE,['/Od','/Oy-','/GS-']),('game-o2',SOURCE,['/O2','/GS']),('fixture',fixture,['/Od','/Oy-','/GS-']),('shared-globals',shared,['/Od','/GS-']),('group-globals',group,['/Od','/GS-'])]
    objects={}
    def compile_all(tag):
        for name,src,flags in units:
            obj=out/(name+'.obj');objects[name]=obj
            receipt=run(tag+'-'+name,[*common,*flags,'/sourceDependencies',out/'dependencies'/(name+'.json'),f'/Fo{obj}',src])
            assert receipt['exit_code']==0,(out/(tag+'-'+name+'.log')).read_text(errors='replace')
    compile_all('dependency-probe')
    deps=dependencies_helper.dependency_paths(out)
    for p in deps:pin(p)
    compile_all('compile');assert dependencies_helper.dependency_paths(out)==deps
    for p in objects.values():pin(p)
    views={}
    expected={'?file_open_00561ca0@porsche@@YAPAXPBDI@Z','?resource_open_callback_00561ce0@porsche@@YAHIPAX@Z'}
    for name in ('game-od','game-o2'):
        view=coff.coff_symbols(objects[name]);views[name]=view
        defined=set(view['defined'])
        literal_definitions=defined-expected
        assert expected<=defined and len(literal_definitions)<=3 and all(x.startswith('??_C@') for x in literal_definitions) and not view['common'],view
        cell=[x for x in view['undefined'] if 'resource_open_transform_006ad750' in x]
        assert len(cell)==1 and not any('resource_open_transform' in x for x in view['defined'])
    def link_fixture(name,game_obj,target):
        receipt=run(name,[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/INCREMENTAL:NO','/OPT:REF','/NODEFAULTLIB',f'/OUT:{target}',game_obj,objects['fixture'],objects['shared-globals'],objects['group-globals'],*libs])
        assert receipt['exit_code']==0,(out/(name+'.log')).read_text(errors='replace')
    native={}
    for name in ('game-od','game-o2'):
        exe=out/(name+'.exe');link_fixture(name+'-link',objects[name],exe);pin(exe)
        receipt=run(name+'-native',[exe]);native[name]=receipt
        assert receipt['exit_code']==0,(out/(name+'-native.log')).read_text()
        assert f'cases={CASES} ' in (out/(name+'-native.log')).read_text()
    negatives=[]
    if args.negative_controls:
        text=SOURCE.read_text()
        mutations=[
            ('late-group', '    const std::uint32_t group = resource_leaf_group_005df770;\n    context.callback_diagnostic_flag = 1;\n    const std::uint32_t device = file_device_name_00568e90(path);','    context.callback_diagnostic_flag = 1;\n    const std::uint32_t device = file_device_name_00568e90(path);\n    const std::uint32_t group = resource_leaf_group_005df770;'),
            ('early-flags','    const std::int32_t size = size_00533de0(handle, nested_group);\n    const std::uint32_t flags = context->opaque_08;','    const std::uint32_t flags = context->opaque_08;\n    const std::int32_t size = size_00533de0(handle, nested_group);'),
            ('early-transform','    (void)close_00533da0(handle, nested_group);\n    const ResourceOpenTransform transform = resource_open_transform_006ad750;','    const ResourceOpenTransform transform = resource_open_transform_006ad750;\n    (void)close_00533da0(handle, nested_group);'),
            ('check-read-result','    (void)read_00533bf0(handle, 0, buffer, static_cast<std::uint32_t>(size), nested_group);','    if (read_00533bf0(handle, 0, buffer, static_cast<std::uint32_t>(size), nested_group) == 0) return 0;'),
            ('missing-free','        (void)free_00531f90(buffer);','        /* missing free */'),
            ('boolean-return','    std::memcpy(&result, &word, sizeof(result));\n    return result;','    std::memcpy(&result, &word, sizeof(result));\n    return result != 0;'),
        ]
        for name,old,new in mutations:
            assert text.count(old)==1,(name,text.count(old))
            src=out/(name+'.cpp');src.write_text(text.replace(old,new),encoding='utf8',newline='\n');pin(src)
            obj=out/(name+'.obj')
            receipt=run(name+'-compile',[*common,'/O2','/GS',f'/Fo{obj}',src]);assert receipt['exit_code']==0,(out/(name+'-compile.log')).read_text(errors='replace')
            exe=out/(name+'.exe');link_fixture(name+'-link',obj,exe)
            receipt=run(name+'-native',[exe]);assert receipt['exit_code']==10,(out/(name+'-native.log')).read_text()
            negatives.append(dict(name=name,detected=True,exit_code=receipt['exit_code']))
    guard()
    outputs={rel(p):sha(p) for p in out.rglob('*') if p.is_file()}
    sources={rel(p):sha(p) for p in (SOURCE,HEADER,TEMPLATE,shared,group)}
    report=dict(schema=1,run=334,attempt=args.attempt,status='PASS',original_sha256=SHA,original_selected_bytes=339,original_vas=['00561ca0','00561ce0'],original_bodies=originals,original_literals=literals,native_cases_per_variant=CASES,native_cases_passed=2*CASES,variants=['/Od /Oy- /GS-','/O2 /GS'],native=native,source_sha256=sources,inputs_sha256={rel(p):h for p,h in pins.items()},outputs_sha256=outputs,receipts=receipts,coff_symbols=views,negative_controls=negatives,actual_dependencies=sorted(map(rel,deps)),guards_before_after=True,limits=['Dispatcher, open/size/alloc/read/close/free and transform effects are controlled native fixture boundaries.','Canonical00533b90 normalizes full EAX to0/1; bool reuse is verified only on that domain.','Transform006ad750 has no production definition; layout/setter/alias/full-game acceptance remains open.','Context+04 is never initialized or read by this consumer/fixture.','Diagnostic adapter explicitly reproduces x86 two-argument stack transport through the unchanged canonical cell.'])
    receipt=out/'receipt.json';write(receipt,report)
    summary=dict(schema=1,run=334,status='PASS',original_sha256=SHA,original_vas=report['original_vas'],original_selected_bytes=339,native_cases_passed=2*CASES,native_cases_per_variant=CASES,native_attemptdir=rel(out),native_receipt_sha256=sha(receipt),source_sha256=sources,coff_symbols=views,negative_controls=negatives,new_production_storage_definitions=0,transform_cell='extern-only typed boundary')
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(status='PASS',run=334,functions=2,pe_bytes=339,cases_passed=2*CASES,cases_total=2*CASES,negative_controls_detected=len(negatives),native_receipt_sha256=sha(receipt)))
    print(f'Run334 PASS:339B;{CASES} cases each Od/O2;{len(negatives)} mutations detected;receipt={rel(receipt)}')

if __name__=='__main__':main()

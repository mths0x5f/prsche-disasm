"""Run331: original111B drive letter helper, native Win32 import/AL contract."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/331-drive-letter'
BASE=ROOT/'local/experiments/v2-drive-letter-331'
PE=ROOT/'local/game/Porsche.exe'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE=RUN/'drive_letter_331.cpp'
HEADER=ROOT/'iterations/v2/001-original-recovery/runs/327-resource-open-callback-evidence/resource_device_327.hpp'
CANONICAL=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_search.cpp'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def relative(path):
    path=Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--attempt',type=int,required=True)
    parser.add_argument('--negative-controls',action='store_true')
    args=parser.parse_args()
    out=BASE/f'{args.attempt:03d}'
    assert not out.exists(),f'Immutable attempt already exists: {out}'
    out.mkdir(parents=True);(out/'dependencies').mkdir()
    utility=module('pe331',ROOT/'scripts/research/verify-v2-pr9-resource-313.py');utility.RUN=RUN
    coff=module('coff331',ROOT/'scripts/research/build-v2-compile-corpus.py')
    provenance=module('provenance331',ROOT/'scripts/research/audio_recovery_provenance.py')
    assert sha(PE)==SHA
    image=PE.read_bytes();body=utility.pe_at(image,0x5916a0,111)
    assert body[17]==0xe8 and 0x5916a0+22+struct.unpack_from('<i',body,18)[0]==0x5a2780
    assert body[37]==0xbe and struct.unpack_from('<I',body,38)[0]==0x5cd1f4
    assert utility.pe_at(image,0x5cd1f4,2)==b'.\0'
    assert body[58:60]==b'\xff\x15' and struct.unpack_from('<I',body,60)[0]==0x5b221c
    assert body[71:73]==b'\xff\x15' and struct.unpack_from('<I',body,73)[0]==0x5b2290
    template=RUN/'native_fixture_331.cpp';fixture=out/'native_fixture.cpp'
    fixture.write_text(template.read_text().replace('@BODY@',','.join(map(str,body))),encoding='utf8',newline='\n')
    vc=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    sdk=Path('C:/Program Files (x86)/Windows Kits/10');kit='10.0.26100.0'
    cl=vc/'bin/Hostx64/x86/cl.exe';link=cl.parent/'link.exe'
    includes=[RUN,ROOT/'iterations/v2/001-original-recovery/source/include',vc/'include',*[sdk/'Include'/kit/x for x in ('ucrt','shared','um')]]
    libs=[vc/'lib/x86/libcmt.lib',vc/'lib/x86/libvcruntime.lib',vc/'lib/x86/oldnames.lib',sdk/'Lib'/kit/'ucrt/x86/libucrt.lib',sdk/'Lib'/kit/'um/x86/kernel32.lib']
    pins={}
    def pin(path):
        path=Path(path).resolve();value=sha(path)
        if path in pins:assert pins[path]==value,f'input changed: {path}'
        pins[path]=value
    def guard():
        for path,value in pins.items():assert sha(path)==value,f'input changed: {path}'
    for path in [PE,Path(__file__),SOURCE,HEADER,CANONICAL,template,fixture,cl,link,cl.parent/'c1xx.dll',cl.parent/'c2.dll',*libs,ROOT/'scripts/research/verify-v2-pr9-resource-313.py',ROOT/'scripts/research/build-v2-compile-corpus.py',ROOT/'scripts/research/audio_recovery_provenance.py']:
        pin(path)
    for source in (SOURCE,CANONICAL,fixture):
        for path in utility.local_includes(source):pin(path)
    receipts={}
    def run(name,command):
        guard();start=time.perf_counter()
        process=subprocess.run(list(map(str,command)),cwd=out,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
        log=out/(name+'.log');log.write_bytes(process.stdout+process.stderr)
        record=dict(command=list(map(str,command)),exit_code=process.returncode,seconds=round(time.perf_counter()-start,6),log=relative(log),log_sha256=sha(log))
        write(out/(name+'.execution.json'),record);receipts[name]=record
        guard();return record
    common=[cl,'/nologo','/c','/TP','/std:c++17','/Od','/Oy-','/Gy','/GS-','/GR-','/EHsc','/W4','/utf-8',*[p for inc in includes for p in ('/I',inc)]]
    api_renames=['/DGetFullPathNameA=fixture_GetFullPathNameA','/DCharUpperA=fixture_CharUpperA']
    objects={}
    def compile_all(tag):
        for name,source,extra in [('game',SOURCE,api_renames),('canonical-search',CANONICAL,['/Dformatter_search_character_005a2780=fixture_canonical_search_005a2780']),('fixture',fixture,[])]:
            obj=out/(name+'.obj');objects[name]=obj
            record=run(tag+'-'+name,[*common,*extra,'/sourceDependencies',out/'dependencies',f'/Fo{obj}',source])
            assert record['exit_code']==0,(out/(tag+'-'+name+'.log')).read_text(errors='replace')
    compile_all('dependency-probe')
    dependencies=provenance.dependency_paths(out)
    for path in dependencies:pin(path)
    compile_all('compile');assert provenance.dependency_paths(out)==dependencies
    for path in objects.values():pin(path)
    symbols=coff.coff_symbols(objects['game'])
    assert set(symbols['defined'])=={'?resource_drive_letter_005916a0@porsche@@YAEPBD@Z'},symbols
    expected={'?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z','__imp__fixture_GetFullPathNameA@16','__imp__fixture_CharUpperA@4'}
    assert set(symbols['undefined'])==expected,symbols
    # Separately compile the unrenamed production source and inspect real imports.
    production=out/'production.obj'
    record=run('production-coff',[*common,f'/Fo{production}',SOURCE]);assert record['exit_code']==0
    production_symbols=coff.coff_symbols(production)
    assert set(production_symbols['defined'])==set(symbols['defined'])
    assert set(production_symbols['undefined'])=={'?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z','__imp__GetFullPathNameA@16','__imp__CharUpperA@4'},production_symbols
    exe=out/'native_fixture.exe'
    def link_fixture(name,game_obj,target):
        result=run(name,[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/INCREMENTAL:NO','/OPT:REF','/NODEFAULTLIB',f'/OUT:{target}',game_obj,objects['canonical-search'],objects['fixture'],*libs])
        assert result['exit_code']==0,(out/(name+'.log')).read_text(errors='replace')
    link_fixture('link',objects['game'],exe);pin(exe)
    execution=run('native',[exe]);assert execution['exit_code']==0,(out/'native.log').read_text()
    assert 'cases=6912 failures=0' in (out/'native.log').read_text()
    negatives=[]
    if args.negative_controls:
        text=SOURCE.read_text()
        mutations=[('unsigned-length','static_cast<std::int32_t>(length) > 1','length > 1'),('before-upper-byte','return static_cast<std::uint8_t>(full_path[0]);','return static_cast<std::uint8_t>(full_path[0] - 17);'),('api-error-shortcut','CharUpperA(full_path);','if (length == 0) return 0;\n    CharUpperA(full_path);')]
        for name,old,new in mutations:
            assert text.count(old)==1
            mutated=out/(name+'.cpp');mutated.write_text(text.replace(old,new),encoding='utf8',newline='\n');pin(mutated)
            obj=out/(name+'.obj');record=run(name+'-compile',[*common,*api_renames,f'/Fo{obj}',mutated]);assert record['exit_code']==0
            target=out/(name+'.exe');link_fixture(name+'-link',obj,target)
            record=run(name+'-native',[target]);assert record['exit_code']==10
            negatives.append(dict(name=name,exit_code=record['exit_code'],detected=True))
    guard()
    outputs={relative(p):sha(p) for p in out.rglob('*') if p.is_file()}
    report=dict(schema=1,run=331,attempt=args.attempt,status='PASS',native_cases_passed=6912,original_sha256=SHA,original_selected_bytes=111,original_vas=['005916a0'],original_body_sha256=hashlib.sha256(body).hexdigest(),source_sha256={relative(p):sha(p) for p in (SOURCE,HEADER,CANONICAL,template)},inputs_sha256={relative(p):h for p,h in pins.items()},outputs_sha256=outputs,receipts=receipts,coff_symbols=symbols,production_coff_symbols=production_symbols,native=execution,negative_controls=negatives,actual_dependencies=sorted(map(relative,dependencies)),guards_before_after=True,limits=['AL only; upper EAX is deliberately not compared.','Win32 imports are controlled mutable-buffer API hooks; actual host OS path behavior is not accepted.','Search is the unchanged canonical TU through recording wrapper; null-only source fallback uses controlled search return because the canonical null search faults.','Unused locale dependencies are fixture-only fail-fast symbols, never production providers.'])
    receipt=out/'receipt.json';write(receipt,report)
    summary=dict(schema=1,run=331,status='PASS',original_sha256=SHA,original_vas=report['original_vas'],original_selected_bytes=111,original_body_sha256=report['original_body_sha256'],native_cases_passed=6912,native_attemptdir=relative(out),native_receipt_sha256=sha(receipt),source_sha256=report['source_sha256'],negative_controls=negatives,coff_symbols=production_symbols)
    write(RUN/'summary.json',summary)
    print(f'Run331 PASS:111B,6912 native AL/API cases;negative controls={len(negatives)};receipt={relative(receipt)}')

if __name__=='__main__':main()

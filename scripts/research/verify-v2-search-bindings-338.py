"""O2 ABI transport for existing canonical search bodies; no new original recovery."""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/338-search-abi-bindings'
BASE=ROOT/'local/experiments/v2-search-bindings-338'
SOURCE=RUN/'search_bindings_338.cpp';HEADER=RUN/'search_bindings_338.hpp'
def sha(p,normalized=False):
    b=Path(p).read_bytes();return hashlib.sha256(b.replace(b'\r\n',b'\n') if normalized else b).hexdigest()
def relative(p):
    p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=int,required=True);parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
    out=BASE/f'{args.attempt:03d}';assert not out.exists(),f'Immutable attempt:{out}'
    out.mkdir(parents=True);(out/'dependencies').mkdir();pins={}
    def pin(p):
        p=Path(p).resolve();v=sha(p);assert p not in pins or pins[p]==v,f'input drift:{p}';pins[p]=v;return p
    def guard():
        for p,v in pins.items():assert sha(p)==v,f'input drift:{p}'
    pin(Path(__file__));pin(SOURCE);pin(HEADER)
    pe=pin(ROOT/'local/game/Porsche.exe');original_sha='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39';assert sha(pe)==original_sha
    coff=module('coff338',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    provenance=module('provenance338',pin(ROOT/'scripts/research/audio_recovery_provenance.py'))
    utility=module('utility338',pin(ROOT/'scripts/research/verify-v2-pr9-resource-313.py'));utility.RUN=RUN
    proofpath=pin(ROOT/'iterations/v2/001-original-recovery/runs/172-formatter-search/production-verification.json');proof=read(proofpath)
    assert proof['native_cpp_equal_original_x86'] and proof['cases']==9374 and proof['sha256']==original_sha
    for name,value in proof['source_sha256'].items():assert sha(pin(ROOT/name),True)==value,f'original proof drift:{name}'
    for body in proof['original_body_pins']:
        for region in body['ranges']:
            assert hashlib.sha256(utility.pe_at(pe.read_bytes(),int(region['start_va'],16),region['bytes'])).hexdigest()==region['sha256']
    intake=pin(ROOT/'iterations/v2/001-original-recovery/runs/330-canonical-search-intake/summary.json');triage=pin(ROOT/'iterations/v2/001-original-recovery/runs/337-game-frontier-triage/summary.json')
    assert read(triage)['candidates'][0]['object_undefined_without_current_provider']==[]
    fixture=pin(RUN/'native_fixture_338.cpp')
    vc=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207';sdk=Path('C:/Program Files (x86)/Windows Kits/10');kit='10.0.26100.0'
    cl=vc/'bin/Hostx64/x86/cl.exe';link=cl.parent/'link.exe'
    includes=[RUN,ROOT/'iterations/v2/001-original-recovery/source/include',vc/'include',*[sdk/'Include'/kit/x for x in ('ucrt','shared','um')]]
    libs=[vc/'lib/x86/libcmt.lib',vc/'lib/x86/libvcruntime.lib',vc/'lib/x86/oldnames.lib',sdk/'Lib'/kit/'ucrt/x86/libucrt.lib',sdk/'Lib'/kit/'um/x86/kernel32.lib']
    for p in [cl,link,cl.parent/'c1xx.dll',cl.parent/'c2.dll',*libs]:pin(p)
    for p in (SOURCE,fixture):
        for q in utility.local_includes(p):pin(q)
    receipts={}
    def run(name,command):
        guard();start=time.perf_counter();proc=subprocess.run(list(map(str,command)),cwd=out,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
        log=out/(name+'.log');log.write_bytes(proc.stdout+proc.stderr)
        r=dict(command=list(map(str,command)),exit_code=proc.returncode,seconds=round(time.perf_counter()-start,6),log=relative(log),log_sha256=sha(log));write(out/(name+'.execution.json'),r);receipts[name]=r;guard();return r
    common=[cl,'/nologo','/c','/TP','/std:c++17','/Oy-','/GS-','/GR-','/EHsc','/W4','/utf-8',*[x for inc in includes for x in ('/I',inc)]]
    objects={}
    def compile_all(tag):
        for name,p,opt in [('game',SOURCE,'/O2'),('fixture',fixture,'/Od')]:
            obj=out/(name+'.obj');objects[name]=obj;r=run(tag+'-'+name,[*common,opt,'/sourceDependencies',out/'dependencies',f'/Fo{obj}',p]);assert r['exit_code']==0,(out/(tag+'-'+name+'.log')).read_text(errors='replace')
    compile_all('dependency-probe');deps=provenance.dependency_paths(out)
    for p in deps:pin(p)
    compile_all('compile');assert provenance.dependency_paths(out)==deps
    for p in objects.values():pin(p)
    symbols=coff.coff_symbols(objects['game'])
    expected_defs={'?compare_005ae3c0@porsche@@YAHPBD0@Z','?render_settings_read_config_005a1e10@porsche@@YAHPADPBD@Z'}
    expected_undef={'?formatter_search_compare_005ae3c0@porsche@@YAHPBD0@Z','?formatter_search_substring_005a1e10@porsche@@YAPBDPBD0@Z'}
    assert set(symbols['defined'])==expected_defs and set(symbols['undefined'])==expected_undef,symbols
    def link_fixture(name,obj,target):
        r=run(name,[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/INCREMENTAL:NO','/NODEFAULTLIB',f'/OUT:{target}',obj,objects['fixture'],*libs]);assert r['exit_code']==0,(out/(name+'.log')).read_text(errors='replace')
    exe=out/'native_fixture.exe';link_fixture('link',objects['game'],exe);pin(exe)
    execution=run('native',[exe]);assert execution['exit_code']==0,(out/'native.log').read_text()
    assert 'cases=816 failures=0' in (out/'native.log').read_text()
    negatives=[]
    if args.negative_controls:
        text=SOURCE.read_text();mutations=[('substring-bool','std::memcpy(&result, &found, sizeof(result));','result = found ? 1 : 0;'),('compare-wrong-callee','return formatter_search_compare_005ae3c0(left, right);','return static_cast<std::int32_t>(reinterpret_cast<std::uintptr_t>(formatter_search_substring_005a1e10(left, right)));'),('compare-swapped-arguments','return formatter_search_compare_005ae3c0(left, right);','return formatter_search_compare_005ae3c0(right, left);')]
        for name,old,new in mutations:
            assert text.count(old)==1;p=out/(name+'.cpp');p.write_text(text.replace(old,new),encoding='utf8',newline='\n');pin(p);obj=out/(name+'.obj')
            r=run(name+'-compile',[*common,'/O2',f'/Fo{obj}',p]);assert r['exit_code']==0
            target=out/(name+'.exe');link_fixture(name+'-link',obj,target);r=run(name+'-native',[target]);assert r['exit_code']==10
            negatives.append(dict(name=name,detected=True,exit_code=10))
    guard();outputs={relative(p):sha(p) for p in out.rglob('*') if p.is_file()}
    report=dict(schema=1,run=338,status='PASS',kind='ABI bindings to existing172 canonical functions',new_original_functions=0,native_cases_passed=816,optimization='bridge/O2;fixture/Od for inspectable inline-assembly ABI capture',source_sha256={relative(p):sha(p) for p in (SOURCE,HEADER,fixture)},inputs_sha256={relative(p):v for p,v in pins.items()},outputs_sha256=outputs,receipts=receipts,coff_symbols=symbols,original_body_proof=dict(path=relative(proofpath),sha256=sha(proofpath),cases=9374,current_source_pins=len(proof['source_sha256']),rerun=False),canonical_game_closure=dict(run=332,undefined_contracts=6,already_defined=True),native=execution,negative_controls=negatives,actual_dependencies=sorted(map(relative,deps)),guards_before_after=True,limits=['Controlled canonical stubs prove transport only; original algorithms retain172 ownership/proof.','Only compare and substring ABI names are bound; no providers/state/behavior are added.','Original172 locale/EOF and whole-game validation holds remain.'])
    receipt=out/'receipt.json';write(receipt,report)
    write(RUN/'summary.json',dict(schema=1,run=338,status='PASS',kind=report['kind'],new_original_functions=0,native_cases_passed=816,native_attemptdir=relative(out),native_receipt_sha256=sha(receipt),source_sha256=report['source_sha256'],coff_symbols=symbols,original_body_proof=report['original_body_proof'],negative_controls=negatives,predicted_closed_names=sorted(expected_defs),predicted_closed_references=2,new_dependencies=[]))
    print(f'Run338 PASS:2 existing-body ABI bindings,816 O2 native transport cases,0 neworiginal functions,negativecontrols={len(negatives)}')
if __name__=='__main__':main()

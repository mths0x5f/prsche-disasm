"""Run330: inspect existing canonical search proof and actual game COFF closure.

Capture compiles only the canonical TU to an isolated object. It does not edit
the game graph, link the game, or rerun accepted native comparisons.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/330-canonical-search-intake'
OUT=ROOT/'local/experiments/v2-search-intake-330'
SOURCE=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_search.cpp'
BUILD=ROOT/'local/builds/v2/resource-device-game-integration-328'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def sha(p,normalized=False):
    b=Path(p).read_bytes()
    if normalized:b=b.replace(b'\r\n',b'\n')
    return hashlib.sha256(b).hexdigest()
def rel(p):
    p=Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def check():
    summary=read(RUN/'summary.json')
    for name,value in summary['inputs_sha256'].items():assert sha(ROOT/name)==value,f'input drift: {name}'
    for name,value in summary['outputs_sha256'].items():assert sha(ROOT/name)==value,f'output drift: {name}'
    print('Run330 existing proof/source/game-COFF input and output pins PASS; no subprocess rerun')

def capture():
    assert not (RUN/'summary.json').exists(),'Immutable Run330 summary exists; use --check'
    OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
    pins={}
    def pin(p):
        p=Path(p).resolve();h=sha(p)
        assert p not in pins or pins[p]==h,f'input drift: {p}'
        pins[p]=h;return p
    def guard():
        for p,h in pins.items():assert sha(p)==h,f'input drift: {p}'
    pin(Path(__file__));pin(SOURCE)
    pe=pin(ROOT/'local/game/Porsche.exe');assert sha(pe)==SHA
    parser_path=pin(ROOT/'scripts/research/build-v2-compile-corpus.py')
    coff=module('coff330',parser_path)
    utility=module('includes330',pin(ROOT/'scripts/research/verify-v2-pr9-resource-313.py'))
    oldproofs=[]
    for name in ('verification.json','production-verification.json'):
        path=pin(ROOT/'iterations/v2/001-original-recovery/runs/172-formatter-search'/name)
        proof=read(path)
        assert proof['sha256']==SHA and proof['native_cpp_equal_original_x86']
        for f,h in proof['source_sha256'].items():assert sha(pin(ROOT/f),True)==h,f'Run172 source drift: {f}'
        for body in proof['original_body_pins']:
            for region in body['ranges']:
                raw=utility.pe_at(pe.read_bytes(),int(region['start_va'],16),region['bytes'])
                assert hashlib.sha256(raw).hexdigest()==region['sha256']
        oldproofs.append(dict(path=rel(path),sha256=sha(path),cases=proof['cases'],case_counts=proof['case_counts'],source_pins_match=len(proof['source_sha256']),private_observer=proof['private_read_observer_compiled'],probe_sha256=proof['probe_sha256'],body_pins=proof['original_body_pins'],shared_original_entries=proof['shared_original_entries_reached']))
    buildpath=pin(ROOT/'iterations/v2/001-original-recovery/runs/328-resource-device-game-integration/build-001.json')
    build=read(buildpath)
    assert rel(SOURCE) not in build['compiled_source_roots']
    receiptpath=pin(ROOT/build['receipt']);assert sha(receiptpath)==build['receipt_sha256']
    buildreceipt=read(receiptpath)
    buildlog=pin(ROOT/buildreceipt['log']);assert sha(buildlog)==buildreceipt['log_sha256']
    object_views={}
    for path in sorted(BUILD.rglob('*.obj')):
        pin(path);object_views[rel(path)]=coff.coff_symbols(path)
    definitions={}
    for path,view in object_views.items():
        for name in view['defined']:definitions.setdefault(name,[]).append(path)
    vc=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    cl=pin(vc/'bin/Hostx64/x86/cl.exe')
    pin(cl.parent/'c1xx.dll');pin(cl.parent/'c2.dll')
    sdk=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0')
    includes=[ROOT/'iterations/v2/001-original-recovery/source/include',vc/'include',sdk/'ucrt',sdk/'shared',sdk/'um']
    for path in utility.local_includes(SOURCE):pin(path)
    obj=OUT/'formatter_search.obj';deps=OUT/'formatter_search.dependencies.json'
    command=[cl,'/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/EHsc','/W4','/utf-8','/sourceDependencies',deps,*[p for inc in includes for p in ('/I',inc)],f'/Fo{obj}',SOURCE]
    guard();started=time.perf_counter()
    result=subprocess.run(list(map(str,command)),cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
    log=OUT/'compile.log';log.write_bytes(result.stdout+result.stderr)
    execution=dict(command=list(map(str,command)),exit_code=result.returncode,seconds=round(time.perf_counter()-started,6),log=rel(log),log_sha256=sha(log))
    write(OUT/'compile.execution.json',execution)
    assert result.returncode==0,log.read_text(errors='replace')
    guard()
    dependency_data=read(deps)['Data']
    for path in dependency_data['Includes']:pin(path)
    view=coff.coff_symbols(obj)
    expected={'?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z','?formatter_search_substring_005a1e10@porsche@@YAPBDPBD0@Z','?formatter_search_compare_005ae3c0@porsche@@YAHPBD0@Z'}
    assert set(view['defined'])==expected,view
    assert not any('trace' in x for x in view['undefined']),view
    closure={name:definitions.get(name,[]) for name in view['undefined']}
    assert all(closure.values()),f'Missing actual game closure: {closure}'
    assert not any(name in definitions for name in expected),'Existing native owner collision'
    exact_duplicates={}
    for va in ('005a2780','005a1e10','005ae3c0'):
        exact_duplicates[va]={name:paths for name,paths in definitions.items() if va in name.lower()}
    frontier={r['symbol']:r for r in build['frontier']}
    closed=sorted(expected & frontier.keys())
    assert closed==['?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z']
    source_by_object={}
    # Every provider path is retained verbatim: these are actual current game
    # object definitions, not a source-level assumption about a library.
    for name,paths in closure.items():
        for p in paths:source_by_object[p]=object_views[p]
    registry=pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')
    registry_owners=[x for x in read(registry)['functions'] if x.get('module')=='Porsche.exe' and x['entry_va'] in ('005a2780','005a1e10','005ae3c0')]
    old327=pin(ROOT/'iterations/v2/001-original-recovery/runs/327-resource-open-callback-evidence/summary.json')
    native327=pin(ROOT/read(old327)['native_attemptdir']/'receipt.json')
    assert sha(native327)==read(old327)['native_receipt_sha256']
    for f,h in read(native327)['source_sha256'].items():assert sha(ROOT/f)==h
    guard()
    outputs={rel(p):sha(p) for p in (obj,deps,log,OUT/'compile.execution.json')}
    summary=dict(schema=1,run=330,status='READY existing canonical whole TU; root integration pending',original_sha256=SHA,canonical_source=rel(SOURCE),new_recovered_vas=0,new_data_providers=0,game_graph_modified=False,production_symbol_definitions=view['defined'],actual_object=rel(obj),coff_symbols=view,actual_game_provider_closure=closure,provider_objects=source_by_object,existing_same_va_native_symbols=exact_duplicates,registry_owners=registry_owners,reused_172_proof=oldproofs,reused_327_native_receipt=rel(native327),reused_327_native_receipt_sha256=sha(native327),baseline=dict(run=328,source_count=build['source_count'],unresolved_names=build['unresolved_names'],unresolved_references=build['unresolved_references']),predicted_frontier=dict(closed_names=closed,new_names=[],closed_references=sum(len(frontier[n]['references']) for n in closed),source_count_delta=1),recommended_action='Add exact existing formatter_search.cpp once to the game bridge/static target; no source/header/alias/data-provider changes.',alternatives=dict(whole_TU='READY: all six undefined contracts already defined by actual328objects',archive_or_Gy_selection='Unnecessary; direct /Gy /OPT:REF did not eliminate unrelated dependencies in327 and no selective-byte extraction is justified.',new_callee_closure='Not required: all providers already compiled in328; preserve their existing holds and identities.'),inputs_sha256={rel(p):h for p,h in pins.items()},outputs_sha256=outputs,compile=execution,limits=['This is link-readiness evidence and existing-proof reuse, not a new native/game/visual run.','Existing Run236 ctype/EOF and locale-domain holds remain unchanged; no new locale storage or forced-zero provider is accepted.','Run172 registry entries are absent; canonical source/proof ownership still applies.','Root332 must confirm actual frontier delta/one-TU ownership in the fresh full game build.'])
    write(RUN/'summary.json',summary)
    write(RUN/'validation.json',dict(status='PASS',run=330,old_proof_pins_current=True,actual_coff_closure=True,game_graph_modified=False,native_rerun=False,closed_names_predicted=1,new_names_predicted=0))
    print('Run330 READY: exact canonical TU defines3 functions; all6 undefined names have current328COFF providers; expected1 name/1 ref closes,0 new; no native rerun')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    if parser.parse_args().check:check()
    else:capture()

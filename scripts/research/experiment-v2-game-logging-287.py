"""Prepare287 without execution; --execute requires coordinator approval."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'iterations/v2/001-original-recovery'
RUN=BASE/'runs/287-game-logging-bridge'
OUT=ROOT/'local/experiments/v2-game-logging-287'
OLD=ROOT/'local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatter_stdio.obj'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def definitions(p):
    data=Path(p).read_bytes();assert data[:8]==b'!<arch>\n'
    size=int(data[56:66]);member=data[68:68+size];count=int.from_bytes(member[:4],'big')
    return set(member[4+4*count:].rstrip(b'\0').decode().split('\0'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'objects').mkdir(exist_ok=True);(OUT/'dependencies').mkdir(exist_ok=True)
    coff=module('coff287','scripts/research/build-v2-compile-corpus.py')
    oracle=module('oracle287','scripts/research/audit-v2-nested-calls-229.py')
    pe=module('pe287','scripts/research/audit-v2-x86-call-chain-258.py')
    abi=module('abi287','scripts/research/experiment-v2-thiscall-186.py')
    dependencies=module('deps287','scripts/research/v2_source_dependencies.py')
    pins={}
    def pin(p,h=None):
        p=Path(p);actual=digest(p);assert h is None or h==actual,('pin',str(p));pins[relative(p)]=actual;return p
    report=load(pin(BASE/'runs/175-formatter-stdio/verification.json'))
    for p,h in report['source_sha256'].items():pin(ROOT/p,h)
    pin(OLD,'837e17652f2975e3a8ec3c2f2de8348c02dc53a7724140db7f5fd50790cadb07')
    symbols=coff.coff_symbols(OLD);assert len(symbols['defined'])==9 and len(symbols['undefined'])==10
    proposal=load(pin(ROOT/'local/experiments/v2-game-entry-frontier-283/entry-link-proposal.json'))
    libraries=[Path(p) for p in proposal['args'] if p.endswith('.lib') and Path(p).is_file() and 'local' in p]
    assert len(libraries)==5
    indexed={relative(pin(p)):definitions(p) for p in libraries}
    overlaps={p:sorted(set(symbols['defined'])&names)for p,names in indexed.items()}
    providers={s:[p for p,names in indexed.items()if s in names]for s in symbols['undefined']}
    assert not any(overlaps.values()) and all(providers.values())
    source=BASE/'source/recovered/Porsche.exe/formatter_stdio.cpp';pin(source)
    registry=pin(BASE/'source/recovered/functions.json')
    owned=[]
    for r in load(registry)['functions']:
        if r.get('module')=='Porsche.exe' and r.get('entry_va','').lower() in report['function_vas']:owned.append(r)
    assert not owned,('registry owners',owned)
    roots=[RUN/'application-log-bridge.cpp',RUN/'fixture.cpp']
    closure=dependencies.source_hashes(roots)
    for p in closure:pin(ROOT/p) # actual bytes, not normalized helper digests
    for p in [__file__,ROOT/'scripts/research/build-v2-compile-corpus.py',ROOT/'scripts/research/audit-v2-nested-calls-229.py',ROOT/'scripts/research/audit-v2-x86-call-chain-258.py',ROOT/'scripts/research/experiment-v2-thiscall-186.py',abi.COMPILER,abi.COMPILER.with_name('link.exe')]:pin(p)
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    original=pe.original_bytes(image,'005a177b',65)
    assert hashlib.sha256(original).hexdigest()==report['functions']['005a177b']['body_sha256']
    edge=pe.original_bytes(image,'004b6b0e',13)
    assert edge.hex()=='68846e5d00e863ac0e0083c410'
    literal=pe.original_bytes(image,'005d6e84',24);assert literal==b'Initializing rendering\n\0'
    tools=abi.COMPILER.parents[3];sdk=Path('C:/Program Files (x86)/Windows Kits/10')
    includes=[BASE/'source/include',tools/'include',sdk/'Include/10.0.26100.0/ucrt',sdk/'Include/10.0.26100.0/shared',sdk/'Include/10.0.26100.0/um']
    command=[str(abi.COMPILER),'/nologo','/c','/std:c++17','/O2','/Oi','/Gy','/MD','/GS-','/GR-','/W4','/utf-8','/MP6','/sourceDependencies',str(OUT/'dependencies'),'/Fo'+str(OUT/'objects')+os.sep,*['/I'+str(p)for p in includes],*map(str,roots)]
    obj=[OUT/'objects/application-log-bridge.obj',OUT/'objects/fixture.obj']
    link=[str(abi.COMPILER.with_name('link.exe')),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/INCREMENTAL:NO','/OUT:'+str(OUT/'fixture.exe'),'/LIBPATH:'+str(tools/'lib/x86'),'/LIBPATH:'+str(sdk/'Lib/10.0.26100.0/ucrt/x86'),'/LIBPATH:'+str(sdk/'Lib/10.0.26100.0/um/x86'),*map(str,obj),str(OLD),'kernel32.lib']
    proof=dict(schema=1,kind='game-logging-bridge-preflight',original_sha256=SHA,game_sources=[relative(roots[0])],cached_game_objects=[relative(OLD)],fixture_sources=[relative(roots[1])],expected_objects=list(map(relative,obj)),canonical_source=relative(source),canonical_coff_symbols=symbols,library_definition_overlaps=overlaps,existing_library_providers=providers,source175_pins_matched=len(report['source_sha256']),original_body_hex=original.hex(),original_call_edge_hex=edge.hex(),original_literal_hex=literal.hex(),planned_cases=224,planned_case_groups=dict(direct_printf=192,format_only_bridge=32),compile_command=command,link_command=link,include_directories=list(map(str,includes)),input_sha256=pins,limits=['Real lock table prefix26 vs required48 remains runtime HOLD; controlled lock provider tests only edge29.','Canonical application_main literal currently lacks the original newline; bridge forwards bytes unchanged.','No whole output-provider composition, game execution or original CRT initialization acceptance.'])
    if args.execute:
        assert load(RUN/'proof-before-compile.json')==proof,'preflight changed; obtain approval for changed inputs'
    else:
        write(RUN/'proof-before-compile.json',proof);print(json.dumps(dict(preflight='ready',source175_pins=len(report['source_sha256']),overlaps=0,providers=len(providers),cases=224)));return
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        receipt=OUT/(name+'.execution.json');log=OUT/(name+'.log');assert not receipt.exists()and not log.exists(),'unique execution names required'
        start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);elapsed=time.perf_counter()-start
        write(receipt,dict(command=command,cwd=str(OUT),exit_code=p.returncode,elapsed_seconds=elapsed,include_directories=list(map(str,includes))))
        log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'));return p,log,elapsed
    p,clog,seconds=run(command,'compile-001');assert p.returncode==0,clog.read_bytes()
    actual_includes=set()
    dependency_reports=list((OUT/'dependencies').glob('*.json'));assert len(dependency_reports)==2
    for report_path in dependency_reports:
        for name in load(report_path)['Data']['Includes']:actual_includes.add(name)
        pin(report_path)
    for name in sorted(actual_includes):pin(Path(name))
    native,relocations=oracle.coff_function(obj[1],'?reference_printf287@porsche@@YAHPBDZZ')
    expected=[(3,6,'?formatter_iob_entries_005e54e8@porsche@@3PAUFormatterOriginalDescriptor32@1@A'),(12,20,'?formatter_stdio_lock_index_005a3719@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z'),(18,20,'?formatter_stdio_temporary_buffer_005a533e@porsche@@YAHPAUFormatterOriginalDescriptor32@1@@Z'),(35,20,'?formatter_core_005a4371@porsche@@YAHPAUFormatterOriginalDescriptor32@1@PBDPBI@Z'),(44,20,'?formatter_stdio_finish_buffer_005a53cb@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z'),(52,20,'?formatter_stdio_unlock_index_005a376b@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z')]
    assert sorted((r['offset'],r['type'],r['symbol'])for r in relocations)==sorted(expected),relocations
    normalized=bytearray(original)
    for offset,kind,symbol in expected:normalized[offset:offset+4]=(32 if kind==6 else 0).to_bytes(4,'little')
    assert native==normalized,(native.hex(),normalized.hex())
    p,llog,_=run(link,'link-001');assert p.returncode==0,llog.read_bytes()
    p,nlog,nseconds=run([str(OUT/'fixture.exe')],'native-001');assert p.returncode==0,nlog.read_bytes()
    result=json.loads(nlog.read_bytes());assert result==dict(cases=224,failures=0,direct_printf=192,format_only_bridge=32)
    for name,h in pins.items():assert digest(ROOT/name)==h,('mutation',name)
    for f in [*obj,OUT/'fixture.exe',*OUT.glob('*.execution.json'),*OUT.glob('*.log'),RUN/'proof-before-compile.json']:pin(f)
    summary=dict(schema=1,kind='game-logging-bridge',original_sha256=SHA,new_original_bodies=0,cached_original_bodies=8,game_bridge_source=relative(roots[0]),game_bridge_object=relative(obj[0]),game_bridge_symbols=coff.coff_symbols(obj[0]),cached_canonical_object=relative(OLD),compiler_exit_code=0,compile_seconds=seconds,compiled_tus=2,compiler_warning_lines=[s for s in clog.read_text().splitlines()if re.search(r'warning [CD]\d+',s)],native_fixture_exit_code=0,native_seconds=nseconds,case_groups=result,original_oracle_relocations=relocations,include_directories=list(map(str,includes)),compiler_command=command,compiler_execution_receipt=relative(OUT/'compile-001.execution.json'),native_game_execution_commands=0,input_sha256=pins,limits=proof['limits'])
    write(RUN/'summary.json',summary);write(RUN/'validation.json',dict(schema=1,status='PASS',summary_sha256=digest(RUN/'summary.json'),input_pins=len(pins),oracle_exact_original_bytes=65,original_calls=5,absolute_relocations=1,native_cases=224,mutation_guard=True));print(json.dumps(dict(status='PASS',cases=224,pins=len(pins))))
if __name__=='__main__':main()

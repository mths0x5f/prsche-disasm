"""Reuse two existing Win32 adapters; platform code never counts as game functions."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/268-native-platform-providers'
OUT=ROOT/'local/experiments/v2-native-platform-providers-268'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE=ROOT/'iterations/v2/001-original-recovery/source/platform/win32_core.cpp'
NAMES=('platform_enter_critical_section','platform_leave_critical_section')
CONTRACTS=[dict(symbol='?'+name+'@porsche@@YGXPAX@Z',module='KERNEL32.dll',sdk_import='__imp__'+sdk+'@4',original_iat_va=iat)
           for name,sdk,iat in zip(NAMES,('EnterCriticalSection','LeaveCriticalSection'),('005b2078','005b206c'))]
FIXTURE='''#include "porsche/heap_locks.hpp"
#include <windows.h>
static_assert(sizeof(void*)==4 && sizeof(CRITICAL_SECTION)==24);
extern "C" void __cdecl entry(){
 CRITICAL_SECTION lock;InitializeCriticalSection(&lock);unsigned failures=0;
 for(unsigned i=0;i<64;++i){
  porsche::platform_enter_critical_section(&lock);
  if(lock.RecursionCount!=1)++failures;
  porsche::platform_enter_critical_section(&lock);
  if(lock.RecursionCount!=2)++failures;
  porsche::platform_leave_critical_section(&lock);
  if(lock.RecursionCount!=1)++failures;
  porsche::platform_leave_critical_section(&lock);
  if(lock.RecursionCount!=0)++failures;
 }
 DeleteCriticalSection(&lock);ExitProcess(failures?1u:0u);
}
'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode())
def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main(finalize=False):
 assert not (RUN/'summary.json').exists(),'completed268 immutable'
 assert finalize or not OUT.exists() or not any(OUT.iterdir()),'fresh268 output required'
 OUT.mkdir(parents=True,exist_ok=True);RUN.mkdir(parents=True,exist_ok=True)
 pins={}
 def pin(p,expected=None):
  p=Path(p).resolve();h=sha(p);assert expected is None or h==expected,('pin',p)
  assert p not in pins or pins[p]==h;pins[p]=h;return p
 def guard():
  for p,h in pins.items():assert sha(p)==h,('drift',p)
 def materialize(p,b):
  if finalize:assert p.read_bytes()==b,('source drift',p)
  else:p.write_bytes(b)
  return pin(p)
 def run(command,name):
  receipt=OUT/(name+'.execution.json');log=OUT/(name+'.log');command=list(map(str,command))
  if finalize:
   r=json.loads(pin(receipt).read_bytes());pin(log)
   assert r['command']==command and r['exit_code']==0;return r
  assert not receipt.exists() and not log.exists(),'unique receipts required'
  start=time.perf_counter()
  result=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':'','LINK':'','_LINK_':''},capture_output=True,timeout=120)
  r=dict(command=command,cwd=str(OUT),exit_code=result.returncode,elapsed_seconds=time.perf_counter()-start)
  write(receipt,r);log.write_bytes((result.stdout+result.stderr).replace(b'\r\n',b'\n'))
  pin(receipt);pin(log);assert result.returncode==0,(name,log.read_bytes());return r
 abi=mod('abi268','scripts/research/experiment-v2-thiscall-186.py')
 slices=mod('slices268','scripts/research/experiment-v2-heap-release-263.py')
 coff=mod('coff268','scripts/research/build-v2-compile-corpus.py')
 contract=mod('contract268','scripts/research/native-platform-contract-268.py')
 for p in [__file__,abi.__file__,slices.__file__,coff.__file__,contract.__file__,SOURCE,abi.COMPILER,
           abi.COMPILER.with_name('c1xx.dll'),abi.COMPILER.with_name('c2.dll'),abi.COMPILER.with_name('link.exe'),
           ROOT/'research/binary-index/static/imports.jsonl',ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/preflight.json']:
  pin(p)
 pin(ROOT/'local/game/Porsche.exe',SHA)
 old=json.loads((ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/preflight.json').read_bytes())
 for c,owner in zip(CONTRACTS,old['lock_wrappers']):
  assert c['original_iat_va']==owner['original_iat_va'] and c['module']+'!'+c['sdk_import'][7:-2]==owner['sdk']
 raw=SOURCE.read_bytes();prefix=raw[:raw.index(b'namespace porsche {')]
 parts=[dict(offset=0,length=len(prefix),sha256=hashlib.sha256(prefix).hexdigest()),dict(literal='namespace porsche {\n')]
 generated=[prefix,b'namespace porsche {\n']
 for name in NAMES:
  start,end,body=slices.definition(raw,name);generated.append(body)
  parts.append(dict(offset=start,length=end-start,sha256=hashlib.sha256(body).hexdigest()))
 generated.append(b'}\n');parts.append(dict(literal='}\n'))
 source=materialize(OUT/'critical-sections.cpp',b''.join(generated))
 fixture=materialize(OUT/'native-fixture.cpp',FIXTURE.encode())
 objects=OUT/'objects';dependencies=OUT/'dependencies'
 objects.mkdir(exist_ok=finalize);dependencies.mkdir(exist_ok=finalize)
 sdk=Path('C:/Program Files (x86)/Windows Kits/10')
 roots=[ROOT/'iterations/v2/001-original-recovery/source/include',abi.COMPILER.parents[3]/'include',*[sdk/'Include/10.0.26100.0'/n for n in ('ucrt','shared','um')]]
 command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GR-','/EHsc','/TP','/W4','/utf-8','/MP6','/Zl','/GS-',
          '/sourceDependencies',dependencies,*[item for r in roots for item in ('/I',r)],'/Fo'+str(objects)+os.sep,source,fixture]
 guard();compiled=run(command,'compile-001')
 assert not re.search(rb'(?:warning|error) [CD]\d+',(OUT/'compile-001.log').read_bytes())
 dep_paths={};headers={}
 for p in (source,fixture):
  dep=pin(dependencies/(p.name+'.json'));d=json.loads(dep.read_bytes())
  assert d['Version']=='1.2' and Path(d['Data']['Source']).resolve()==p
  dep_paths[p]=dep;headers[p]=[pin(Path(n)) for n in d['Data']['Includes']]
 obj=pin(objects/'critical-sections.obj');symbols=coff.coff_symbols(obj)
 row=dict(id='win32-critical-section-providers',compiled=True,compiler_exit_code=0,generated_source=rel(source),generated_source_sha256=sha(source),
          object=rel(obj),object_sha256=sha(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
          dependency_sha256={rel(p):sha(p) for p in headers[source]},forced_headers=[],include_directories=[rel(p) for p in roots],
          compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),
          source_dependencies=rel(dep_paths[source]),source_dependencies_sha256=sha(dep_paths[source]),
          platform_contracts=CONTRACTS,platform_source=rel(SOURCE),platform_source_parts=parts)
 contract.validate('native-platform-provider',row,symbols,obj,ROOT,pins)
 kernel=pin(sdk/'Lib/10.0.26100.0/um/x86/kernel32.lib');exe=OUT/'native-fixture.exe';fixture_obj=pin(objects/'native-fixture.obj')
 linked=run([abi.COMPILER.with_name('link.exe'),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO',
             '/OUT:'+str(exe),obj,fixture_obj,kernel],'link-001')
 pin(exe);native=run([exe],'native-001');guard()
 summary=dict(schema=1,kind='native-platform-provider',original_sha256=SHA,compiler_sha256=sha(abi.COMPILER),compiler_batch_exit_code=0,
              compiler_command=list(map(str,command)),support_objects=[row],input_sha256={rel(p):h for p,h in pins.items()},
              actual_compiler_batches=1,actual_native_commands=1,native_fixture=dict(exit_code=0,recursive_cycles=64,provider_calls=256,
              compile_seconds=compiled['elapsed_seconds'],native_seconds=native['elapsed_seconds']),new_game_functions=0,
              limits=['Existing modern Win32 adapters only; no game algorithms or original function VAs.',
                      'Valid real Win32 critical-section recursion/release only; faults and contention not proved.',
                      'No original heap-table provider or full-game execution.'])
 write(RUN/'summary.json',summary)
 print(json.dumps(dict(platform_objects=1,defined_providers=2,recursive_cycles=64,pins=len(pins),compile_exit=0,native_exit=0)))


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--finalize-existing',action='store_true');main(p.parse_args().finalize_existing)

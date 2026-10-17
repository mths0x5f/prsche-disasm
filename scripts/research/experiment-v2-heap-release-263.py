"""Compile three exact accepted canonical bodies and compare bounded original heap cutpoints."""
import argparse,hashlib,importlib.util,json,os,re,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release'
OUT=ROOT/'local/experiments/v2-canonical-heap-release-263'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=('00531f90','005322b0','005322c0')
NAMES=('free_00531f90','heap_enter_005322b0','heap_leave_005322c0')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def definition(data,name):
 at=data.index(name.encode()+b'(');start=data.rfind(b'\n',0,at)+1
 opening=data.index(b'{',at);depth=1;end=opening+1
 while depth:depth+=(data[end]==123)-(data[end]==125);end+=1
 return start,end+1,data[start:end+1]
def fixture(oracle):
 chunks=[]
 for case in oracle['cases']:
  for free in case['frees']:
   chunks.append((free['before'],free['after'],free['pointer_offset'],case['locked']))
 rows=[]
 for before,after,offset,locked in chunks:
  rows.append('{"'+before+'","'+after+'",'+str(offset)+','+str(int(locked))+'}')
 table=',\n'.join(rows)
 return r'''#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
using U=std::uint32_t;
U fails263=0,enter263=0,leave263=0;
void* last_enter263=nullptr;void* last_leave263=nullptr;
namespace porsche {
OriginalHeap* heaps_006b4f20[16];
void __stdcall platform_enter_critical_section(void* p){++enter263;last_enter263=p;}
void __stdcall platform_leave_critical_section(void* p){++leave263;last_leave263=p;}
}
static U digit263(char c){return c>='0'&&c<='9'?U(c-'0'):c>='a'&&c<='f'?U(c-'a'+10):99u;}
static void decode263(unsigned char* p,const char* hex){for(U i=0;i<512;++i)p[i]=static_cast<unsigned char>((digit263(hex[i*2])<<4)|digit263(hex[i*2+1]));}
struct Case263{const char* before;const char* after;U offset;U locked;};
static const Case263 cases263[]={
'''+table+r'''
};
extern "C" void __cdecl entry(){
 unsigned char* arena=static_cast<unsigned char*>(VirtualAlloc(reinterpret_cast<void*>(0x03000000u),0x20000u,0x3000u,4u));
 if(reinterpret_cast<U>(arena)!=0x03000000u)ExitProcess(101);
 unsigned char expected[512];
 void* lock=reinterpret_cast<void*>(0x02001000u);
 porsche::heap_enter_005322b0(lock);porsche::heap_leave_005322c0(lock);
 if(enter263!=1||leave263!=1||last_enter263!=lock||last_leave263!=lock)++fails263;
 enter263=leave263=0;last_enter263=last_leave263=nullptr;
 if(porsche::free_00531f90(nullptr)!=1||enter263||leave263)++fails263;
 for(U c=0;c<sizeof(cases263)/sizeof(cases263[0]);++c){
  const Case263& q=cases263[c];decode263(arena,q.before);decode263(expected,q.after);
  for(U k=0;k<16;++k)porsche::heaps_006b4f20[k]=nullptr;
  porsche::heaps_006b4f20[0]=reinterpret_cast<porsche::OriginalHeap*>(arena+16);
  U before_enter=enter263,before_leave=leave263;
  U value=porsche::free_00531f90(arena+q.offset);
  if(value!=1||enter263!=before_enter+q.locked||leave263!=before_leave+q.locked)++fails263;
  if(q.locked&&(last_enter263!=lock||last_leave263!=lock))++fails263;
  for(U k=0;k<512;++k)if(arena[k]!=expected[k])++fails263;
 }
 ExitProcess(fails263?1:0);
}
'''
def main(finalize):
 pre=RUN/'preflight.json';oracle_path=OUT/'original-oracles.json'
 assert pre.exists() and oracle_path.exists() and not (RUN/'summary.json').exists()
 if not finalize:assert not (OUT/'compile.execution.json').exists()
 pins={}
 def pin(p,expected=None):
  p=Path(p).resolve();digest=sha(p);assert expected is None or digest==expected,(p,digest,expected);pins[p]=digest;return p
 def guard():
  for p,h in pins.items():assert sha(p)==h,('drift',p)
 def run(command,name):
  command=list(map(str,command));start=time.perf_counter()
  p=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
  log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
  result=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log=rel(log),log_sha256=sha(log))
  write(OUT/(name+'.execution.json'),result);return result
 pin(__file__);pin(pre);oracle=json.loads(pin(oracle_path).read_bytes());assert oracle['original_sha256']==SHA
 abi=module('abi263',pin(ROOT/'scripts/research/experiment-v2-thiscall-186.py'))
 coff=module('coff263',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
 for p in [ROOT/'scripts/research/preflight-v2-heap-release-263.py',ROOT/'scripts/research/oracle-v2-heap-release-263.py',ROOT/'scripts/research/verify-v2-heap.py',ROOT/'local/game/Porsche.exe',ROOT/'iterations/v2/001-original-recovery/runs/078-shared-runtime-integration/heap/verification.json',ROOT/'iterations/v2/001-original-recovery/runs/078-shared-runtime-integration/heap-locks/verification.json',ROOT/'iterations/v2/001-original-recovery/runs/261-canonical-reuse-union/summary.json',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',ROOT/'research/binary-index/static/imports.jsonl']:pin(p)
 assert sha(ROOT/'local/game/Porsche.exe')==SHA
 src_root=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'
 source={VAS[0]:pin(src_root/'heap.cpp'),VAS[1]:pin(src_root/'heap_locks.cpp'),VAS[2]:src_root/'heap_locks.cpp'}
 include_root=ROOT/'iterations/v2/001-original-recovery/source/include'
 for p in include_root.rglob('*.hpp'):pin(p)
 old=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/259-canonical-reuse/summary.json').read_bytes())
 roots=[(ROOT/n if not Path(n).is_absolute() else Path(n)).resolve() for n in old['results'][0]['include_directories']]
 assert len(roots)==5 and all(p.is_dir() for p in roots)
 for name,h in old['input_sha256'].items():
  p=Path(name);p=(ROOT/p if not p.is_absolute() else p)
  if p.suffix.lower() in ('.h','.hpp') and p.exists():pin(p,h if sha(p)==h else None)
 for p in [abi.COMPILER,abi.COMPILER.with_name('c1xx.dll'),abi.COMPILER.with_name('c2.dll'),abi.COMPILER.with_name('link.exe'),Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')]:pin(p)
 text={va:source[va].read_bytes() for va in VAS}
 includes={va:text[va][:text[va].index(b'namespace porsche {')] for va in VAS}
 fragments={};generated={}
 for va,name in zip(VAS,NAMES):
  pieces=[includes[va],b'namespace porsche {\n']
  slices=[]
  helpers=('address','at','links','unlink','insert') if va==VAS[0] else ()
  for symbol in (*helpers,name):
   a,b,part=definition(text[va],symbol);pieces.append(part);pieces.append(b'\n');slices.append(dict(name=symbol,offset=a,length=b-a,sha256=hashlib.sha256(part).hexdigest()))
  pieces.append(b'}\n');output=b''.join(pieces)
  path=OUT/(va+'.cpp')
  if finalize:assert path.read_bytes()==output
  else:path.write_bytes(output)
  generated[va]=pin(path);fragments[va]=dict(source=rel(source[va]),source_sha256=sha(source[va]),slices=slices)
 fixture_src=OUT/'native-fixture.cpp';fixture_text=fixture(oracle).encode('utf8')
 if finalize:assert fixture_src.read_bytes()==fixture_text
 else:fixture_src.write_bytes(fixture_text)
 pin(fixture_src)
 objects=OUT/'objects';deps=OUT/'dependencies'
 if not finalize:objects.mkdir(exist_ok=True);deps.mkdir(exist_ok=True)
 flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/GS-','/sourceDependencies',str(deps)]
 command=[abi.COMPILER,*flags,*[item for root in roots for item in ('/I',root)],'/Fo'+str(objects)+os.sep,*generated.values(),fixture_src]
 if finalize:
  prepared=json.loads(pin(OUT/'prepare.json').read_bytes())
  for name,h in prepared['input_sha256'].items():pin(ROOT/name if not Path(name).is_absolute() else name,h)
  compiled=json.loads(pin(OUT/'compile.execution.json').read_bytes());assert compiled['command']==list(map(str,command))
 else:
  guard();write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={rel(p):h for p,h in pins.items()}));compiled=run(command,'compile')
 assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
 assert not re.search(rb'warning [CD]\d+|error [CD]\d+',(OUT/'compile.log').read_bytes())
 actual_headers={};dep_paths={}
 for path in [*generated.values(),fixture_src]:
  dep=pin(deps/(path.name+'.json'));d=json.loads(dep.read_bytes());assert d['Version']=='1.2' and Path(d['Data']['Source']).resolve()==path
  actual_headers[path]={Path(x).resolve() for x in d['Data']['Includes']};dep_paths[path]=dep
  for h in actual_headers[path]:
   assert any(h.is_relative_to(r) for r in roots)
   pin(h)
 results=[]
 for va,name in zip(VAS,NAMES):
  p=generated[va];obj=pin(objects/(va+'.obj'));symbols=coff.coff_symbols(obj);assert len(symbols['defined'])==1 and name in symbols['defined'][0]
  results.append(dict(va=va,name=name,compiled=True,canonical_reuse=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,generated_source=rel(p),generated_source_sha256=sha(p),dependency_sha256={rel(q):pins[q] for q in actual_headers[p]|{p}},forced_headers=[],include_directories=[rel(r) for r in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile.execution.json'),source_dependencies=rel(dep_paths[p]),source_dependencies_sha256=sha(dep_paths[p]),object=rel(obj),object_sha256=sha(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined']))
 fixture_obj=pin(objects/'native-fixture.obj');exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
 linker=[abi.COMPILER.with_name('link.exe'),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),*[objects/(va+'.obj') for va in VAS],fixture_obj,Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')]
 if finalize and (OUT/'fixture-link.execution.json').exists():linked=json.loads(pin(OUT/'fixture-link.execution.json').read_bytes())
 else:linked=run(linker,'fixture-link')
 assert linked['exit_code']==0,(OUT/'fixture-link.log').read_text(errors='replace')
 if finalize and (OUT/'fixture-native.execution.json').exists():native=json.loads(pin(OUT/'fixture-native.execution.json').read_bytes())
 else:native=run([exe],'fixture-native')
 assert native['exit_code']==0,(OUT/'fixture-native.log').read_text(errors='replace')
 for p in [exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),*deps.glob('*.json')]:pin(p)
 guard();manifest={rel(p):h for p,h in pins.items()}
 summary=dict(schema=1,kind='canonical-body-reuse-batch',module='Porsche.exe',original_sha256=SHA,objects_compiled=3,real_coff_objects=3,results=results,compiled_vas=list(VAS),new_distinct_function_VAs=3,actual_compiler_batches=1,actual_MP6_requested=True,changed_game_TUs=3,handwritten_game_algorithm_TUs=0,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=compiled['seconds'],compiler_sha256=sha(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile.execution.json'),compiler_log=rel(OUT/'compile.log'),compiler_log_sha256=sha(OUT/'compile.log'),source_dependencies_format='MSVC1.2',input_sha256=manifest,input_guards_before=True,input_guards_after=True,original_selected_bytes=302,canonical_fragments=fragments,original_oracles=rel(oracle_path),original_oracles_sha256=sha(oracle_path),native_fixture=dict(executable=rel(exe),executable_sha256=sha(exe),exit_code=0,seconds=native['seconds'],free_cutpoints=4,controlled_providers=['heaps_006b4f20','platform_enter_critical_section','platform_leave_critical_section'],arena_bytes_compared=2048),production_ready=False,production_or_union_changes=False,limits=['No real heap table provider or whole game link','Controlled Win32 lock callbacks; concurrency/fault semantics not proven','Prior 078 original whole-heap differential is supporting evidence, not rerun'])
 write(RUN/'summary.json',summary)
 print(json.dumps(dict(bodies=3,compile_exit=0,native_exit=0,free_cutpoints=4,pins=len(pins))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--finalize-existing',action='store_true');main(p.parse_args().finalize_existing)

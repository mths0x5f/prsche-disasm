"""One proven raw-to-canonical heap-free link directive and native ABI fixture."""
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/266-heap-free-binding'
OUT=ROOT/'local/experiments/v2-heap-free-binding-266'
RAW='?FUN_00531f90@@YAIH@Z';CAN='?free_00531f90@porsche@@YAIPAX@Z'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def fixture(oracle):
 q=oracle['cases'][0]['frees'][0];assert q['return_value']==1 and len(q['before'])==len(q['after'])==1024
 return r'''#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
unsigned int __cdecl FUN_00531f90(int);
using U=std::uint32_t;
U fails266=0,enters266=0,leaves266=0,before266=0,after266=0;
namespace porsche {
OriginalHeap* heaps_006b4f20[16];
void __stdcall platform_enter_critical_section(void*){++enters266;}
void __stdcall platform_leave_critical_section(void*){++leaves266;}
}
static U digit266(char c){return c>='0'&&c<='9'?U(c-'0'):c>='a'&&c<='f'?U(c-'a'+10):99u;}
static void decode266(unsigned char*p,const char*hex){for(U i=0;i<512;++i)p[i]=static_cast<unsigned char>((digit266(hex[i*2])<<4)|digit266(hex[i*2+1]));}
static U invoke266(U target,U value){U result;
 __asm {
  mov before266,esp
  push value
  call target
  add esp,4
  mov result,eax
  mov after266,esp
 }
 if(before266!=after266)++fails266;
 return result;
}
static const char before_state266[]="'''+q['before']+r'''";
static const char after_state266[]="'''+q['after']+r'''";
extern "C" void __cdecl entry(){
 U raw=reinterpret_cast<U>(&FUN_00531f90),canonical=reinterpret_cast<U>(&porsche::free_00531f90);
 if(raw!=canonical)++fails266;
 unsigned char*arena=static_cast<unsigned char*>(VirtualAlloc(reinterpret_cast<void*>(0x03000000u),0x20000u,0x3000u,4u));
 if(reinterpret_cast<U>(arena)!=0x03000000u)ExitProcess(101);
 unsigned char expected[512];decode266(expected,after_state266);
 if(invoke266(raw,0)!=1||invoke266(canonical,0)!=1||enters266||leaves266)++fails266;
 U targets[2]={raw,canonical};
 for(U c=0;c<2;++c){
  decode266(arena,before_state266);
  for(U i=0;i<16;++i)porsche::heaps_006b4f20[i]=nullptr;
  porsche::heaps_006b4f20[0]=reinterpret_cast<porsche::OriginalHeap*>(arena+16);
  if(invoke266(targets[c],reinterpret_cast<U>(arena+'''+str(q['pointer_offset'])+r'''))!=1)++fails266;
  for(U i=0;i<512;++i)if(arena[i]!=expected[i])++fails266;
 }
 if(enters266||leaves266)++fails266;
 ExitProcess(fails266?1:0);
}
'''
def main(finalize,retry):
 assert not (RUN/'summary.json').exists()
 assert not (finalize and retry)
 if retry:
  failed=json.loads((OUT/'compile.execution.json').read_bytes());assert failed['exit_code']!=0
  assert not (OUT/'first-compile.execution.json').exists()
  for name in ('compile.execution.json','compile.log','prepare.json','native-fixture.cpp'):
   shutil.copyfile(OUT/name,OUT/('first-'+name))
 elif not finalize:assert not (OUT/'compile.execution.json').exists()
 pins={}
 def pin(p,expected=None):
  p=Path(p).resolve();h=sha(p);assert expected is None or h==expected,(p,h,expected);pins[p]=h;return p
 def guard():
  for p,h in pins.items():assert sha(p)==h,('input drift',p)
 def run(command,name):
  command=list(map(str,command));start=time.perf_counter()
  p=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
  log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
  receipt=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log=rel(log),log_sha256=sha(log))
  write(OUT/(name+'.execution.json'),receipt);return receipt
 pre=json.loads(pin(RUN/'preflight.json').read_bytes());assert pre['alias_approved'] and pre['consumer_count']==10
 if retry:
  for name in ('first-compile.execution.json','first-compile.log','first-prepare.json','first-native-fixture.cpp'):pin(OUT/name)
 old=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/summary.json').read_bytes())
 pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/validation.json')
 union=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/264-heap-release-union/summary.json').read_bytes())
 pin(ROOT/'iterations/v2/001-original-recovery/runs/264-heap-release-union/validation.json')
 oracle=json.loads(pin(ROOT/old['original_oracles'],old['original_oracles_sha256']).read_bytes())
 abi=module('abi266',pin(ROOT/'scripts/research/experiment-v2-thiscall-186.py'))
 coff=module('coff266',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
 parser=module('parser266',pin(ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py'))
 for p in [__file__,ROOT/'scripts/research/preflight-v2-heap-free-binding-266.py',ROOT/'local/game/Porsche.exe',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',ROOT/pre['canonical_header']]:pin(p)
 assert sha(ROOT/'local/game/Porsche.exe')==old['original_sha256']==union['original_sha256']
 for c in pre['consumers']:
  pin(ROOT/c['object'],c['object_sha256']);pin(ROOT/c['source'],c['source_sha256'])
 game=[]
 for va in ('00531f90','005322b0','005322c0'):
  row=next(x for x in old['results'] if x['va']==va);obj=pin(ROOT/row['object'],row['object_sha256']);assert len(coff.coff_symbols(obj)['defined'])==1;game.append(obj)
 roots=[(Path(x) if Path(x).is_absolute() else ROOT/x).resolve() for x in old['results'][0]['include_directories']]
 assert len(roots)==5 and all(x.is_dir() for x in roots)
 for name,h in old['input_sha256'].items():
  p=Path(name);p=p if p.is_absolute() else ROOT/p
  if p.suffix.lower() in ('.h','.hpp') and p.exists():pin(p,h if sha(p)==h else None)
 compiler=pin(abi.COMPILER,old['compiler_sha256']);linker=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
 directive='/alternatename:'+RAW+'='+CAN
 binding=OUT/'binding.cpp';binding_bytes=('#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4&&sizeof(int)==4,"raw32 ABI");\n#pragma comment(linker,"'+directive+'")\n').encode()
 fixture_src=OUT/'native-fixture.cpp';fixture_bytes=fixture(oracle).encode()
 if finalize:assert binding.read_bytes()==binding_bytes and fixture_src.read_bytes()==fixture_bytes
 else:binding.write_bytes(binding_bytes);fixture_src.write_bytes(fixture_bytes)
 pin(binding);pin(fixture_src)
 objects=OUT/'objects';deps=OUT/'dependencies'
 if not finalize and not retry:objects.mkdir(exist_ok=True);deps.mkdir(exist_ok=True)
 flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/GS-','/sourceDependencies',str(deps)]
 command=[compiler,*flags,*[item for root in roots for item in ('/I',root)],'/Fo'+str(objects)+os.sep,binding,fixture_src]
 if finalize:
  prepared=json.loads(pin(OUT/'prepare.json').read_bytes())
  for name,h in prepared['input_sha256'].items():pin(Path(name) if Path(name).is_absolute() else ROOT/name,h)
  compiled=json.loads(pin(OUT/'compile.execution.json').read_bytes());assert compiled['command']==list(map(str,command))
 else:
  guard();write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={rel(p):h for p,h in pins.items()}));compiled=run(command,'compile')
 assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
 assert not re.search(rb'warning [CD]\d+|error [CD]\d+',(OUT/'compile.log').read_bytes())
 for src in (binding,fixture_src):
  dep=pin(deps/(src.name+'.json'));data=json.loads(dep.read_bytes());assert data['Version']=='1.2' and Path(data['Data']['Source']).resolve()==src
  for h in data['Data']['Includes']:
   h=Path(h).resolve();assert any(h.is_relative_to(root) for root in roots);pin(h)
 support_obj=pin(objects/'binding.obj');symbols=coff.coff_symbols(support_obj);assert not any(symbols.values())
 parsed=parser.coff(support_obj);sec=next(x for x in parsed['sections'] if x['name']=='.drectve')
 actual=parsed['bytes'][sec['raw']:sec['raw']+sec['size']].decode('ascii').strip();assert actual==directive
 fixture_obj=pin(objects/'native-fixture.obj');exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
 link=[linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),*game,support_obj,fixture_obj,kernel]
 if finalize and (OUT/'fixture-link.execution.json').exists():linked=json.loads(pin(OUT/'fixture-link.execution.json').read_bytes())
 else:linked=run(link,'fixture-link')
 assert linked['exit_code']==0,(OUT/'fixture-link.log').read_text(errors='replace')
 if finalize and (OUT/'fixture-native.execution.json').exists():native=json.loads(pin(OUT/'fixture-native.execution.json').read_bytes())
 else:native=run([exe],'fixture-native')
 assert native['exit_code']==0,(OUT/'fixture-native.log').read_text(errors='replace')
 for p in [exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),*deps.glob('*.json')]:pin(p)
 guard();manifest={rel(p):h for p,h in pins.items()}
 support=dict(id='heap-free-raw-binding-266',generated_source=rel(binding),generated_source_sha256=sha(binding),object=rel(support_obj),object_sha256=sha(support_obj),dependency_sha256={rel(binding):sha(binding)},include_directories=[rel(root) for root in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile.execution.json'),source_dependencies=rel(deps/'binding.cpp.json'),source_dependencies_sha256=sha(deps/'binding.cpp.json'),symbols=symbols,directive=directive,function_count=0)
 alias=dict(**{'from':RAW,'to':CAN},va='00531f90',support_object_id=support['id'],directive=directive,proof=dict(original_sha256=old['original_sha256'],ret_pop_bytes=0,representation='one x86 DWORD argument; full EAX=1 preserved',exact_consumer_evidence=rel(RUN/'preflight.json')))
 first=OUT/'first-compile.execution.json'
 summary=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=old['original_sha256'],compiler_sha256=sha(compiler),new_function_count=0,support_objects=[support],aliases=[alias],compiler_batch_exit_code=0,compiler_batch_seconds=compiled['seconds'],actual_compiler_batches=2 if first.exists() else 1,first_compile_failure=dict(receipt=rel(first),exit_code=json.loads(first.read_bytes())['exit_code'],reason='private fixture single-line MSVC inline assembly syntax') if first.exists() else None,actual_MP6_requested=True,input_sha256=manifest,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile.execution.json'),compiler_log=rel(OUT/'compile.log'),native_fixture=dict(executable=rel(exe),executable_sha256=sha(exe),exit_code=0,seconds=native['seconds'],raw_canonical_identity=True,full_EAX=1,relative_ESP=True,original_arena_bytes_compared=1024),ordinary_summary=rel(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/summary.json'),ordinary_summary_sha256=sha(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/summary.json'),production_ready=False,limits=['Controlled heap table and platform endpoints only','No new game COFF or game launch','Original provider composition remains separate'])
 write(RUN/'summary.json',summary)
 print(json.dumps(dict(support_objects=1,aliases=1,compile_exit=0,native_exit=0,pins=len(pins))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--finalize-existing',action='store_true');p.add_argument('--retry-failed-asm',action='store_true');a=p.parse_args();main(a.finalize_existing,a.retry_failed_asm)

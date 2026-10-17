"""Compile two exact file-operation fragments and their bounded raw ABI aliases."""
import argparse,hashlib,importlib.util,json,os,re,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/276-file-operation-reuse'
OUT=ROOT/'local/experiments/v2-file-operation-reuse-276'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=('00568200','005682a0')
NAMES=('operation_queue_00568200','operation_allocate_005682a0')
RAW=('?FUN_00568200@@YAIH@Z','?FUN_005682a0@@YAHIEII@Z')
CAN=('?operation_queue_00568200@porsche@@YAIPAUFileOperation@1@@Z','?operation_allocate_005682a0@porsche@@YAPAUFileOperation@1@IEPAXI@Z')
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
 kinds={'pop':1,'sorted':2,'event':3,'start':4,'lock':5,'unlock':6,'diagnostic':7}
 rows=[]
 for c in oracle['cases']:
  events=[]
  for ev in c['events']:
   a=ev[1] if len(ev)>1 and isinstance(ev[1],int) else 0
   b=ev[2] if len(ev)>2 and isinstance(ev[2],int) else 0
   events.append('{'+','.join(map(str,(kinds[ev[0]],a,b)))+'}')
  events+=['{0,0,0}']*(4-len(events))
  rows.append('{"'+c['name']+'",'+','.join(map(str,(int(c['kind']=='queue'),c['index'],c['serial'],c['initialized'],c['op_id'],int(c['pop']),c['eax'],c['diagnostic_line'],len(c['events']))))+',"'+c['before']['op']+'","'+c['before']['device']+'","'+c['after']['op']+'","'+c['after']['device']+'",{'+','.join(events)+'}}')
 table=',\n'.join(rows)
 return r'''#define PORSCHE_DEFINE_SHARED_RUNTIME_GLOBALS_FIXTURE
#include "porsche/files.hpp"
extern "C" __declspec(dllimport) void* __stdcall VirtualAlloc(void*,unsigned,unsigned,unsigned);
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
std::uint32_t __cdecl FUN_00568200(std::int32_t);
std::int32_t __cdecl FUN_005682a0(std::uint32_t,std::uint8_t,std::uint32_t,std::uint32_t);
using U=std::uint32_t;
static constexpr U DEV=0x03001000u,OP=0x03002000u,CONTEXT=0x03003000u,EVENT=0x03004000u;
struct Ev {U kind,a,b;};
struct Case {const char* name;U queue,index,serial,initialized,op_id,pop,eax,line,event_count;const char *op_before,*dev_before,*op_after,*dev_after;Ev events[4];};
static const Case cases[]={
'''+table+r'''
};
static U fail=0,events_count=0,pop_available=0,current_index=0;
static Ev events[8];
static unsigned char* arena=nullptr;
static U digit(char c){return c>='0'&&c<='9'?U(c-'0'):c>='a'&&c<='f'?U(c-'a'+10):99u;}
static void decode(unsigned char* p,const char* s,U n){for(U i=0;i<n;++i)p[i]=static_cast<unsigned char>((digit(s[i*2])<<4)|digit(s[i*2+1]));}
static void compare(const unsigned char* p,const char* s,U n){for(U i=0;i<n;++i)if(p[i]!=((digit(s[i*2])<<4)|digit(s[i*2+1])))++fail;}
static bool equal(const char* a,const char* b){while(*a&&*b){if(*a++!=*b++)return false;}return *a==*b;}
static void record(U k,U a=0,U b=0){if(events_count>=8){++fail;return;}events[events_count++]={k,a,b};}
namespace porsche {
FileDevice* devices_006a5c7c=nullptr;
IoList free_operations_006a5c58{};
void (__cdecl* diagnostic_handler_005debf0)(const char*)=nullptr;
IoNode* __cdecl io_pop_00580790(IoList* list){if(list!=&free_operations_006a5c58)++fail;record(1);return pop_available?reinterpret_cast<IoNode*>(OP):nullptr;}
void __cdecl io_sorted_00580850(IoList* list,IoNode* node){if(list!=&devices_006a5c7c[current_index].queued||reinterpret_cast<U>(node)!=OP)++fail;record(2,reinterpret_cast<U>(list),reinterpret_cast<U>(node));}
U __cdecl file_event_signal_0055fb30(void* event){record(3,reinterpret_cast<U>(event));return 1;}
void __cdecl file_start_device_00568390(U index){record(4,index);devices_006a5c7c[index].initialized=1;}
U __cdecl io_lock_00580ea0(IoList* list){record(5,reinterpret_cast<U>(list));return 0x1234abcdu;}
void __cdecl io_unlock_00580ec0(IoList* list,U token){record(6,reinterpret_cast<U>(list),token);}
}
static void diagnostic(const char* message){if(!equal(message,"FILE_allocateop - NO FREE OPS LEFT TO ALLOCATE.\n"))++fail;record(7);}
extern "C" void __cdecl entry(){
 arena=static_cast<unsigned char*>(VirtualAlloc(reinterpret_cast<void*>(0x03000000u),0x10000u,0x3000u,4u));
 if(reinterpret_cast<U>(arena)!=0x03000000u)ExitProcess(101);
 porsche::devices_006a5c7c=reinterpret_cast<porsche::FileDevice*>(DEV);
 porsche::diagnostic_handler_005debf0=diagnostic;
 for(U c=0;c<sizeof(cases)/sizeof(cases[0]);++c)for(U mode=0;mode<2;++mode){
  const Case& q=cases[c];current_index=q.index;pop_available=q.pop;events_count=0;
  unsigned char* op=arena+0x2000;unsigned char* dev=arena+0x1000+q.index*0x70;
  for(U i=0;i<0x70*2;++i)arena[0x1000+i]=0xcc;
  decode(op,q.op_before,48);decode(dev,q.dev_before,0x70);
  porsche::shared_runtime_word_005deb74=0;porsche::diagnostic_line_005deb78=0;
  U result;
  if(q.queue)result=mode?FUN_00568200(static_cast<std::int32_t>(OP)):porsche::operation_queue_00568200(reinterpret_cast<porsche::FileOperation*>(OP));
  else result=mode?static_cast<U>(FUN_005682a0(7,0xd7u,CONTEXT,q.index)):reinterpret_cast<U>(porsche::operation_allocate_005682a0(7,0xd7u,reinterpret_cast<void*>(CONTEXT),q.index));
  if(result!=q.eax||porsche::diagnostic_line_005deb78!=q.line)++fail;
  if(q.line){if(!equal(porsche::diagnostic_file_005deb74(),"\\real\\pc\\nfile.c"))++fail;}
  else if(porsche::diagnostic_file_005deb74()!=nullptr)++fail;
  compare(op,q.op_after,48);compare(dev,q.dev_after,0x70);
  if(events_count!=q.event_count)++fail;
  for(U i=0;i<q.event_count&&i<events_count;++i)if(events[i].kind!=q.events[i].kind||events[i].a!=q.events[i].a||events[i].b!=q.events[i].b)++fail;
 }
 ExitProcess(fail?1:0);
}
'''
def main(finalize):
 OUT.mkdir(parents=True,exist_ok=True)
 pre=RUN/'preflight.json';oracle_path=OUT/'original-oracles.json'
 assert pre.exists() and oracle_path.exists()
 if not finalize:assert not (OUT/'compile-001.execution.json').exists()
 pins={}
 def pin(p,expected=None):
  p=Path(p).resolve();h=sha(p);assert expected is None or h==expected,(p,h,expected);pins[p]=h;return p
 def guard():
  for p,h in pins.items():assert sha(p)==h,('input drift',p)
 def run(cmd,name):
  cmd=list(map(str,cmd));started=time.perf_counter()
  p=subprocess.run(cmd,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
  log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
  receipt=dict(command=cmd,exit_code=p.returncode,seconds=round(time.perf_counter()-started,6),log=rel(log),log_sha256=sha(log))
  write(OUT/(name+'.execution.json'),receipt);return receipt
 preflight=json.loads(pin(pre).read_bytes());oracle=json.loads(pin(oracle_path).read_bytes())
 assert preflight['original_sha256']==oracle['original_sha256']==SHA and oracle['preflight_sha256']==sha(pre)
 assert len(preflight['consumers'])==4 and len(oracle['cases'])==4
 for p in [__file__,ROOT/'scripts/research/preflight-v2-file-operation-reuse-276.py',ROOT/'scripts/research/oracle-v2-file-operation-reuse-276.py',ROOT/'local/game/Porsche.exe',ROOT/preflight['union_summary'],ROOT/preflight['registry'],ROOT/preflight['prior_oracle'],ROOT/preflight['header'],ROOT/preflight['source'],ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py'] :pin(p)
 assert sha(ROOT/'local/game/Porsche.exe')==SHA
 for x in preflight['consumers']:pin(ROOT/x['object'],x['object_sha256']);pin(ROOT/x['source'],x['source_sha256'])
 abi=module('abi276',ROOT/'scripts/research/experiment-v2-thiscall-186.py')
 coff=module('coff276',ROOT/'scripts/research/build-v2-compile-corpus.py')
 old=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/summary.json').read_bytes())
 pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/validation.json')
 roots=[(Path(n) if Path(n).is_absolute() else ROOT/n).resolve() for n in old['results'][0]['include_directories']]
 assert len(roots)==5 and all(x.is_dir() for x in roots)
 compiler=pin(abi.COMPILER,old['compiler_sha256']);linker=pin(abi.COMPILER.with_name('link.exe'))
 kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
 data=(ROOT/preflight['source']).read_bytes();source={};fragments={}
 for va,name in zip(VAS,NAMES):
  chunks=[b'#include "porsche/files.hpp"\nnamespace porsche {\n'];slices=[]
  for symbol in ('error',name):
   a,b,part=definition(data,symbol);chunks.extend((part,b'\n'));slices.append(dict(name=symbol,offset=a,length=b-a,sha256=hashlib.sha256(part).hexdigest()))
  chunks.append(b'}\n');path=RUN/(va+'.cpp');blob=b''.join(chunks)
  if finalize:assert path.read_bytes()==blob
  else:path.write_bytes(blob)
  source[va]=pin(path);fragments[va]=dict(source=preflight['source'],source_sha256=sha(ROOT/preflight['source']),slices=slices)
 binding=RUN/'file_operation_binding.cpp';bind_text=('#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4,"x86 ABI");\n'+''.join('#pragma comment(linker,"/alternatename:'+r+'='+c+'")\n' for r,c in zip(RAW,CAN))).encode()
 if finalize:assert binding.read_bytes()==bind_text
 else:binding.write_bytes(bind_text)
 pin(binding)
 fixture_path=RUN/'file_operation_fixture.cpp';fixture_text=fixture(oracle).encode('utf8')
 if finalize:assert fixture_path.read_bytes()==fixture_text
 else:fixture_path.write_bytes(fixture_text)
 pin(fixture_path)
 objects=OUT/'objects';deps=OUT/'dependencies';objects.mkdir(exist_ok=True);deps.mkdir(exist_ok=True)
 sources=[*source.values(),binding,fixture_path]
 flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GS-','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/sourceDependencies',str(deps)]
 command=[compiler,*flags,*[item for root in roots for item in ('/I',root)],'/Fo'+str(objects)+os.sep,*sources]
 if finalize:
  prepared=json.loads(pin(OUT/'prepare.json').read_bytes())
  for name,h in prepared['input_sha256'].items():pin(Path(name) if Path(name).is_absolute() else ROOT/name,h)
  compiled=json.loads(pin(OUT/'compile-001.execution.json').read_bytes());assert compiled['command']==list(map(str,command))
 else:
  guard();write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={rel(p):h for p,h in pins.items()}));compiled=run(command,'compile-001')
 assert compiled['exit_code']==0,(OUT/'compile-001.log').read_text(errors='replace')
 assert not re.search(rb'warning [CD]\d+|error [CD]\d+',(OUT/'compile-001.log').read_bytes())
 depmap={}
 for src in sources:
  dep=pin(deps/(src.name+'.json'));d=json.loads(dep.read_bytes());assert d['Version']=='1.2' and Path(d['Data']['Source']).resolve()==src
  includes={Path(x).resolve() for x in d['Data']['Includes']};assert all(any(x.is_relative_to(root) for root in roots) for x in includes)
  for x in includes:pin(x)
  depmap[src]=dict(path=dep,includes=includes)
 def row(src,obj,extra):
  syms=coff.coff_symbols(obj)
  return dict(compiled=True,compiler_exit_code=0,generated_source=rel(src),generated_source_sha256=sha(src),object=rel(obj),object_sha256=sha(obj),dependency_sha256={rel(x):pins[x] for x in depmap[src]['includes']|{src}},include_directories=[rel(x) for x in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),source_dependencies=rel(depmap[src]['path']),source_dependencies_sha256=sha(depmap[src]['path']),symbols=syms,**extra)
 results=[]
 for va,name,canonical in zip(VAS,NAMES,CAN):
  obj=pin(objects/(va+'.obj'));syms=coff.coff_symbols(obj)
  assert syms['defined']==[canonical] and not syms['common'] and not syms['weak']
  results.append(row(source[va],obj,dict(va=va,name=name,canonical_reuse=True,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,forced_headers=[],defined_external_symbols=syms['defined'],undefined_external_symbols=syms['undefined'])))
 binding_obj=pin(objects/'file_operation_binding.obj');bs=coff.coff_symbols(binding_obj);assert not any(bs.values())
 fixture_obj=pin(objects/'file_operation_fixture.obj')
 exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
 link=[linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),*[objects/(va+'.obj') for va in VAS],binding_obj,fixture_obj,kernel]
 if finalize and (OUT/'fixture-link-001.execution.json').exists():linked=json.loads(pin(OUT/'fixture-link-001.execution.json').read_bytes())
 else:linked=run(link,'fixture-link-001')
 assert linked['exit_code']==0,(OUT/'fixture-link-001.log').read_text(errors='replace')
 if finalize and (OUT/'fixture-native-001.execution.json').exists():native=json.loads(pin(OUT/'fixture-native-001.execution.json').read_bytes())
 else:native=run([exe],'fixture-native-001')
 assert native['exit_code']==0,(OUT/'fixture-native-001.log').read_text(errors='replace')
 for p in [exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),*deps.glob('*.json')]:pin(p)
 guard();manifest={rel(p):h for p,h in pins.items()}
 summary=dict(schema=1,kind='canonical-body-reuse-batch',module='Porsche.exe',original_sha256=SHA,objects_compiled=2,real_coff_objects=2,results=results,compiled_vas=list(VAS),new_distinct_function_VAs=2,actual_compiler_batches=1,actual_MP6_requested=True,changed_game_TUs=2,handwritten_game_algorithm_TUs=0,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=compiled['seconds'],compiler_sha256=sha(compiler),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),compiler_log=rel(OUT/'compile-001.log'),compiler_log_sha256=sha(OUT/'compile-001.log'),source_dependencies_format='MSVC1.2',input_sha256=manifest,input_guards_before=True,input_guards_after=True,original_selected_bytes=sum(x['size'] for x in preflight['targets']),canonical_fragments=fragments,original_oracles=rel(oracle_path),original_oracles_sha256=sha(oracle_path),native_fixture=dict(executable=rel(exe),executable_sha256=sha(exe),exit_code=0,seconds=native['seconds'],original_cutpoints=4,canonical_and_raw_calls=8,controlled_providers=['io_pop','io_sorted','file_event_signal','file_start_device','io_lock','io_unlock','diagnostic_handler','devices','free_operations'],memory_and_ordered_calls_compared=True),production_ready=False,production_or_union_changes=False,limits=['No original disk/event/platform execution','No game global owner or service provider compiled','No caller object or handle_device ABI changes'])
 write(RUN/'summary.json',summary)
 binding_row=row(binding,binding_obj,dict(id='file-operation-abi-276',function_count=0,directives=['/alternatename:'+r+'='+c for r,c in zip(RAW,CAN)]))
 aliases=[dict(**{'from':r,'to':c},va=va,support_object_id=binding_row['id'],directive='/alternatename:'+r+'='+c,proof=dict(original_sha256=SHA,preflight=rel(pre),raw_references=4)) for va,r,c in zip(VAS,RAW,CAN)]
 support=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=SHA,compiler_sha256=sha(compiler),new_function_count=0,support_objects=[binding_row],aliases=aliases,compiler_batch_exit_code=0,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),ordinary_summary=rel(RUN/'summary.json'),ordinary_summary_sha256=sha(RUN/'summary.json'),input_sha256={**manifest,rel(RUN/'summary.json'):sha(RUN/'summary.json')},production_ready=False,limits=summary['limits'])
 (RUN/'bindings').mkdir(exist_ok=True);write(RUN/'bindings/summary.json',support)
 print(json.dumps(dict(bodies=2,aliases=2,compile_exit=0,native_exit=0,oracle_cases=4,pins=len(pins))))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--finalize-existing',action='store_true');main(a.parse_args().finalize_existing)

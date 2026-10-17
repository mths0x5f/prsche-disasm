"""One original zero-tail heap table allocation and a proven raw base alias."""
import argparse,hashlib,importlib.util,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/272-shared-heap-table'
OUT=ROOT/'local/experiments/v2-shared-heap-table-272'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
RAW='?DAT_006b4f20@@3IA';CAN='?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
DATA='#include "porsche/heap.hpp"\nnamespace porsche {\nOriginalHeap* heaps_006b4f20[16];\n}\n'
BINDING='#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4,"original DWORD slots");\n#pragma comment(linker,"/alternatename:'+RAW+'='+CAN+'")\n'
FIXTURE=r'''#include "porsche/heap.hpp"
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned);
extern unsigned int DAT_006b4f20;
using U=std::uint32_t;
U fail272=0;
volatile U canary_before272=0x1234abcd,canary_after272=0xfedc4321;
alignas(16) unsigned char safe272[256];
static U load272(const unsigned char* p){return U(p[0])|(U(p[1])<<8)|(U(p[2])<<16)|(U(p[3])<<24);}
static void store272(unsigned char* p,U value){for(U i=0;i<4;++i)p[i]=static_cast<unsigned char>(value>>(i*8));}
extern "C" void __cdecl entry(){
 static_assert(sizeof(void*)==4&&sizeof(porsche::heaps_006b4f20)==64,"one original 64B table");
 unsigned char* typed=reinterpret_cast<unsigned char*>(&porsche::heaps_006b4f20[0]);
 volatile U* raw=reinterpret_cast<volatile U*>(&DAT_006b4f20);
 if(reinterpret_cast<const void*>(&DAT_006b4f20)!=reinterpret_cast<const void*>(&porsche::heaps_006b4f20[0]))++fail272;
 for(U i=0;i<64;++i)if(typed[i]!=0)++fail272;
 for(U i=0;i<16;++i){
  U bits=0x80000000u^(0x01020304u*i)^i;
  raw[i]=bits;
  if(load272(typed+i*4)!=bits)++fail272;
  for(U j=0;j<i;++j)if(load272(typed+j*4)!=(0x80000000u^(0x01020304u*j)^j))++fail272;
 }
 for(U i=0;i<16;++i){
  porsche::heaps_006b4f20[i]=reinterpret_cast<porsche::OriginalHeap*>(safe272+i*16);
  if(raw[i]!=reinterpret_cast<U>(safe272+i*16))++fail272;
 }
 for(U i=0;i<16;++i){
  U bits=0xf0000000u|(i<<20)|0x000abcdu;
  store272(typed+i*4,bits);
  if(raw[i]!=bits)++fail272;
 }
 if(canary_before272!=0x1234abcdu||canary_after272!=0xfedc4321u)++fail272;
 ExitProcess(fail272?1:0);
}
'''
def main(finalize):
 pre=RUN/'preflight.json';assert pre.exists() and not (RUN/'summary.json').exists()
 if not finalize:assert not (OUT/'compile-001.execution.json').exists()
 pins={}
 def pin(p,expected=None):
  p=Path(p).resolve();h=sha(p);assert expected is None or h==expected,(p,h,expected);pins[p]=h;return p
 def guard():
  for p,h in pins.items():assert sha(p)==h,('input drift',p)
 def run(command,name):
  command=list(map(str,command));start=time.perf_counter()
  proc=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
  log=OUT/(name+'.log');log.write_bytes((proc.stdout+proc.stderr).replace(b'\r\n',b'\n'))
  receipt=dict(command=command,exit_code=proc.returncode,seconds=round(time.perf_counter()-start,6),log=rel(log),log_sha256=sha(log))
  write(OUT/(name+'.execution.json'),receipt);return receipt
 preflight=json.loads(pin(pre).read_bytes());assert preflight['storage_approved'] and preflight['alias_approved'] and len(preflight['raw_consumers'])==2
 for p in [__file__,ROOT/'scripts/research/preflight-v2-shared-heap-table-272.py',ROOT/'local/game/Porsche.exe',ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence/summary.json',ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence/validation.json',ROOT/'iterations/v2/001-original-recovery/runs/270-heap-consumer-index/preflight.json',ROOT/'iterations/v2/001-original-recovery/runs/271-heap-candidate-index/summary.json',ROOT/'iterations/v2/001-original-recovery/runs/271-heap-candidate-index/validation.json',ROOT/'research/binary-index/supplemental/heap-consumers-271.jsonl',ROOT/preflight['canonical_source'],ROOT/preflight['canonical_header']]:pin(p)
 assert sha(ROOT/'local/game/Porsche.exe')==SHA
 for consumer in preflight['raw_consumers']:pin(ROOT/consumer['object'],consumer['object_sha256'])
 old=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/summary.json').read_bytes())
 pin(ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release/validation.json')
 native=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/runs/268-native-platform-providers/summary.json').read_bytes())
 pin(ROOT/'iterations/v2/001-original-recovery/runs/268-native-platform-providers/validation.json')
 abi=mod('abi272',pin(ROOT/'scripts/research/experiment-v2-thiscall-186.py'))
 coff=mod('coff272',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
 parser=mod('parse272',pin(ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py'))
 roots=[(Path(n) if Path(n).is_absolute() else ROOT/n).resolve() for n in old['results'][0]['include_directories']]
 assert len(roots)==5 and all(x.is_dir() for x in roots)
 for n,h in old['input_sha256'].items():
  p=Path(n);p=p if p.is_absolute() else ROOT/p
  if p.suffix.lower() in ('.h','.hpp') and p.exists():pin(p,h if sha(p)==h else None)
 compiler=pin(abi.COMPILER,old['compiler_sha256']);linker=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
 reused=[]
 for va in ('00531f90','005322b0','005322c0'):
  r=next(x for x in old['results'] if x['va']==va);reused.append(pin(ROOT/r['object'],r['object_sha256']))
 provider=native['support_objects'][0];reused.append(pin(ROOT/provider['object'],provider['object_sha256']))
 sources=[RUN/'original_heap_table.cpp',RUN/'heap_table_binding.cpp',RUN/'heap_table_fixture.cpp']
 for p,content in zip(sources,(DATA,BINDING,FIXTURE)):
  if finalize:assert p.read_bytes()==content.encode()
  else:p.write_bytes(content.encode())
  pin(p)
 objects=OUT/'objects';deps=OUT/'dependencies'
 if not finalize:objects.mkdir(parents=True,exist_ok=True);deps.mkdir(parents=True,exist_ok=True)
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
  includes={Path(x).resolve() for x in d['Data']['Includes']};assert all(any(h.is_relative_to(root) for root in roots) for h in includes)
  for h in includes:pin(h)
  depmap[src]=dict(path=dep,includes=includes)
 data_obj=pin(objects/'original_heap_table.obj');binding_obj=pin(objects/'heap_table_binding.obj');fixture_obj=pin(objects/'heap_table_fixture.obj')
 data_symbols=coff.coff_symbols(data_obj);binding_symbols=coff.coff_symbols(binding_obj)
 assert data_symbols['defined']==[CAN] and not data_symbols['undefined'] and not any(binding_symbols.values())
 parsed=parser.coff(data_obj);sym=next(x for x in parsed['symbols'] if x['name']==CAN)
 sec=parsed['sections'][sym['section']-1]
 assert sym['value']==0 and sec['size']==64 and sec['reloc_count']==0 and sec['chars']&0x80000000 and not sec['chars']&0x20000000
 bparsed=parser.coff(binding_obj);bsec=next(x for x in bparsed['sections'] if x['name']=='.drectve')
 directive=bparsed['bytes'][bsec['raw']:bsec['raw']+bsec['size']].decode('ascii').strip()
 assert directive=='/alternatename:'+RAW+'='+CAN
 exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
 link=[linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),data_obj,binding_obj,fixture_obj,*reused,kernel]
 if finalize and (OUT/'fixture-link-001.execution.json').exists():linked=json.loads(pin(OUT/'fixture-link-001.execution.json').read_bytes())
 else:linked=run(link,'fixture-link-001')
 assert linked['exit_code']==0,(OUT/'fixture-link-001.log').read_text(errors='replace')
 if finalize and (OUT/'fixture-native-001.execution.json').exists():executed=json.loads(pin(OUT/'fixture-native-001.execution.json').read_bytes())
 else:executed=run([exe],'fixture-native-001')
 assert executed['exit_code']==0,(OUT/'fixture-native-001.log').read_text(errors='replace')
 for p in [exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),*deps.glob('*.json')]:pin(p)
 guard();manifest={rel(p):h for p,h in pins.items()}
 def support(id,src,obj,symbols,extra):
  return dict(id=id,compiled=True,compiler_exit_code=0,generated_source=rel(src),generated_source_sha256=sha(src),object=rel(obj),object_sha256=sha(obj),dependency_sha256={rel(x):pins[x] for x in depmap[src]['includes']|{src}},include_directories=[rel(x) for x in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),source_dependencies=rel(depmap[src]['path']),source_dependencies_sha256=sha(depmap[src]['path']),symbols=symbols,**extra)
 data_row=support('shared-heap-table-272',sources[0],data_obj,data_symbols,dict(storage_sections=[dict(name=sec['name'],size=sec['size'],chars=sec['chars'],reloc_count=sec['reloc_count'])],function_count=0))
 binding_row=support('shared-heap-table-binding-272',sources[1],binding_obj,binding_symbols,dict(directive=directive,function_count=0))
 limits=['Only original 006b4f20..006b4f5f physical span; no neighboring 006b4f60 cell','Four candidate code entries remain unproved/unpromoted','No original relative layout, computed aliases or initialization caller semantics','Native invalid pointer patterns are copied as bits only']
 summary=dict(schema=1,kind='original-writable-data',module='Porsche.exe',original_sha256=SHA,functions_added=0,data_symbols=1,physical_data_cells=1,storage_va='006b4f20',storage_bytes=64,initial_bytes='00'*64,source_slice=preflight['canonical_declaration'],support_objects=[data_row],compiler_sha256=sha(compiler),compiler_batch_exit_code=0,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),actual_compiler_batches=1,actual_MP6_requested=True,input_sha256=manifest,native_fixture=dict(exit_code=0,seconds=executed['seconds'],executable=rel(exe),executable_sha256=sha(exe),slots=16,zero_bytes=64,crosswrites=True,canaries=True,invalid_pointer_bits_never_dereferenced=True),production_ready=False,limits=limits)
 write(RUN/'summary.json',summary)
 alias=dict(**{'from':RAW,'to':CAN},va='006b4f20',support_object_id=binding_row['id'],directive=directive,proof=dict(original_sha256=SHA,representation='same original 64B base, 16 masked DWORD slots',raw_consumers=rel(pre)))
 bindings=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=SHA,compiler_sha256=sha(compiler),new_function_count=0,support_objects=[binding_row],aliases=[alias],compiler_batch_exit_code=0,compiler_command=list(map(str,command)),compiler_execution_receipt=rel(OUT/'compile-001.execution.json'),ordinary_summary=rel(RUN/'summary.json'),ordinary_summary_sha256=sha(RUN/'summary.json'),input_sha256={**manifest,rel(RUN/'summary.json'):sha(RUN/'summary.json')},production_ready=False,limits=limits)
 (RUN/'bindings').mkdir(exist_ok=True);write(RUN/'bindings/summary.json',bindings)
 print(json.dumps(dict(data_objects=1,bindings=1,compile_exit=0,native_exit=0,pins=len(pins))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--finalize-existing',action='store_true');main(p.parse_args().finalize_existing)

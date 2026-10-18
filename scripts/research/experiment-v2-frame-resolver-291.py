"""Typed 004898f0 replacement and exact 25-byte native oracle, one batch."""
import argparse, hashlib, importlib.util, json, os, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/291-frame-resolver'
OUT=ROOT/'local/experiments/v2-frame-resolver-291'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--finalize-existing',action='store_true');args=parser.parse_args()
 assert not(RUN/'summary.json').exists(),'Completed packet immutable'
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'objects').mkdir(exist_ok=True);(OUT/'dependencies').mkdir(exist_ok=True)
 baseline=load(ROOT/'iterations/v2/001-original-recovery/runs/290-frame-service-cluster/summary.json')
 compiler=Path(baseline['compiler_command'][0]);linker=compiler.with_name('link.exe')
 roots=[ROOT/x if not Path(x).is_absolute() else Path(x) for x in baseline['results'][0]['include_directories']]
 source=RUN/'004898f0.cpp';fixture=RUN/'fixture.cpp';sources=[source,fixture]
 objects=[OUT/'objects'/(x.stem+'.obj') for x in sources]
 old_packet=ROOT/'iterations/v2/001-original-recovery/runs/187-thiscall-leaf-candidates/summary.json'
 old=next(x for x in load(old_packet)['results'] if x['va']=='004898f0')
 assert sha(ROOT/old['object'])==old['object_sha256'] and sha(ROOT/old['generated_source'])==old['generated_source_sha256']
 assert old['method_contract']['return_storage']=='<VOID>'
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 assert not any(x['entry_va']=='004898f0' for x in registry)
 body=bytes.fromhex(old['original_instruction_bytes_hex']);assert len(body)==25
 pe=module('read291',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 assert pe.pe_read((ROOT/'local/game/Porsche.exe').read_bytes(),0x4898f0,25)==body
 assert sha(ROOT/'local/game/Porsche.exe')==SHA
 kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
 inputs=[*sources,RUN.parent/'290-frame-service-cluster/frame_service_290.hpp',old_packet,ROOT/old['object'],ROOT/old['generated_source'],compiler,linker,kernel,ROOT/'local/game/Porsche.exe']
 pins={rel(p):sha(p) for p in inputs}
 command=[str(compiler),'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GS-','/GR-','/EHsc','/W4','/utf-8','/MP6','/Zl','/sourceDependencies',str(OUT/'dependencies'),*[a for p in roots for a in ('/I',str(p))],'/Fo'+str(OUT/'objects')+os.sep,*map(str,sources)]
 def run(cmd,name):
  rp=OUT/(name+'.receipt.json');lp=OUT/(name+'.log');assert not rp.exists() and not lp.exists()
  start=time.perf_counter();p=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CL':'','_CL_':'','INCLUDE':''},stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  lp.write_bytes(p.stdout);d=dict(command=cmd,cwd=str(ROOT),exit_code=p.returncode,seconds=time.perf_counter()-start,log=rel(lp),log_sha256=sha(lp));save(rp,d);return d
 if not args.finalize_existing:
  assert not(OUT/'before.json').exists()
  (OUT/'producer-used.py').write_bytes(Path(__file__).read_bytes());pins[rel(OUT/'producer-used.py')]=sha(OUT/'producer-used.py')
  save(OUT/'before.json',dict(input_sha256=pins,command=command,old_void_candidate=old,original_body_hex=body.hex()))
  compile_receipt=run(command,'compile-001')
 else:
  before=load(OUT/'before.json');pins=before['input_sha256'];assert before['command']==command
  compile_receipt=load(OUT/'compile-001.receipt.json')
 assert compile_receipt['exit_code']==0,'Compile receipt preserved'
 coff=module('coff291',ROOT/'scripts/research/build-v2-compile-corpus.py')
 oracle=module('oracle291',ROOT/'scripts/research/audit-v2-direct-callee-223.py')
 native,relocations=oracle.coff_function(objects[1],'@reference291@16');assert native==body and not relocations
 symbols=coff.coff_symbols(objects[0]);assert len(symbols['defined'])==1 and 'resolve_004898f0' in symbols['defined'][0] and not symbols['undefined']
 for src in sources:
  p=OUT/'dependencies'/(src.name+'.json');pins[rel(p)]=sha(p)
  for name in load(p)['Data']['Includes']:pins[rel(name)]=sha(name)
 exe=OUT/'fixture.exe';link=[str(linker),'/nologo','/MACHINE:X86','/NODEFAULTLIB','/ENTRY:entry','/SUBSYSTEM:CONSOLE','/OUT:'+str(exe),*map(str,objects),str(kernel)]
 if args.finalize_existing and (OUT/'link-001.receipt.json').exists():linked=load(OUT/'link-001.receipt.json')
 else:linked=run(link,'link-001')
 assert linked['exit_code']==0,'Link receipt preserved'
 if args.finalize_existing and (OUT/'native-001.receipt.json').exists():native_receipt=load(OUT/'native-001.receipt.json')
 else:native_receipt=run([str(exe)],'native-001')
 assert native_receipt['exit_code']==0 and load(OUT/'native-001.log')==dict(cases=512,failures=0)
 assert all(sha(ROOT/p if not Path(p).is_absolute() else p)==h for p,h in pins.items()),'input drift'
 for p in [*objects,exe,*OUT.glob('*.receipt.json'),*OUT.glob('*.log')]:pins[rel(p)]=sha(p)
 summary=dict(schema=1,kind='typed-frame-resolver-replacement',original_sha256=SHA,va='004898f0',original_body_bytes=25,original_body_hex=body.hex(),new_distinct_function_VAs=0,old_void_candidate={k:old[k] for k in ('va','object','object_sha256','generated_source','generated_source_sha256','defined_external_symbols','method_contract')},game_objects=[dict(path=rel(objects[0]),sha256=sha(objects[0]))],game_source=rel(source),defined_symbols=symbols['defined'],undefined_symbols=symbols['undefined'],native_cases=512,native_exit=0,oracle_relocations=0,compiler_batches=1,input_sha256=pins,limits=['Old187 void-return object must be explicitly replaced in any future raw union; not linked by game293','Native value/alias cases are finite; faults and arbitrary stack aliases are unproved'])
 save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),input_pins=len(pins),exact_native_oracle_bytes=25,native_cases=512,no_game_provider_definitions=True))
 print(json.dumps(dict(passed=True,native_cases=512,game_objects=1,new_distinct_VAs=0)))
if __name__=='__main__':main()

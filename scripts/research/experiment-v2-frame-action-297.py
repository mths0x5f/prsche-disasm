"""One MP6 batch for original frame action and finite native oracle comparisons."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path
from v2_shared_manifests import ManifestReader, externalize
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/297-frame-action'
OUT=ROOT/'local/experiments/v2-frame-action-297'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p): return json.loads(Path(p).read_bytes())
def save(p,d): p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);parser.add_argument('--finalize-existing',action='store_true');args=parser.parse_args()
 assert args.attempt.isdigit() and len(args.attempt)==3
 assert not (RUN/'summary.json').exists(),'Completed packet immutable'
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'objects').mkdir(exist_ok=True);(OUT/'dependencies').mkdir(exist_ok=True)
 baseline=load(RUN.parent/'290-frame-service-cluster/summary.json')
 compiler=Path(baseline['compiler_command'][0]);linker=compiler.with_name('link.exe')
 roots=[ROOT/x if not Path(x).is_absolute() else Path(x) for x in baseline['results'][0]['include_directories']]
 original=(ROOT/'local/game/Porsche.exe').read_bytes();assert sha(ROOT/'local/game/Porsche.exe')==SHA
 audit=module('read297',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 body=audit.pe_read(original,0x476170,169)
 recorded=bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))
 assert body==recorded and body[43]==0xe8 and int.from_bytes(body[44:48],'little')+0x4761a0==0x476710
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
 block=asm.split('; FUNCTION 00476170 ',1)[1].split('; FUNCTION ',1)[0]
 assert b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^[0-9a-f]{8}\s+([0-9a-f]+)\s+',block))==body
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 assert not any(x['entry_va']=='00476170' for x in registry)
 index=[json.loads(x) for x in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 accepted={x['entry_va'] for x in registry}
 assert not any(int(a,16)<=0x476170<=int(b,16) for x in index if x['entry_va'] in accepted for a,b in x['ranges'])
 sources=[RUN/'00476170.cpp',RUN/'fixture.cpp'];objects=[OUT/'objects'/(p.stem+'.obj') for p in sources]
 kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
 repo_inputs=[*sources,RUN/'action_297.hpp',RUN/'original-body.inc',RUN.parent/'290-frame-service-cluster/frame_service_290.hpp',ROOT/'local/game/Porsche.exe',Path(__file__),ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py']
 pins={rel(p):sha(p) for p in repo_inputs}
 tool_pins={str(p):sha(p) for p in [compiler,linker,kernel]}
 command=[str(compiler),'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GS-','/GR-','/EHsc','/W4','/utf-8','/MP6','/Zl','/sourceDependencies',str(OUT/'dependencies'),*[a for p in roots for a in ('/I',str(p))],'/Fo'+str(OUT/'objects')+os.sep,*map(str,sources)]
 def run(cmd,name):
  rp=OUT/(name+'.receipt.json');lp=OUT/(name+'.log');assert not rp.exists() and not lp.exists()
  start=time.perf_counter();p=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CL':'','_CL_':'','INCLUDE':''},stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  lp.write_bytes(p.stdout);receipt=dict(command=cmd,cwd=str(ROOT),exit_code=p.returncode,seconds=time.perf_counter()-start,log=rel(lp),log_sha256=sha(lp));save(rp,receipt);return receipt
 preflight=OUT/('before-'+args.attempt+'.json')
 if not args.finalize_existing:
  assert not preflight.exists();save(preflight,dict(input_sha256=pins,tool_sha256=tool_pins,command=command))
  compiled=run(command,'compile-'+args.attempt)
 else:
  before=load(preflight);assert before['input_sha256']==pins and before['command']==command and before['tool_sha256']==tool_pins
  compiled=load(OUT/('compile-'+args.attempt+'.receipt.json'))
 assert compiled['exit_code']==0,'Compile failed; receipt preserved'
 for src in sources:
  p=OUT/'dependencies'/(src.name+'.json');pins[rel(p)]=sha(p)
  for name in load(p)['Data']['Includes']:
   p=Path(name)
   if p.is_relative_to(ROOT):pins[rel(p)]=sha(p)
   else:tool_pins[str(p)]=sha(p)
 coff=module('coff297',ROOT/'scripts/research/build-v2-compile-corpus.py')
 symbols=coff.coff_symbols(objects[0]);assert len(symbols['defined'])==1 and 'invoke_00476170' in symbols['defined'][0]
 assert len(symbols['undefined'])==1 and 'update_00476710' in symbols['undefined'][0]
 exe=OUT/'fixture.exe';link=[str(linker),'/nologo','/MACHINE:X86','/NODEFAULTLIB','/ENTRY:entry','/SUBSYSTEM:CONSOLE','/OUT:'+str(exe),*map(str,objects),str(kernel)]
 name='link-'+args.attempt
 linked=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run(link,name)
 assert linked['exit_code']==0,'Link failed; receipt preserved'
 name='native-'+args.attempt
 native=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run([str(exe)],name)
 assert native['exit_code']==0,'Native comparison failed; receipt preserved'
 assert load(ROOT/native['log'])==dict(cases=480,failures=0)
 for p in [*objects,exe,*OUT.glob('*.receipt.json'),*OUT.glob('*.log'),*OUT.glob('before-*.json')]: pins[rel(p)]=sha(p)
 summary=dict(schema=2,kind='original-frame-action',original_sha256=SHA,va='00476170',original_body_hex=body.hex(),original_body_bytes=169,original_relocated_call=dict(offset=43,operand=44,next=48,target='00476710'),game_objects=[dict(path=rel(objects[0]),sha256=sha(objects[0]))],game_source=rel(sources[0]),symbols=symbols,native_cases=480,native_exit=0,compiler_batches=1,selected_attempt=args.attempt,tool_sha256=tool_pins,input_sha256=pins,limits=['00476710 algorithm remains explicit external boundary; fixture controlled provider is not linked into game','Virtual destructor and update implementations remain caller-supplied boundaries','Finite valid-memory states; not whole game or arbitrary fault/DF behavior acceptance'])
 summary=externalize(ROOT,summary,'input','raw')
 reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw');assert all(sha(p)==h for p,h in tool_pins.items())
 save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),original_body_bytes=169,native_cases=480,game_defined_symbols=1,game_undefined_symbols=1,input_manifest=summary['input_manifest']))
 print(json.dumps(dict(passed=True,native_cases=480,game_objects=1,undefined=symbols['undefined'])))
if __name__=='__main__': main()

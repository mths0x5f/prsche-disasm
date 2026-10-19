"""One MP6 batch for original frame action and finite native oracle comparisons."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path
from v2_shared_manifests import ManifestReader, externalize
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/304-heap-slot-release'
OUT=ROOT/'local/experiments/v2-heap-slot-release-304'
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
 audit=module('read304',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 body=audit.pe_read(original,0x5699f0,72)
 recorded=bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))
 assert body==recorded and body[-3:]==bytes.fromhex('5f5ec3')
 assert body[14:18]==body[21:25]==bytes.fromhex('204f6b00')
 assert 0x5699f0+42+int.from_bytes(body[38:42],'little',signed=True)==0x5322d0
 assert 0x5699f0+55+int.from_bytes(body[51:55],'little',signed=True)==0x53c290
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
 block=asm.split('; FUNCTION 005699f0 ',1)[1].split('; FUNCTION ',1)[0]
 assert b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^[0-9a-f]{8}\s+([0-9a-f]+)\s+',block))==body
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 assert not any(x['entry_va']=='005699f0' for x in registry)
 index=[json.loads(x) for x in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 accepted={x['entry_va'] for x in registry}
 assert not any(int(a,16)<=0x569a37 and 0x5699f0<=int(b,16) for x in index if x['entry_va'] in accepted for a,b in x['ranges'])
 assert any(x['entry_va']=='005322d0' for x in registry)
 assert not any(x['va']=='005699f0' for x in load(RUN.parent/'274-shared-heap-union/summary.json')['results'])
 sources=[RUN/'005699f0.cpp',RUN/'fixture.cpp'];objects=[OUT/'objects'/(p.stem+'.obj') for p in sources]
 kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
 owner_summary=RUN.parent/'272-shared-heap-table/summary.json';owner=load(owner_summary)['support_objects'][0]
 table_object=ROOT/owner['object'];assert sha(table_object)==owner['object_sha256']
 assert sha(ROOT/owner['generated_source'])==owner['generated_source_sha256']
 repo_inputs=[owner_summary,table_object,ROOT/owner['generated_source'],*sources,RUN/'heap_slot_release_304.hpp',RUN/'original-body.inc',RUN.parent/'290-frame-service-cluster/frame_service_290.hpp',ROOT/'local/game/Porsche.exe',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json',Path(__file__),ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py']
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
 coff=module('coff304',ROOT/'scripts/research/build-v2-compile-corpus.py')
 symbols=coff.coff_symbols(objects[0]);assert len(symbols['defined'])==1 and 'heap_slot_release_005699f0' in symbols['defined'][0]
 assert len(symbols['undefined'])==3 and not symbols['weak'] and not symbols['common']
 assert all(any(name in x for x in symbols['undefined']) for name in ('heaps_006b4f20','heap_lock_destroy_005322d0','heap_fill_0053c290'))
 exe=OUT/'fixture.exe';link=[str(linker),'/nologo','/MACHINE:X86','/NODEFAULTLIB','/ENTRY:entry','/SUBSYSTEM:CONSOLE','/OUT:'+str(exe),*map(str,objects),str(table_object),str(kernel)]
 name='link-'+args.attempt
 linked=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run(link,name)
 assert linked['exit_code']==0,'Link failed; receipt preserved'
 name='native-'+args.attempt
 native=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run([str(exe)],name)
 assert native['exit_code']==0,'Native comparison failed; receipt preserved'
 assert load(ROOT/native['log'])==dict(cases=960,failures=0)
 for p in [*objects,exe,*OUT.glob('*.receipt.json'),*OUT.glob('*.log'),*OUT.glob('before-*.json')]: pins[rel(p)]=sha(p)
 summary=dict(schema=2,kind='original-heap-slot-release',original_sha256=SHA,va='005699f0',original_body_hex=body.hex(),original_body_bytes=72,game_objects=[dict(path=rel(objects[0]),sha256=sha(objects[0]))],game_source=rel(sources[0]),symbols=symbols,reused_table_object=dict(path=rel(table_object),sha256=sha(table_object)),original_relocations=[dict(kind='DIR32',offset=14,target='006b4f20'),dict(kind='DIR32',offset=21,target='006b4f20'),dict(kind='REL32',offset=38,next=42,target='005322d0'),dict(kind='REL32',offset=51,next=55,target='0053c290')],native_cases=960,native_exit=0,compiler_batches=1,selected_attempt=args.attempt,tool_sha256=tool_pins,input_sha256=pins,limits=['Lock destruction and fill remain canonical external boundaries; fixture providers are controlled only','Finite valid-memory states; not whole game or arbitrary fault/DF behavior acceptance'])
 summary=externalize(ROOT,summary,'input','raw')
 reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw');assert all(sha(p)==h for p,h in tool_pins.items())
 save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),original_body_bytes=72,native_cases=960,game_defined_symbols=1,game_undefined_symbols=3,input_manifest=summary['input_manifest']))
 print(json.dumps(dict(passed=True,native_cases=960,game_objects=1,undefined=symbols['undefined'])))
if __name__=='__main__': main()

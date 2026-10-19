"""One MP6 batch for original frame action and finite native oracle comparisons."""
import argparse, hashlib, importlib.util, json, os, re, subprocess, time
from pathlib import Path
from v2_shared_manifests import ManifestReader, externalize
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/307-disk-slot-shutdown'
OUT=ROOT/'local/experiments/v2-disk-slot-shutdown-307'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p): return json.loads(Path(p).read_bytes())
def save(p,d): p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);parser.add_argument('--link-attempt',required=True);parser.add_argument('--finalize-existing',action='store_true');args=parser.parse_args()
 assert args.attempt.isdigit() and len(args.attempt)==3
 assert not (RUN/'summary.json').exists(),'Completed packet immutable'
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'objects').mkdir(exist_ok=True);(OUT/'dependencies').mkdir(exist_ok=True)
 baseline=load(RUN.parent/'290-frame-service-cluster/summary.json')
 compiler=Path(baseline['compiler_command'][0]);linker=compiler.with_name('link.exe')
 roots=[ROOT/x if not Path(x).is_absolute() else Path(x) for x in baseline['results'][0]['include_directories']]
 original=(ROOT/'local/game/Porsche.exe').read_bytes();assert sha(ROOT/'local/game/Porsche.exe')==SHA
 audit=module('read307',ROOT/'scripts/research/audit-v2-frame-service-290.py')
 body=audit.pe_read(original,0x5918c0,181)
 recorded=bytes(int(x,16) for x in (RUN/'original-body.inc').read_text().strip().split(','))
 assert body==recorded and body[-3:]==bytes.fromhex('005ec3')
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text()
 block=asm.split('; FUNCTION 005918c0 ',1)[1].split('; FUNCTION ',1)[0]
 assert b''.join(bytes.fromhex(x) for x in re.findall(r'(?m)^[0-9a-f]{8}\s+([0-9a-f]+)\s+',block))==body
 registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
 assert not any(x['entry_va']=='005918c0' for x in registry)
 index=[json.loads(x) for x in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
 accepted={x['entry_va'] for x in registry}
 assert not any(int(a,16)<=0x591974 and 0x5918c0<=int(b,16) for x in index if x['entry_va'] in accepted for a,b in x['ranges'])
 callee_vas={'005322b0','005322c0','005322d0','00592290','0056e640'}
 assert callee_vas<=accepted
 canonical_sources=[ROOT/x['source'] for x in registry if x['entry_va'] in callee_vas]
 sources=[RUN/'005918c0.cpp',RUN/'fixture.cpp'];objects=[OUT/'objects'/(p.stem+'.obj') for p in sources]
 kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
 repo_inputs=[*sources,ROOT/'iterations/v2/001-original-recovery/source/include/porsche/application_pool.hpp',RUN/'original-body.inc',RUN/'relocations.inc',RUN.parent/'290-frame-service-cluster/frame_service_290.hpp',ROOT/'local/game/Porsche.exe',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json',Path(__file__),ROOT/'scripts/research/v2_shared_manifests.py',ROOT/'scripts/research/v2_proof_cache.py']
 repo_inputs+=canonical_sources+[ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'/name for name in ('files.cpp','file_disk.cpp','disk_open.cpp')]
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
  before=load(preflight);captured=OUT/'producer-before-finalization.py'
  assert sha(captured)==before['input_sha256'][rel(Path(__file__))]
  comparable=dict(pins);comparable[rel(Path(__file__))]=sha(captured)
  assert before['input_sha256']==comparable and before['command']==command and before['tool_sha256']==tool_pins
  pins[rel(captured)]=sha(captured)
  compiled=load(OUT/('compile-'+args.attempt+'.receipt.json'))
 assert compiled['exit_code']==0,'Compile failed; receipt preserved'
 for src in sources:
  p=OUT/'dependencies'/(src.name+'.json');pins[rel(p)]=sha(p)
  for name in load(p)['Data']['Includes']:
   p=Path(name)
   if p.is_relative_to(ROOT):pins[rel(p)]=sha(p)
   else:tool_pins[str(p)]=sha(p)
 coff=module('coff307',ROOT/'scripts/research/build-v2-compile-corpus.py')
 symbols=coff.coff_symbols(objects[0]);assert len(symbols['defined'])==1 and 'application_pool_disk_slots_release_005918c0' in symbols['defined'][0]
 assert len(symbols['undefined'])==9 and not symbols['weak'] and not symbols['common']
 crt=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/lib/x86/libvcruntime.lib';tool_pins[str(crt)]=sha(crt)
 pins[rel(OUT/'producer-link002.py')]=sha(OUT/'producer-link002.py')
 pins[rel(OUT/'producer-link003.py')]=sha(OUT/'producer-link003.py')
 runtime_library=crt.with_name('libcmt.lib');tool_pins[str(runtime_library)]=sha(runtime_library)
 member=OUT/'libcmt-isa-5186cc.obj';library_bytes=runtime_library.read_bytes();member_header=library_bytes[0x5186cc:0x5186cc+60];member_size=int(member_header[48:58])
 assert member.read_bytes()==library_bytes[0x5186cc+60:0x5186cc+60+member_size]
 pins[rel(member)]=sha(member)
 runtime_origin=dict(library=rel(runtime_library),library_sha256=sha(runtime_library),member_offset=0x5186cc,member_header_hex=member_header.hex(),member_bytes=member_size,object=rel(member),object_sha256=sha(member),fixture_only=True,selection='dumpbin /LINKERMEMBER:1 confirms three actual memset CPU-state providers; extracted bytes compared to exact archive member')
 exe=OUT/'fixture.exe';link=[str(linker),'/nologo','/MACHINE:X86','/NODEFAULTLIB','/ENTRY:entry','/SUBSYSTEM:CONSOLE','/OUT:'+str(exe),*map(str,objects),str(kernel),str(crt),str(member)]
 name='link-'+args.link_attempt
 linked=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run(link,name)
 assert linked['exit_code']==0,'Link failed; receipt preserved'
 name='native-'+args.attempt
 native=load(OUT/(name+'.receipt.json')) if args.finalize_existing and (OUT/(name+'.receipt.json')).exists() else run([str(exe)],name)
 assert native['exit_code']==0,'Native comparison failed; receipt preserved'
 assert load(ROOT/native['log'])==dict(cases=48,failures=0)
 for p in [*objects,exe,*OUT.glob('*.receipt.json'),*OUT.glob('*.log'),*OUT.glob('before-*.json')]: pins[rel(p)]=sha(p)
 summary=dict(schema=2,kind='original-disk-slot-shutdown',original_sha256=SHA,va='005918c0',original_body_hex=body.hex(),original_body_bytes=181,game_objects=[dict(path=rel(objects[0]),sha256=sha(objects[0]))],game_source=rel(sources[0]),symbols=symbols,original_relocations=[{'offset': 1, 'next': 0, 'target': 7008388}, {'offset': 14, 'next': 0, 'target': 7008380}, {'offset': 21, 'next': 25, 'target': 5448368}, {'offset': 26, 'next': 0, 'target': 7008384}, {'offset': 44, 'next': 0, 'target': 7008388}, {'offset': 60, 'next': 64, 'target': 5841552}, {'offset': 68, 'next': 0, 'target': 7008384}, {'offset': 82, 'next': 0, 'target': 7008388}, {'offset': 88, 'next': 92, 'target': 5695040}, {'offset': 97, 'next': 0, 'target': 7008388}, {'offset': 106, 'next': 0, 'target': 7008252}, {'offset': 118, 'next': 122, 'target': 5448400}, {'offset': 136, 'next': 0, 'target': 7008380}, {'offset': 144, 'next': 0, 'target': 7008380}, {'offset': 150, 'next': 154, 'target': 5448384}, {'offset': 156, 'next': 0, 'target': 7008380}, {'offset': 162, 'next': 166, 'target': 5448400}, {'offset': 171, 'next': 0, 'target': 7008380}],endpoint_relocation=dict(offset=136,original_literal='006af07c',native_role='disk_mutexes_006aeffc+32; pure CMP end, not global mutex cell'),accepted_callee_vas=sorted(callee_vas),native_cases=48,native_exit=0,compiler_batches=1,selected_attempt=args.attempt,tool_sha256=tool_pins,input_sha256=pins,limits=['Callee algorithms are existing accepted owners; fixture providers are controlled only','Finite valid-memory states; not whole game or arbitrary fault/DF behavior acceptance'])
 summary['fixture_runtime_support']=runtime_origin
 summary['selected_link_attempt']=args.link_attempt
 summary=externalize(ROOT,summary,'input','raw')
 reader=ManifestReader(ROOT);reader.verify(summary,expected_hash_mode='raw');assert all(sha(p)==h for p,h in tool_pins.items())
 save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),original_body_bytes=181,native_cases=48,game_defined_symbols=1,game_undefined_symbols=9,input_manifest=summary['input_manifest']))
 print(json.dumps(dict(passed=True,native_cases=48,game_objects=1,undefined=symbols['undefined'])))
if __name__=='__main__': main()

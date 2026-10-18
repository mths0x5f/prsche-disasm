"""Verify the expanded single CRT lock prefix with the existing157 native/oracle fixtures."""
import argparse,hashlib,json,os,struct,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/292-stdio-lock-prefix'
OUT=ROOT/'local/experiments/v2-stdio-lock-prefix-292'
BASE=ROOT/'iterations/v2/001-original-recovery/source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--finalize-existing',action='store_true');args=parser.parse_args()
 assert not(RUN/'summary.json').exists(),'Completed292 immutable'
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'objects').mkdir(exist_ok=True);(OUT/'dependencies').mkdir(exist_ok=True)
 owner=BASE/'recovered/Porsche.exe/formatter_crt_runtime.cpp';header=BASE/'include/porsche/formatter_crt_runtime.hpp'
 preflight=load(RUN/'preflight.json')
 for p in preflight['patches']:assert sha(ROOT/p['path'])==p['after_sha256']
 original_probe=BASE/'recovered/formatter_crt_runtime_probe.cpp'
 model_path=ROOT/'scripts/research/verify-v2-formatter-crt-runtime.py'
 probe_text=original_probe.read_text(encoding='utf8');model_text=model_path.read_text(encoding='utf8')
 assert probe_text.count('i<26')==3 and model_text.count('range(26)')==3
 probe=OUT/'probe-prefix.cpp';model_copy=OUT/'oracle-prefix.py'
 if not args.finalize_existing:
  probe.write_text(probe_text.replace('i<26','i<48'),encoding='utf8',newline='\n')
  model_copy.write_text(model_text.replace('range(26)','range(48)'),encoding='utf8',newline='\n')
 assert probe.read_text(encoding='utf8')==probe_text.replace('i<26','i<48')
 assert model_copy.read_text(encoding='utf8')==model_text.replace('range(26)','range(48)')
 baseline=load(ROOT/'iterations/v2/001-original-recovery/runs/276-file-operation-reuse/summary.json')
 compiler=Path(baseline['compiler_command'][0]);linker=compiler.with_name('link.exe')
 roots=[ROOT/x if not Path(x).is_absolute() else Path(x) for x in baseline['results'][0]['include_directories']]
 vc=compiler.parents[3]/'lib/x86';sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
 sources=[owner,probe];objects=[OUT/'objects'/(p.stem+'.obj') for p in sources]
 pins={rel(p):sha(p) for p in [owner,header,original_probe,model_path,probe,model_copy,RUN/'preflight.json',compiler,linker,ROOT/'local/game/Porsche.exe']}
 command=[str(compiler),'/nologo','/c','/std:c++17','/MD','/O2','/Gy','/EHsc','/W4','/MP6','/sourceDependencies',str(OUT/'dependencies'),*[x for p in roots for x in ('/I',str(p))],'/Fo'+str(OUT/'objects')+os.sep,*map(str,sources)]
 def capture(command,name,stdin=None):
  rp=OUT/(name+'.receipt.json');lp=OUT/(name+'.log');assert not rp.exists() and not lp.exists()
  start=time.perf_counter();p=subprocess.run(command,cwd=ROOT,env={**os.environ,'CL':'','_CL_':'','INCLUDE':''},input=stdin,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  lp.write_bytes(p.stdout);d=dict(command=command,cwd=str(ROOT),exit_code=p.returncode,seconds=time.perf_counter()-start,log=rel(lp),log_sha256=sha(lp))
  if stdin is not None:d['stdin_sha256']=hashlib.sha256(stdin).hexdigest()
  save(rp,d);return d
 if not args.finalize_existing:
  assert not(OUT/'before.json').exists();(OUT/'producer-used.py').write_bytes(Path(__file__).read_bytes());pins[rel(OUT/'producer-used.py')]=sha(OUT/'producer-used.py')
  save(OUT/'before.json',dict(input_sha256=pins,compile_command=command));compiled=capture(command,'compile-001')
 else:
  before=load(OUT/'before.json');pins=before['input_sha256'];assert command==before['compile_command'];compiled=load(OUT/'compile-001.receipt.json')
 assert compiled['exit_code']==0,'Compile failed; receipt saved'
 exe=OUT/'prefix-probe.exe'
 link=[str(linker),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/OUT:'+str(exe),'/OPT:REF','/OPT:ICF','/LIBPATH:'+str(vc),'/LIBPATH:'+str(sdk/'um/x86'),'/LIBPATH:'+str(sdk/'ucrt/x86'),*map(str,objects),'kernel32.lib']
 link_name='link-001'
 if (OUT/'link-001.receipt.json').exists() and load(OUT/'link-001.receipt.json')['exit_code']!=0:link_name='link-002'
 if args.finalize_existing and (OUT/(link_name+'.receipt.json')).exists():linked=load(OUT/(link_name+'.receipt.json'))
 else:linked=capture(link,link_name)
 assert linked['exit_code']==0,'Link failed; receipt saved'
 rows=[]
 def case(op,index,b=0,race=0,fail=0):return (op,index,b,0,0,fail,0,0,0,race,0)
 for index in range(28,48):
  for b,race in ((1,0),(0,0),(0,1),(0,2)):rows.append(case('l',index,b,race))
  rows.append(case('u',index))
 for index in (1,9,13,17,25):rows.extend([case('l',index,1),case('u',index)])
 rows.extend([case('i',0),case('l',29,fail=-1)])
 inputs=('\n'.join(' '.join(map(str,x)) for x in rows)+'\n').encode();(OUT/'cases.txt').write_bytes(inputs)
 if args.finalize_existing and (OUT/'native-001.receipt.json').exists():native=load(OUT/'native-001.receipt.json')
 else:native=capture([str(exe)],'native-001',inputs)
 assert native['exit_code']==0,'Native failed; receipt saved'
 observed=[json.loads(x) for x in (OUT/'native-001.log').read_bytes().splitlines()];initial=observed.pop(0);assert len(observed)==len(rows)==112
 # Only three range constants differ in the old, independently tested oracle.
 namespace=dict(__name__='oracle292',__file__=str(model_path))
 exec(compile(model_copy.read_text(encoding='utf8'),str(model_copy),'exec'),namespace)
 binary=next(x for x in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if x['file']=='Porsche.exe')
 image=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==namespace['SHA']
 prefix=namespace['mapped'](image,binary,0x5e57a8,192)
 assert prefix.hex()==preflight['original_prefix_hex']
 actual_expected=[-1]*48
 for index,value in ((1,-100),(17,-124),(9,-148),(13,-172)):actual_expected[index]=value
 assert initial['locks']==actual_expected and initial['static']=='00'*96
 results=[]
 for row,actual in zip(rows,observed):
  expected=namespace['original'](namespace['make_uc'](image,binary),row)
  assert actual==expected,('native/original mismatch',row,[k for k in expected if actual.get(k)!=expected[k]])
  results.append(dict(input=row,state_sha256=hashlib.sha256(json.dumps(actual,sort_keys=True).encode()).hexdigest()))
 for src in sources:
  p=OUT/'dependencies'/(src.name+'.json');pins[rel(p)]=sha(p)
  for name in load(p)['Data']['Includes']:pins[rel(name)]=sha(name)
 assert all(sha(ROOT/p if not Path(p).is_absolute() else p)==h for p,h in pins.items()),'input drift'
 for p in [*objects,exe,*OUT.glob('*.log'),*OUT.glob('*.receipt.json'),OUT/'cases.txt']:pins[rel(p)]=sha(p)
 summary=dict(schema=1,kind='canonical-stdio-lock-prefix-expansion',original_sha256=namespace['SHA'],prefix_va='005e57a8',prefix_entries=48,prefix_bytes=192,total_table_extent_proven=False,source_patches=preflight['patches'],initial_all48_cells_native_equal_original=True,native_cpp_equal_original=True,native_cases=112,case_results=results,compiler_batches=1,compiled_tus=2,derived_fixture_changes=dict(native_i_less_than26_to48=3,oracle_range26_to48=3),input_sha256=pins,game_objects=[dict(path=rel(objects[0]),sha256=sha(objects[0]))],limitations=['Real OS locking/concurrency and full original CRT startup remain unproved','Frozen earlier source-pin reports describe their historical26-entry owner; current48-entry owner is proved here'])
 save(RUN/'summary.json',summary);save(RUN/'validation.json',dict(passed=True,summary_sha256=sha(RUN/'summary.json'),input_pins=len(pins),native_cases=112,initial_cells=48))
 print(json.dumps(dict(passed=True,native_cases=112,initial_cells=48,compiler_batches=1)))
if __name__=='__main__':main()

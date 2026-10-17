"""Independent read-only Run263 PE/source/COFF/oracle/dependency acceptance audit."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/263-canonical-heap-release'
OUT=ROOT/'local/experiments/v2-canonical-heap-release-263'
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 s=load(RUN/'summary.json');p=load(RUN/'preflight.json');o=load(OUT/'original-oracles.json')
 assert s['compiled_vas']==['00531f90','005322b0','005322c0'] and s['actual_compiler_batches']==1
 assert p['lock_wrappers'][0]['sdk']=='KERNEL32.dll!EnterCriticalSection' and p['lock_wrappers'][1]['sdk']=='KERNEL32.dll!LeaveCriticalSection'
 assert s['original_sha256']==p['original_sha256']==o['original_sha256']==sha(ROOT/'local/game/Porsche.exe')
 assert s['compiler_sha256']==sha(s['compiler_command'][0])
 for name,h in s['input_sha256'].items():
  q=Path(name);q=q if q.is_absolute() else ROOT/q
  assert sha(q)==h,('input SHA',name)
 original=(ROOT/'local/game/Porsche.exe').read_bytes();pe=struct.unpack_from('<I',original,0x3c)[0]
 assert original[pe:pe+4]==b'PE\0\0'
 n=struct.unpack_from('<H',original,pe+6)[0];oh=struct.unpack_from('<H',original,pe+20)[0]
 secs=[]
 for i in range(n):
  q=pe+24+oh+i*40;_,rva,size,raw=struct.unpack_from('<IIII',original,q+8);secs.append((rva,raw,size))
 def pebytes(va,length):
  rva=va-0x400000;v,raw,size=next((v,r,z) for v,r,z in secs if v<=rva and rva+length<=v+z)
  return original[raw+rva-v:raw+rva-v+length]
 indexed={x['entry_va']:x for x in map(json.loads,(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 lengths={'00531f90':278,'005322b0':12,'005322c0':12}
 for va,length in lengths.items():
  assert indexed[va]['body_bytes']==length
  start=int(va,16);end=start+length;seen=0
  for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
   if len(line)<12:continue
   try:pc=int(line[:8],16)
   except ValueError:continue
   if start<=pc<end:
    item=line.split(None,2);raw=bytes.fromhex(item[1]);assert pebytes(pc,len(raw))==raw;seen+=len(raw)
  assert seen==length,(va,seen)
 coff=mod('coff263audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 actual_defined=[];actual_undefined=[]
 receipt=load(OUT/'compile.execution.json');assert receipt['exit_code']==0 and receipt['command']==s['compiler_command']
 observed=[Path(receipt['command'][i+1]).resolve() for i,t in enumerate(receipt['command'][:-1]) if t=='/I'];assert len(observed)==5
 for row in s['results']:
  va=row['va'];fragment=s['canonical_fragments'][va];source=(ROOT/fragment['source']).read_bytes();generated=(ROOT/row['generated_source']).read_bytes()
  prefix=source[:source.index(b'namespace porsche {')]
  rebuilt=prefix+b'namespace porsche {\n'
  for piece in fragment['slices']:
   raw=source[piece['offset']:piece['offset']+piece['length']]
   assert hashlib.sha256(raw).hexdigest()==piece['sha256']
   rebuilt+=raw+b'\n'
  assert generated==rebuilt+b'}\n'
  declared=[(Path(x) if Path(x).is_absolute() else ROOT/x).resolve() for x in row['include_directories']]
  assert declared==observed and row['compiler_command']==receipt['command']
  dep=load(ROOT/row['source_dependencies']);assert dep['Version']=='1.2' and Path(dep['Data']['Source']).resolve()==(ROOT/row['generated_source']).resolve()
  for name in dep['Data']['Includes']:
   h=Path(name).resolve();assert any(h.is_relative_to(root) for root in observed)
   pin=next((v for k,v in s['input_sha256'].items() if Path(k).name.lower()==h.name.lower() and (Path(k) if Path(k).is_absolute() else ROOT/k).resolve()==h),None)
   assert pin==sha(h),name
  obj=ROOT/row['object'];assert sha(obj)==row['object_sha256']
  symbols=coff.coff_symbols(obj);assert symbols==row['symbols'] and len(symbols['defined'])==1
  actual_defined+=symbols['defined'];actual_undefined+=symbols['undefined']
 assert set(actual_defined)=={'?free_00531f90@porsche@@YAIPAX@Z','?heap_enter_005322b0@porsche@@YAXPAX@Z','?heap_leave_005322c0@porsche@@YAXPAX@Z'}
 assert set(actual_undefined)-set(actual_defined)=={'?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A','?platform_enter_critical_section@porsche@@YGXPAX@Z','?platform_leave_critical_section@porsche@@YGXPAX@Z'}
 assert s['native_fixture']['free_cutpoints']==sum(len(q['frees']) for q in o['cases'])==4
 assert s['native_fixture']['arena_bytes_compared']==2048 and all(q['return_value']==1 for c in o['cases'] for q in c['frees'])
 assert sha(OUT/'native-fixture.exe')==s['native_fixture']['executable_sha256']
 assert load(OUT/'fixture-link.execution.json')['exit_code']==0 and load(OUT/'fixture-native.execution.json')['exit_code']==0
 verdict=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),script_sha256=sha(__file__),pass_all=True,original_sha256=s['original_sha256'],selected_vas=s['compiled_vas'],pe_bytes_verified=302,exact_canonical_fragments=True,actual_coff_symbols=True,actual_source_dependencies=True,observed_include_order=True,bounded_original_free_cutpoints=4,native_exit=0,compiler_invocations=1,production_ready=False)
 (RUN/'validation.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(verdict))
if __name__=='__main__':main()

"""Independent read-only audit of the 266 raw heap-free link contract."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/266-heap-free-binding'
OUT=ROOT/'local/experiments/v2-heap-free-binding-266'
RAW='?FUN_00531f90@@YAIH@Z';CAN='?free_00531f90@porsche@@YAIPAX@Z'
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 s=load(RUN/'summary.json');pre=load(RUN/'preflight.json')
 assert s['kind']=='proven-link-contract' and s['new_function_count']==0 and len(s['support_objects'])==len(s['aliases'])==1
 assert s['aliases'][0]['from']==RAW and s['aliases'][0]['to']==CAN and pre['alias_approved']
 assert s['actual_compiler_batches']==2 and s['first_compile_failure']['exit_code']!=0
 assert s['compiler_sha256']==sha(s['compiler_command'][0])
 for name,h in s['input_sha256'].items():
  p=Path(name);p=p if p.is_absolute() else ROOT/p
  assert sha(p)==h,('pin',name)
 assert s['ordinary_summary_sha256']==sha(ROOT/s['ordinary_summary'])
 original=(ROOT/'local/game/Porsche.exe').read_bytes();assert sha(ROOT/'local/game/Porsche.exe')==s['original_sha256']
 pe=struct.unpack_from('<I',original,0x3c)[0];assert original[pe:pe+4]==b'PE\0\0'
 n=struct.unpack_from('<H',original,pe+6)[0];oh=struct.unpack_from('<H',original,pe+20)[0]
 rva=0x531f90-0x400000
 for i in range(n):
  q=pe+24+oh+i*40;_,v,z,r=struct.unpack_from('<IIII',original,q+8)
  if v<=rva and rva+278<=v+z:body=original[r+rva-v:r+rva-v+278];break
 else:raise AssertionError('body section')
 assert len(body)==278 and body[-9:]==bytes.fromhex('5eb8010000005d59c3')
 indexed={x['entry_va']:x for x in map(json.loads,(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 assert indexed['00531f90']['body_bytes']==278
 asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines();count=0
 for line in asm:
  if len(line)<12:continue
  try:pc=int(line[:8],16)
  except ValueError:continue
  if 0x531f90<=pc<0x5320a6:
   raw=bytes.fromhex(line.split(None,2)[1]);assert body[pc-0x531f90:pc-0x531f90+len(raw)]==raw;count+=len(raw)
 assert count==278
 coff=mod('coff266audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 parse=mod('parse266audit',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 parser=mod('scalar266audit',ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
 cap=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
 assert len(pre['consumers'])==10
 for c in pre['consumers']:
  obj=ROOT/c['object'];src=ROOT/c['source'];assert sha(obj)==c['object_sha256'] and sha(src)==c['source_sha256']
  assert RAW in coff.coff_symbols(obj)['undefined'] and 'undefined4 FUN_00531f90(int param_1);' in src.read_text(errors='replace')
  body,relocs=parse.coff_function(obj,c['defined']);r=[x for x in relocs if x['symbol']==RAW];assert r==c['raw_relocations'] and len(r)==1
  ins=list(cap.disasm(body,0));ix=next(i for i,x in enumerate(ins) if x.address+1==r[0]['offset'])
  assert ins[ix-1].mnemonic=='push' and ins[ix].bytes[0]==0xe8 and ins[ix+1].bytes==bytes.fromhex('83c404')
 command=load(OUT/'compile.execution.json');assert command['exit_code']==0 and command['command']==s['compiler_command']
 roots=[Path(command['command'][i+1]).resolve() for i,x in enumerate(command['command'][:-1]) if x=='/I'];assert len(roots)==5
 support=s['support_objects'][0]
 declared=[(Path(x) if Path(x).is_absolute() else ROOT/x).resolve() for x in support['include_directories']]
 assert declared==roots and support['compiler_command']==command['command'] and support['compiler_execution_receipt']=='local/experiments/v2-heap-free-binding-266/compile.execution.json'
 assert sha(ROOT/support['source_dependencies'])==support['source_dependencies_sha256']
 for source in (OUT/'binding.cpp',OUT/'native-fixture.cpp'):
  dep=load(OUT/'dependencies'/(source.name+'.json'));assert dep['Version']=='1.2' and Path(dep['Data']['Source']).resolve()==source
  for name in dep['Data']['Includes']:
   p=Path(name).resolve();assert any(p.is_relative_to(q) for q in roots)
   assert any(sha(p)==h for k,h in s['input_sha256'].items() if (Path(k) if Path(k).is_absolute() else ROOT/k).resolve()==p)
  assert b'\r\n' not in source.read_bytes()
 obj=ROOT/support['object'];assert sha(obj)==support['object_sha256']
 assert coff.coff_symbols(obj)==support['symbols'] and not any(support['symbols'].values())
 parsed=parser.coff(obj);sec=next(q for q in parsed['sections'] if q['name']=='.drectve')
 actual=parsed['bytes'][sec['raw']:sec['raw']+sec['size']].decode('ascii').strip()
 assert actual==support['directive']==s['aliases'][0]['directive']=='/alternatename:'+RAW+'='+CAN
 assert load(OUT/'first-compile.execution.json')['exit_code']!=0
 assert load(OUT/'fixture-link.execution.json')['exit_code']==load(OUT/'fixture-native.execution.json')['exit_code']==0
 assert s['native_fixture']['raw_canonical_identity'] and s['native_fixture']['full_EAX']==1 and s['native_fixture']['relative_ESP']
 assert sha(OUT/'native-fixture.exe')==s['native_fixture']['executable_sha256']
 verdict=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),script_sha256=sha(__file__),pass_all=True,original_sha256=s['original_sha256'],all_actual_consumer_COFFs=10)
 verdict.update(original_pe_bytes=278,original_RET_pop_bytes=0,full_EAX=1,exact_native_directive=True,native_exit=0,compiler_attempts=2,game_coffs_reused=3,production_ready=False)
 (RUN/'validation.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(verdict))
if __name__=='__main__':main()

"""Read-only acceptance audit of Run259 PE, exact source, COFF, dependencies and receipts."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/259-canonical-reuse'
OUT=ROOT/'local/experiments/v2-canonical-reuse-259'
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def main():
 s=json.loads((RUN/'summary.json').read_bytes());b=json.loads((RUN/'bindings/summary.json').read_bytes());proof=json.loads((RUN/'proof-before-compile.json').read_bytes())
 assert s['compiled_vas']==['0059f050','005a66a7'] and s['actual_compiler_batches']==4 and s['recompilations']==3
 assert s['compiler_sha256']==b['compiler_sha256']==sha(s['compiler_command'][0])
 for name,digest in s['input_sha256'].items():
  p=Path(name);p=p if p.is_absolute() else ROOT/p
  assert p.exists() and sha(p)==digest,(name,'pin')
 assert b['input_sha256'][rel(RUN/'summary.json')]==sha(RUN/'summary.json')
 assert b['ordinary_summary_sha256']==sha(RUN/'summary.json')
 image=(ROOT/'local/game/Porsche.exe').read_bytes();assert sha(ROOT/'local/game/Porsche.exe')==s['original_sha256']
 pe_off=struct.unpack_from('<I',image,0x3c)[0];assert image[pe_off:pe_off+4]==b'PE\0\0'
 sections=[];n=struct.unpack_from('<H',image,pe_off+6)[0];opsize=struct.unpack_from('<H',image,pe_off+20)[0]
 for i in range(n):
  q=pe_off+24+opsize+i*40;size,va,rawsize,raw=struct.unpack_from('<IIII',image,q+8);sections.append((va,raw,rawsize))
 def get(va,length):
  va-=0x400000
  v,r,z=next((v,r,z) for v,r,z in sections if v<=va and va+length<=v+z)
  return image[r+va-v:r+va-v+length]
 for va,instructions in proof['original_instructions'].items():
  assert va in s['compiled_vas']
  for item in instructions:
   raw=bytes.fromhex(item['bytes']);assert get(int(item['va'],16),len(raw))==raw
 for va,parts in proof['canonical_fragments'].items():
  canonical=(ROOT/parts['canonical_source']).read_bytes();generated=(OUT/(va+'.cpp')).read_bytes()
  joined=b''
  for part in parts['parts']:
   raw=part['text'].encode('utf8');joined+=raw
   if part['kind']=='canonical_slice':assert canonical[part['offset']:part['offset']+part['length']]==raw and hashlib.sha256(raw).hexdigest()==part['sha256']
  assert generated==joined
 coff=mod('coff259audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 parser=mod('parse259audit',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 for row in s['results']:
  command=json.loads((ROOT/row['compiler_execution_receipt']).read_bytes())['command']
  assert row['compiler_command']==command
  observed=[Path(command[i+1]).resolve() for i,item in enumerate(command[:-1]) if item=='/I']
  declared=[(Path(name) if Path(name).is_absolute() else ROOT/name).resolve() for name in row['include_directories']]
  assert declared==observed and len(observed)==5
  obj=ROOT/row['object'];assert sha(obj)==row['object_sha256']
  assert coff.coff_symbols(obj)==row['symbols']
  dep=json.loads((ROOT/row['source_dependencies']).read_bytes())
  assert dep['Version']=='1.2' and Path(dep['Data']['Source']).resolve()==(ROOT/row['generated_source']).resolve()
  for include in dep['Data']['Includes']:
   p=Path(include);key=rel(p) if p.is_relative_to(ROOT) else p.as_posix()
   match=next((v for k,v in s['input_sha256'].items() if k.lower()==key.lower()),None)
   assert match is not None and sha(p)==match,key
  assert row['defined_external_symbols']==[next(a['to'] for a in b['aliases'] if a['va']==row['va'])]
 for a in b['aliases']:
  support=next(r for r in b['support_objects'] if r['id']==a['support_object_id'])
  obj=ROOT/support['object'];parsed=mod('scalar259audit',RUN.parent/'226-writable-scalar-storage/audit.py').coff(obj)
  section=next(q for q in parsed['sections'] if q['name']=='.drectve')
  assert parsed['bytes'][section['raw']:section['raw']+section['size']].decode('ascii').strip()==a['directive']
  assert coff.coff_symbols(obj)['defined']==[] and coff.coff_symbols(obj)['undefined']==[]
 fixture=OUT/'objects/native-fixture.obj'
 for oracle in s['oracle']:
  body,relocs=parser.coff_function(fixture,oracle['symbol']);va=oracle['va'];expected=bytearray.fromhex(''.join(x['bytes'] for x in proof['original_instructions'][va]))
  offset=10 if va=='0059f050' else 1;expected[offset:offset+4]=bytes(4)
  assert body==bytes(expected) and len(relocs)==1 and relocs[0]['offset']==offset
 assert s['deferred'][0]['original_va']=='005925d0' and 'signed char promotion' in s['deferred'][0]['reason'].lower()
 assert s['fixture']['native_exit_code']==0 and json.loads((OUT/'fixture-native.execution.json').read_bytes())['exit_code']==0
 assert json.loads((OUT/'first-compile.execution.json').read_bytes())['exit_code']!=0
 assert json.loads((OUT/'first-fixture-link.execution.json').read_bytes())['exit_code']!=0
 assert json.loads((OUT/'first-fixture-native.execution.json').read_bytes())['exit_code']==3221225477
 verdict=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),script_sha256=sha(Path(__file__)),pass_all=True,selected_vas=s['compiled_vas'],original_sha256=s['original_sha256'],exact_pe=True,exact_canonical_fragments=True,actual_coff_symbols=True,source_dependencies=True,observed_include_order=True,exact_oracle_bodies=True,fixture_exit=0,compiler_invocations=4,primary_failed_receipts_preserved=True,stale_native_receipt_overwritten=True,production_ready=False)
 (RUN/'validation.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf8',newline='\n')
 support={**verdict,'summary_sha256':sha(RUN/'bindings/summary.json'),'ordinary_summary_sha256':sha(RUN/'summary.json')}
 (RUN/'bindings/validation.json').write_text(json.dumps(support,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(verdict))
if __name__=='__main__':main()

"""Independent read-only PE/COFF/source/receipt audit of Run276."""
import hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/276-file-operation-reuse'
OUT=ROOT/'local/experiments/v2-file-operation-reuse-276'
RAW=('?FUN_00568200@@YAIH@Z','?FUN_005682a0@@YAHIEII@Z')
CAN=('?operation_queue_00568200@porsche@@YAIPAUFileOperation@1@@Z','?operation_allocate_005682a0@porsche@@YAPAUFileOperation@1@IEPAXI@Z')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_bytes())
def path(s):
 p=Path(s);return p if p.is_absolute() else ROOT/p
def mod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 s=get(RUN/'summary.json');b=get(RUN/'bindings/summary.json');p=get(RUN/'preflight.json');o=get(OUT/'original-oracles.json')
 assert s['kind']=='canonical-body-reuse-batch' and b['kind']=='proven-link-contract'
 assert s['objects_compiled']==s['real_coff_objects']==2 and s['compiled_vas']==['00568200','005682a0']
 assert s['new_distinct_function_VAs']==2 and b['new_function_count']==0
 assert len(b['support_objects'])==1 and len(b['aliases'])==2
 assert s['original_sha256']==p['original_sha256']==o['original_sha256']==b['original_sha256']
 assert sha(RUN/'preflight.json')==o['preflight_sha256']
 assert b['ordinary_summary_sha256']==sha(RUN/'summary.json')
 assert s['original_oracles_sha256']==sha(OUT/'original-oracles.json')
 assert sha(path(p['source']))==p['source_sha256'] and sha(path(p['header']))==p['header_sha256']
 previous=get(path(p['prior_oracle']))
 assert previous['native_cpp_equal_original_x86'] and previous['source_sha256'][p['source']]==p['source_sha256']
 assert o['oracle_script_sha256']==sha(ROOT/'scripts/research/oracle-v2-file-operation-reuse-276.py')
 assert len(o['cases'])==4 and {c['kind'] for c in o['cases']}=={'queue','allocate'}
 assert sum(len(c['events']) for c in o['cases'])==11
 assert s['native_fixture']['original_cutpoints']==4 and s['native_fixture']['canonical_and_raw_calls']==8
 for report in (s,b):
  for name,h in report['input_sha256'].items():assert sha(path(name))==h,name
 image=path('local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==s['original_sha256']
 pe=struct.unpack_from('<I',image,0x3c)[0];assert image[pe:pe+4]==b'PE\0\0'
 n=struct.unpack_from('<H',image,pe+6)[0];oh=struct.unpack_from('<H',image,pe+20)[0]
 for target in p['targets']:
  rva=int(target['va'],16)-0x400000;size=target['size'];found=[]
  for i in range(n):
   q=pe+24+oh+i*40;vs,va,rs,rp=struct.unpack_from('<IIII',image,q+8)
   if va<=rva and rva+size<=va+rs:found.append(image[rp+rva-va:rp+rva-va+size])
  assert len(found)==1 and hashlib.sha256(found[0]).hexdigest()==target['sha256']
  assert found[0][-1]==0xc3 and target['original_ret_pop']==0
 coff=mod('coff276audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
 parser=mod('parse276audit',ROOT/'iterations/v2/001-original-recovery/runs/226-writable-scalar-storage/audit.py')
 functions=mod('fn276audit',ROOT/'scripts/research/audit-v2-nested-calls-229.py')
 command=s['compiler_command'];receipt=get(path(s['compiler_execution_receipt']))
 assert receipt['command']==command and receipt['exit_code']==0 and '/MP6' in command
 roots=[str(path(x).resolve()) for x in s['results'][0]['include_directories']]
 assert roots==[command[i+1] for i,x in enumerate(command[:-1]) if x=='/I'] and len(roots)==5
 for index,row in enumerate(s['results']):
  va=row['va'];assert va==p['targets'][index]['va'] and row['canonical_reuse']
  assert row['symbols']==coff.coff_symbols(path(row['object']))
  assert row['symbols']['defined']==[CAN[index]]
  assert sha(path(row['object']))==row['object_sha256'] and sha(path(row['generated_source']))==row['generated_source_sha256']
  assert sha(path(row['source_dependencies']))==row['source_dependencies_sha256']
  assert row['include_directories']==s['results'][0]['include_directories'] and row['compiler_command']==command
  for name,h in row['dependency_sha256'].items():assert sha(path(name))==h,name
  chunks=[];data=path(p['source']).read_bytes()
  for part in s['canonical_fragments'][va]['slices']:
   blob=data[part['offset']:part['offset']+part['length']]
   assert hashlib.sha256(blob).hexdigest()==part['sha256'];chunks.append(blob)
  assert path(row['generated_source']).read_bytes()==b'#include "porsche/files.hpp"\nnamespace porsche {\n'+b''.join(x+b'\n' for x in chunks)+b'}\n'
  assert row['owned_warning_count']==row['owned_error_count']==0
 binding=b['support_objects'][0]
 assert binding['symbols']==coff.coff_symbols(path(binding['object']))
 assert all(not vals for vals in binding['symbols'].values())
 parsed=parser.coff(path(binding['object']))
 ds=next(x for x in parsed['sections'] if x['name']=='.drectve')
 directive=parsed['bytes'][ds['raw']:ds['raw']+ds['size']].decode('ascii').strip()
 assert all(a['directive'] in directive for a in b['aliases'])
 assert all(not(x['chars']&0x20000000) for x in parsed['sections'])
 assert sorted(binding['directives'])==sorted(a['directive'] for a in b['aliases'])
 assert binding['include_directories']==s['results'][0]['include_directories'] and binding['compiler_command']==command
 for name,h in binding['dependency_sha256'].items():assert sha(path(name))==h
 for consumer in p['consumers']:
  assert sha(path(consumer['object']))==consumer['object_sha256']
  code,refs=functions.coff_function(path(consumer['object']),consumer['defined'])
  for site in consumer['sites']:
   ref=site['relocation'];assert ref in refs and ref['type']==20
   assert code[site['call_offset']]==0xe8 and ref['offset']==site['call_offset']+1
   assert site['caller_pop_bytes']==(4 if site['target']=='00568200' else 16)
 for alias,raw,can in zip(b['aliases'],RAW,CAN):
  assert alias['from']==raw and alias['to']==can and alias['support_object_id']==binding['id']
 for name in ('compile-001','fixture-link-001','fixture-native-001'):
  r=get(OUT/(name+'.execution.json'))
  assert r['exit_code']==0 and sha(path(r['log']))==r['log_sha256']
 assert sha(path(s['native_fixture']['executable']))==s['native_fixture']['executable_sha256']
 validation=dict(schema=1,status='pass',summary_sha256=sha(RUN/'summary.json'),audit_script_sha256=sha(__file__),original_sha256=s['original_sha256'],actual_PE_spans=2,actual_COFF_bodies=2,actual_raw_call_sites=8,oracle_cases=4,native_calls=8,native_exit_code=0,full_source_dependency_closure=True,compile_batches=1)
 (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
 bv={**validation,'summary_sha256':sha(RUN/'bindings/summary.json'),'ordinary_summary_sha256':sha(RUN/'summary.json')}
 (RUN/'bindings/validation.json').write_text(json.dumps(bv,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(status='pass',bodies=2,aliases=2,call_sites=8,original_cutpoints=4,native_exit=0)))
if __name__=='__main__':main()

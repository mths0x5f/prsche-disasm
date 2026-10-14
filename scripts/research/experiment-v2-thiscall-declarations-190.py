"""Retry only frozen187 failed leaves with exact184 per-TU declarations."""
from __future__ import annotations
from collections import Counter
import hashlib,importlib.util,json,os,re,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/190-thiscall-declaration-delta'
OUT=ROOT/'local/experiments/v2-thiscall-declarations-190'
PRIOR=ROOT/'iterations/v2/001-original-recovery/runs/187-thiscall-leaf-candidates/summary.json'
PRIOR_VALIDATION=PRIOR.parent/'validation.json'
DECLARATIONS=ROOT/'local/experiments/v2-declaration-compat-184/full/audit.json'
spec=importlib.util.spec_from_file_location('leaves187',ROOT/'scripts/research/experiment-v2-thiscall-leaves-187.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()

def verify_row(row):
 assert sha(ROOT/row['generated_source'])==row['generated_source_sha256']
 for name,expected in row['dependency_sha256'].items():assert sha(ROOT/name)==expected
 if row['compiled']:
  obj=ROOT/row['object'];assert sha(obj)==row['object_sha256']
  assert base.coff_symbols(obj)['defined_external_symbols']==row['defined_external_symbols']

def main():
 start=time.perf_counter();RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 sources=OUT/'sources';objects=OUT/'objects';logs=OUT/'logs'
 for p in (sources,objects,logs):p.mkdir(exist_ok=True)
 prior=json.loads(PRIOR.read_bytes());validation=json.loads(PRIOR_VALIDATION.read_bytes());declarations=json.loads(DECLARATIONS.read_bytes())
 assert validation['summary_sha256']==sha(PRIOR) and validation['objects_pass'] and validation['actual_original_pe_bytes_pass']
 assert prior['original_sha256']==declarations['original_sha256']==base.abi.SHA
 assert prior['real_coff_objects']==127 and prior['compiler_failures']==32 and prior['jobs']==6
 assert prior['compiler_sha256']==sha(base.abi.COMPILER)
 assert not os.environ.get('CL') and not os.environ.get('_CL_'),'Unrecorded compiler environment options are not allowed'
 pins={Path(__file__).resolve():sha(Path(__file__)),PRIOR:sha(PRIOR),PRIOR_VALIDATION:sha(PRIOR_VALIDATION),DECLARATIONS:sha(DECLARATIONS),Path(spec.origin):sha(Path(spec.origin))}
 for name,expected in prior['input_sha256'].items():
  path=ROOT/name;assert sha(path)==expected,('prior input changed',name);pins[path]=expected
 flags=None
 for batch in prior['batches'].values():
  rsp=ROOT/batch['response_file'];assert sha(rsp)==batch['response_file_sha256'];pins[rsp]=sha(rsp)
  options=[line.strip('"') for line in rsp.read_text(encoding='utf-8-sig').splitlines() if line.startswith('"/')]
  normalized=[o for o in options if not o.startswith('/Fo')]
  if flags is None:flags=normalized
  else:assert flags==normalized,'187 compiler flags differ across batches'
 assert '/MP6' in flags and '/O2' in flags and '/std:c++17' in flags
 declaration_rows={r['va']:r for r in declarations['results']};results=[];retry=[]
 for old in prior['results']:
  verify_row(old);row=json.loads(json.dumps(old));row['prior_generated_source']=old['generated_source'];row['prior_generated_source_sha256']=old['generated_source_sha256']
  if old['compiled']:
   row['cache_reused']=True;row['reuse_reason']='Exact187 source/header/object/compiler/flags and frozen186 ABI proof verified';results.append(row);continue
  va=old['va'];d=declaration_rows[va];source184=Path(d['generated_source']);assert sha(source184)==d['generated_source_sha256'];pins[source184]=sha(source184)
  marker='/* VA '+va+' */'
  body184=source184.read_text().split(marker,1)[1];body183=(ROOT/old['baseline_generated_source']).read_text().split(marker,1)[1]
  assert body184==body183,('184 body changed',va)
  assert d.get('forced_headers',[])==old['forced_headers'],('forced-header ABI context changed',va)
  text=(ROOT/old['generated_source']).read_text();header=d.get('declaration_header');row['declaration_header']=None
  if header:
   header=Path(header);assert sha(header)==d['declaration_header_sha256'];pins[header]=sha(header)
   scalar=re.search(r'^#include\s+"[^"]*ghidra-scalars-syntax-only\.h"[^\n]*\n',text,flags=re.M);assert scalar,va
   include='#include "'+header.as_posix()+'"\n';assert include not in text
   text=text[:scalar.end()]+include+text[scalar.end():]
   row['declaration_header']=relative(header);row['declaration_header_sha256']=sha(header)
   # Traverse the actual native declaration include closure; preserve scalar/helper order.
   row['dependency_sha256'].update(base.headers_closure([header],pins))
  source=sources/(va+'.cpp');source.write_text(text,encoding='utf8',newline='\n');obj=objects/(va+'.obj')
  if obj.exists():obj.unlink() # Known190 output only; never alter frozen187 objects.
  row['generated_source']=relative(source);row['generated_source_sha256']=sha(source);row['object']=relative(obj);row['cache_reused']=False
  row['source_changed']=row['generated_source_sha256']!=old['generated_source_sha256'];row['compiled']=False;row.pop('failure',None)
  retry.append(row);results.append(row)
 assert len(retry)==32 and sum(r['cache_reused'] for r in results)==127
 # One actual /MP6 command. Only output location changes from frozen187 flags.
 rsp=logs/'retry-32.rsp';log=logs/'retry-32.log';options=flags+['/Fo'+objects.as_posix()+'/']
 rsp.write_text('\n'.join('"'+s+'"' for s in options+[str(ROOT/r['generated_source']) for r in retry]),encoding='utf-8-sig',newline='\n')
 before=time.perf_counter();p=subprocess.run([str(base.abi.COMPILER),'@'+str(rsp)],cwd=OUT,capture_output=True,encoding='utf8',errors='replace',env=base.abi.ENV,timeout=180)
 log.write_text(p.stdout+p.stderr,encoding='utf8',newline='\n');elapsed_compile=time.perf_counter()-before
 errors={};codes=Counter()
 for m in re.finditer(r'porsche_method_([0-9a-f]{8})\((\d+),(\d+)\):\s*(fatal error|error|warning)\s+(C\d+):\s*(.*)',p.stdout+p.stderr):
  va,line,column,severity,code,message=m.groups();errors.setdefault(va,[]).append({'line':int(line),'column':int(column),'severity':severity,'code':code,'message':message});codes[code]+=1
 for row in retry:
  obj=ROOT/row['object'];row['compiled']=obj.exists();row['compiler_exit_code']=0 if obj.exists() else None;row['diagnostics']=errors.get(row['va'],[])
  if obj.exists():
   row['object_sha256']=sha(obj);row['object_bytes']=obj.stat().st_size;row.update(base.coff_symbols(obj));sections=base.abi.text_sections(obj);row['native_text_sections']=sections
   row['exact_original_body_bytes_match']=any(s['relocations']==0 and s['bytes']==row['original_instruction_bytes_hex'] for s in sections)
   assert any('Thiscall_'+row['va'] in s for s in row['defined_external_symbols'])
  else:row['failure']='Exact184 declaration delta still produces no COFF; no body/ABI/type/storage substitution supplied'
 for row in results:verify_row(row)
 for path,expected in pins.items():assert sha(path)==expected,('input changed',path)
 old_by_va={r['va']:r for r in prior['results']}
 for row in results:
  old=old_by_va[row['va']]
  assert row['original_contract']==old['original_contract'] and row['method_contract']==old['method_contract']
  if row['cache_reused']:assert row['object_sha256']==old['object_sha256'] and row['exact_original_body_bytes_match']==old['exact_original_body_bytes_match']
 new=[r for r in retry if r['compiled']];undefined=Counter(s for r in results if r['compiled'] for s in r['undefined_external_symbols'])
 report={'schema':1,'module':'Porsche.exe','original_sha256':base.abi.SHA,'prior_summary':relative(PRIOR),'prior_summary_sha256':sha(PRIOR),'prior_validation_sha256':sha(PRIOR_VALIDATION),'declarations_audit':relative(DECLARATIONS),'declarations_audit_sha256':sha(DECLARATIONS),'input_sha256':{relative(path):expected for path,expected in sorted(pins.items(),key=lambda x:str(x[0]))},'compiler_sha256':sha(base.abi.COMPILER),'compiler_flags':flags,'compiler_environment_options':{'CL':os.environ.get('CL'),'_CL_':os.environ.get('_CL_')},'selected_unique_vas':len(results),'reused_objects':127,'retried_failed_tus':32,'retried_tus_with_header':sum(bool(r['declaration_header']) for r in retry),'actual_compiler_batches':1,'compiler_batch_exit_code':p.returncode,'new_objects':len(new),'new_object_vas':[r['va'] for r in new],'real_coff_objects':127+len(new),'remaining_compiler_failures':32-len(new),'preserved_cached_body_byte_matches':sum(r.get('exact_original_body_bytes_match',False) for r in results if r['cache_reused']),'exact_original_body_byte_matches':sum(r.get('exact_original_body_bytes_match',False) for r in results),'undefined_unique_symbols':len(undefined),'undefined_references':sum(undefined.values()),'undefined_symbols':dict(undefined),'diagnostic_codes':dict(codes),'compiler_log':relative(log),'compiler_log_sha256':sha(log),'compiler_response':relative(rsp),'compiler_response_sha256':sha(rsp),'compile_seconds':round(elapsed_compile,3),'elapsed_seconds':round(time.perf_counter()-start,3),'results':results,'boundary':'Only exact184 memory declaration headers added to frozen187 failed leaves;127 guarded actualCOFF reused,32 retried, no new body/ABI/caller/registry/storage changes, no original bytes executed or new native oracles'}
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps({k:report[k] for k in ('reused_objects','retried_failed_tus','retried_tus_with_header','new_objects','real_coff_objects','remaining_compiler_failures','preserved_cached_body_byte_matches','undefined_unique_symbols','undefined_references','elapsed_seconds')},indent=2))

if __name__=='__main__':main()

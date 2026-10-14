"""Read-only validation of the guarded187 reuse and exact184 include delta."""
import hashlib,importlib.util,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5];RUN=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('delta190',ROOT/'scripts/research/experiment-v2-thiscall-declarations-190.py');delta=importlib.util.module_from_spec(spec);spec.loader.exec_module(delta)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
summary=RUN/'summary.json';s=json.loads(summary.read_bytes());prior=json.loads((ROOT/s['prior_summary']).read_bytes())
assert not b'\r\n' in summary.read_bytes()
assert sha(ROOT/s['prior_summary'])==s['prior_summary_sha256']
assert sha(ROOT/s['declarations_audit'])==s['declarations_audit_sha256']
for name,expected in s['input_sha256'].items():assert sha(ROOT/name)==expected,('input changed',name)
assert sha(ROOT/s['compiler_log'])==s['compiler_log_sha256'] and sha(ROOT/s['compiler_response'])==s['compiler_response_sha256']
old_by_va={r['va']:r for r in prior['results']};reused=0;retried=0;new=0;cached_matches=0;undefined=Counter();failures=[]
assert len({r['va'] for r in s['results']})==159
for r in s['results']:
 delta.verify_row(r);old=old_by_va[r['va']]
 assert r['original_contract']==old['original_contract'] and r['method_contract']==old['method_contract']
 assert r['original_instruction_bytes_hex']==old['original_instruction_bytes_hex'] and r['baseline_generated_source_sha256']==old['baseline_generated_source_sha256']
 if r['cache_reused']:
  assert old['compiled'] and r['object_sha256']==old['object_sha256'] and r['generated_source_sha256']==old['generated_source_sha256']
  assert r['native_text_sections']==old['native_text_sections']
  reused+=1;cached_matches+=r['exact_original_body_bytes_match']
 else:
  assert not old['compiled'];retried+=1
  text=(ROOT/old['generated_source']).read_text()
  if r['declaration_header']:
   header=ROOT/r['declaration_header'];assert sha(header)==r['declaration_header_sha256']
   scalar=re.search(r'^#include\s+"[^"]*ghidra-scalars-syntax-only\.h"[^\n]*\n',text,flags=re.M);assert scalar
   text=text[:scalar.end()]+'#include "'+header.as_posix()+'"\n'+text[scalar.end():]
  source=ROOT/r['generated_source'];assert source.read_text()==text,('non-header/body change',r['va'])
  assert b'\r\n' not in source.read_bytes(),('new source not LF',r['va'])
  if r['compiled']:new+=1
 if r['compiled']:
  obj=ROOT/r['object'];sections=delta.base.abi.text_sections(obj);assert sections==r['native_text_sections']
  exact=any(t['relocations']==0 and t['bytes']==r['original_instruction_bytes_hex'] for t in sections);assert exact==r['exact_original_body_bytes_match']
  symbols=delta.base.coff_symbols(obj);assert symbols['defined_external_symbols']==r['defined_external_symbols'] and symbols['undefined_external_symbols']==r['undefined_external_symbols']
  undefined.update(r['undefined_external_symbols'])
 else:
  assert not (ROOT/r['object']).exists();assert r['diagnostics'];failures.append({'va':r['va'],'diagnostics':r['diagnostics']})
assert reused==127 and retried==32 and new==3 and cached_matches==27 and len(failures)==29
assert dict(undefined)==s['undefined_symbols']
result={'schema':1,'summary_sha256':sha(summary),'audit_source_sha256':sha(Path(__file__)),'input_pins_pass':True,'frozen187_source_objects_flags_pass':True,'exact184_include_only_pass':True,'original_body_ret_width_contracts_preserved':True,'new_output_lf_pass':True,'reused_objects':reused,'retried_failed_tus':retried,'new_objects':new,'real_coff_objects':reused+new,'cached_body_byte_matches':cached_matches,'remaining_failures':failures,'undefined_symbols':dict(undefined),'boundary':'Reuse/include/COFF audit only; original PE/native ABI proof retained from187/186 without new runtime execution or semantic acceptance'}
(RUN/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k!='remaining_failures'},indent=2))

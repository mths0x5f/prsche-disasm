"""Read-only208 source/metadata/COFF/capture audit; no compiler/oracle calls."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]; RUN=Path(__file__).resolve().parent
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result
declarations=load_module('decl184_208audit',ROOT/'scripts/research/experiment-v2-declarations-184.py')
coff=load_module('coff208audit',ROOT/'scripts/research/build-v2-compile-corpus.py')
report=json.loads((RUN/'summary.json').read_bytes()); validation=json.loads((RUN/'validation.json').read_bytes())
assert sha(RUN/'summary.json')==validation['summary_sha256']
def verify(item):
    name,expected=item; assert sha(ROOT/name)==expected,('input changed',name)
with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(verify,report['input_sha256'].items()))
assert report['selected']==9 and len(report['results'])==9 and report['full_audit_read_count']==1
assert report['actual_compiler_batches']==1 and report['objects_compiled']==3 and report['code_generation_failed']==6
assert report['compiled_vas']==['00589df0','00589f40','00590340'] and not report['warning_codes']
capture_path=ROOT/report['native_capture']; assert sha(capture_path)==report['native_capture_sha256']; capture=json.loads(capture_path.read_bytes())
prepare_path=ROOT/capture['prepare']; assert sha(prepare_path)==capture['prepare_sha256']; prepare=json.loads(prepare_path.read_bytes())
assert prepare['before_guard_pass'] and prepare['input_sha256']==report['input_sha256']
assert capture['observed_compiler_batch_exit_code']==report['observed_compiler_batch_exit_code']==2
assert capture['compile_seconds']==report['compile_seconds']==2.858542
assert capture['response_sha256']==report['compiler_response_sha256']==sha(ROOT/report['compiler_response'])
assert capture['log_sha256']==report['compiler_log_sha256']==sha(ROOT/report['compiler_log'])
extraction=json.loads((capture_path.parent/'input-extraction.json').read_bytes()); metadata=extraction['function_metadata']
text=(ROOT/report['compiler_log']).read_text(encoding='utf8'); diagnostics=declarations.diagnostics(text)
assert len(re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',text))==len(diagnostics)
by_va={va:[] for va in report['selected_scope_vas']}
for d in diagnostics:
    va=declarations.diagnostic_owner(d['source']); assert va in by_va; by_va[va].append(d)
assert Counter(re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',text))==Counter(by_va.keys())
assert not any(d['severity']=='warning' for d in diagnostics)
objects=0; undefined=Counter(); definitions=set()
for row in report['results']:
    va=row['va']; source=ROOT/row['generated_source']; baseline=ROOT/row['baseline_generated_source']; header=ROOT/row['declaration_header']
    assert sha(source)==row['generated_source_sha256'] and sha(baseline)==row['baseline_generated_source_sha256']
    raw=baseline.read_bytes(); match=re.search(rb'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n',raw,re.M); assert match
    include=('#include "'+header.as_posix()+'"\n').encode()
    assert source.read_bytes()==raw[:match.end()]+include+raw[match.end():]
    marker=('/* VA '+va+' */').encode(); a=raw.split(marker,1)[1]; b=source.read_bytes().split(marker,1)[1]
    assert a==b and hashlib.sha256(a).hexdigest()==row['body_after_marker_sha256']
    assert header.read_text(encoding='utf8')==declarations.header(row['declaration_records'])
    scoped={s['name']:s for s in metadata[va].get('globals',[]) if s.get('name')}
    for record in row['declaration_records']:
        assert record['symbol']==scoped[record['symbol']['name']] and record['consumer_vas']==[va] and record['consumer_va']==va
    assert row['ownership']==report['ownership_preflight'][va]
    assert not row['ownership']['canonical_overlaps'] and not row['ownership']['wip_implementation_definitions']
    assert row['diagnostics']==by_va[va]; errors=[d for d in by_va[va] if 'error' in d['severity']]
    assert len(errors)==row['owned_error_count'] and row['compiler_batch_exit_code']==2
    assert row['compiler_exit_code'] is None
    obj=ROOT/row['object']; assert obj.exists()==row['compiled']==row['code_generation_succeeded']==(not errors)
    if row['compiled']:
        assert row['actual_i386_coff_validated'] and row['object_only_status_certified']
        assert sha(obj)==row['object_sha256']; symbols=coff.coff_symbols(obj); assert symbols==row['symbols']
        assert any('FUN_'+va in name for name in symbols['defined']); objects+=1
        undefined.update(symbols['undefined']); definitions.update(symbols['defined']+symbols['common'])
assert objects==3
subset={s:n for s,n in undefined.items() if s not in definitions}
assert subset==report['subset_undefined_symbols'] and len(subset)==6 and sum(subset.values())==8
for path in (RUN/'README.md',RUN/'summary.json',Path(__file__),ROOT/'scripts/research/experiment-v2-frontier-dependencies-208.py',ROOT/report['compiler_response'],ROOT/report['compiler_log'],capture_path,prepare_path): assert b'\r' not in path.read_bytes()
validation.update(read_only_audit_sha256=sha(Path(__file__)),readme_sha256=sha(RUN/'README.md'),exact179_consumer_metadata_pass=True,
    only_include_changes_pass=True,body_bytes_identical_pass=True,prepare_capture_chain_pass=True,actual_observed_exit_and_time_pass=True,
    individual_exit_unknown_preserved=True,actual_three_coff_symbols_pass=True,actual_six_owned_failures_pass=True,
    exact_subset_frontier_pass=True,new_text_LF_pass=True)
(RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in validation.items() if not k.endswith('sha256')},indent=2))

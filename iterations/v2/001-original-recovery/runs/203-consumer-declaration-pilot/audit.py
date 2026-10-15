"""Read-only203 body/metadata/include/COFF evidence audit; no compiler invocation."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]; RUN=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('decl184audit203',ROOT/'scripts/research/experiment-v2-declarations-184.py'); declarations=importlib.util.module_from_spec(spec); spec.loader.exec_module(declarations)
spec=importlib.util.spec_from_file_location('coffaudit203',ROOT/'scripts/research/build-v2-compile-corpus.py'); coff=importlib.util.module_from_spec(spec); spec.loader.exec_module(coff)
summary_path=RUN/'summary.json'; report=json.loads(summary_path.read_bytes()); validation=json.loads((RUN/'validation.json').read_bytes())
assert validation['summary_sha256']==sha(summary_path)
triage=json.loads((ROOT/report['triage_summary']).read_bytes()); cache_path=ROOT/'local/experiments/v2-missing-body-triage-201/selected-inputs.json'; cache=json.loads(cache_path.read_bytes())
assert sha(cache_path)==triage['input_sha256'][cache_path.relative_to(ROOT).as_posix()]
assert report['selected_scope_vas']==triage['clean_declaration_pilot_vas'] and len(report['results'])==25
assert report['objects_compiled']==report['real_coff_objects']==21 and report['code_generation_failed']==4
assert report['owned_body_candidates']==0 and not report['blocked_metadata']


def verify(item):
    name,expected=item; assert sha(ROOT/name)==expected,('changed input',name)


with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(verify,report['input_sha256'].items()))
assert sha(ROOT/report['capture_driver'])==report['capture_driver_sha256']
assert report['actual_compiler_batches']==1 and report['actual_compiler_batches_this_pass']==0
assert report['compiler_batch_exit_code'] is None and report['compile_seconds'] is None
assert sha(ROOT/report['compiler_response'])==report['compiler_response_sha256']
assert sha(ROOT/report['compiler_log'])==report['compiler_log_sha256']
log=(ROOT/report['compiler_log']).read_text(encoding='utf8'); ds=declarations.diagnostics(log)
severity_lines=re.findall(r'(?m)^.*?:\s*(?:fatal error|error|warning)\s+[CD]\d+:',log)
assert len(severity_lines)==len(ds), 'Unattributed compiler/fatal diagnostic'
owned={r['va']:[] for r in report['results']}
for d in ds:
    va=declarations.diagnostic_owner(d['source']); assert va in owned; owned[va].append(d)
assert Counter(re.findall(r'(?m)^([0-9a-f]{8})\.cpp\s*$',log))==Counter(owned.keys())
objects=0; undefined=Counter(); definitions=set(); failures=[]
for row in report['results']:
    va=row['va']; source=ROOT/row['generated_source']; original=ROOT/row['baseline_generated_source']; header=ROOT/row['declaration_header']
    assert sha(source)==row['generated_source_sha256'] and sha(original)==row['baseline_generated_source_sha256']
    expected=original.read_bytes(); match=re.search(rb'^#include "[^\n]*ghidra-scalars-syntax-only\.h"\n',expected,re.M); assert match
    include=('#include "'+header.as_posix()+'"\n').encode()
    assert source.read_bytes()==expected[:match.end()]+include+expected[match.end():]
    marker=('/* VA '+va+' */').encode(); a=expected.split(marker,1)[1]; b=source.read_bytes().split(marker,1)[1]
    assert a==b and hashlib.sha256(a).hexdigest()==row['preserved_body_sha256']
    assert header.read_text(encoding='utf8')==declarations.header(row['declaration_records'])
    scoped={s['name']:s for s in cache['declarations'][va].get('globals',[]) if s.get('name')}
    for record in row['declaration_records']:
        assert record['symbol']==scoped[record['symbol']['name']]
        assert record['consumer_va']==va and record['consumer_vas']==[va]
    assert row['diagnostics']==owned[va]
    errors=[d for d in owned[va] if 'error' in d['severity']]; obj=ROOT/row['object']
    row['owned_error_count']=len(errors); row['owned_warning_count']=sum(d['severity']=='warning' for d in owned[va])
    assert row['compiler_exit_code'] is None and row['observed_compiler_exit_code'] is None
    assert obj.exists()==row['compiled']==row['code_generation_succeeded']==(not errors)
    if row['compiled']:
        assert sha(obj)==row['object_sha256']; symbols=coff.coff_symbols(obj); assert symbols==row['symbols']
        assert any('FUN_'+va in name for name in symbols['defined']); objects+=1
        row['actual_i386_coff_validated']=True
        row['object_only_status_certified']=True
        undefined.update(symbols['undefined']); definitions.update(symbols['defined']+symbols['common'])
    else:
        row['actual_i386_coff_validated']=False; row['object_only_status_certified']=False; failures.append(va)
unresolved={name:n for name,n in undefined.items() if name not in definitions}
assert unresolved==report['subset_undefined_symbols'] and len(unresolved)==43 and sum(unresolved.values())==60
assert objects==21 and failures==['00540480','005404e0','00554530','0058f1f0']
assert not any(d['severity']=='warning' for d in ds) and not report['warning_codes']
for p in (RUN/'README.md',summary_path,ROOT/'scripts/research/experiment-v2-declaration-pilot-203.py',Path(__file__),ROOT/report['compiler_response'],ROOT/report['compiler_log']): assert b'\r' not in p.read_bytes()
summary_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
validation.update(summary_sha256=sha(summary_path),read_only_audit_sha256=sha(Path(__file__)),readme_sha256=sha(RUN/'README.md'),native_object_status_evidence='Fresh actual i386 COFF + zero owned errors; observed compiler exit unknown',
                  actual_25_response_members_pass=True,actual_21_coff_symbols_pass=True,actual_four_failures_pass=True,
                  exact179_consumer_metadata_pass=True,byte_identical_bodies_pass=True,include_only_edits_pass=True,
                  observed_compiler_exits_all_unknown=True,new_text_LF_pass=True,subset_frontier_pass=True,new_warnings=0,
                  no_unattributed_compiler_or_fatal_diagnostics=True,explicit_per_row_owned_error_and_coff_proof=True)
(RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in validation.items() if not k.endswith('sha256')},indent=2))

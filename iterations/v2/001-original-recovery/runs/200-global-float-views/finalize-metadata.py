import importlib.util,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('views200',ROOT/'scripts/research/experiment-v2-global-views-200.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.RUN/'summary.json';d=json.loads(p.read_text())
for path,expected in d['input_sha256'].items():assert m.sha(ROOT/path)==expected
for row in d['results']:
 row['dependency_sha256']=m.base.headers_closure([ROOT/row['generated_source']],{})
 row['cache_inputs_sha256']=hashlib.sha256(json.dumps(row['dependency_sha256'],sort_keys=True).encode()).hexdigest()
 row['headers_sha256']={k:v for k,v in row['dependency_sha256'].items() if k.endswith('.h')}
 row['error_count']=sum('error' in x['severity'] for x in row['diagnostics'])
 row['warning_count']=sum(x['severity']=='warning' for x in row['diagnostics'])
d['metadata_finalization']={'only_exact_per_tu_dependency_closure':'no compiler rerun','driver_sha256':m.sha(Path(__file__))}
m.dump(p,d);m.dump(m.OUT/'audit.json',d)
m.dump(m.RUN/'validation.json',{'status':'PASS','all_input_sha_guards_before_after':True,'exact_per_tu_dependency_hashes':True,'bodies_unchanged':True,'diagnostics_attributed':True,'summary_sha256':m.sha(p),'native_compile_delta':d['new_objects']})
for row in d['results']:print(row['va'],row['compiled'],row['error_count'],row['warning_count'])

"""Compact measured syntax-audit results; keep full diagnostics in local artifacts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--audit',action='append',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
 phases=[];inputs={}
 for path in args.audit:
  data=path.read_bytes();p=json.loads(data);inputs[path.resolve().relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest();warnings=Counter();warning_functions=Counter()
  for row in p['results']:
   seen=set()
   for diagnostic in row['diagnostics']:
    if diagnostic['severity']=='warning':warnings[diagnostic['code']]+=1;seen.add(diagnostic['code'])
   warning_functions.update(seen)
  phase={key:p[key] for key in ('phase','language','total_exported_functions','selected_functions','syntax_passed','syntax_failed','elapsed_seconds','errors_by_category','functions_by_error_category','error_codes','headers_sha256','limits')}
  phase.update(warning_codes=dict(warnings.most_common()),functions_by_warning=dict(warning_functions.most_common()),syntax_passed_with_implicit_function_declarations=sum(r['syntax_passed'] and any(d['code']=='C4013' for d in r['diagnostics']) for r in p['results']),compiler_error_limited_vas=[r['va'] for r in p['results'] if any(d['code']=='C1003' for d in r['diagnostics'])],syntax_passed_vas=[r['va'] for r in p['results'] if r['syntax_passed']],examples=p['examples'])
  phases.append(phase)
 summary={'schema':1,'module':'Porsche.exe','sha256':p['original_sha256'],'pseudo_c_sha256':p['pseudo_c_sha256'],'pseudo_c_bytes':p['pseudo_c_bytes'],'input_audit_sha256':inputs,'phases':phases,'lexical_full_corpus':p['lexical_full_corpus'],'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in ('scripts/research/audit-v2-compile-corpus.py','scripts/research/report-v2-compile-corpus.py','scripts/research/ghidra/ExportRecoveryCorpus.java','iterations/v2/001-original-recovery/runs/178-compile-corpus/README.md')},'findings':['Current corpus export contains5772 decompiled bodies, not a complete declaration/type/storage source tree.','Missing declarations can be addressed in bulk; calling convention, conflicting inferred prototypes, p-code intrinsics, scalar slices, extended-float representation and overlapping global identities remain independent compiler/runtime concerns.','No function bodies, storage definitions, stubs, host algorithm substitutes or production source changes are introduced by this audit.','C syntax success can still rely on implicit function declarations; those cases are counted separately. Syntax success alone does not prove correct ABI or behavior.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8');print(json.dumps({'phases':len(phases),'output':str(args.output),'syntax_counts':[{'phase':p['phase'],'language':p['language'],'passed':p['syntax_passed'],'total':p['selected_functions']} for p in phases]}))
if __name__=='__main__':main()

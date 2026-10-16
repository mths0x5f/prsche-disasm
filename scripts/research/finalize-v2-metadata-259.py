"""Correct Run259 attempt accounting and pin preserved repair artifacts, without building."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/259-canonical-reuse'
OUT=ROOT/'local/experiments/v2-canonical-reuse-259'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    s=json.loads((RUN/'summary.json').read_bytes());b=json.loads((RUN/'bindings/summary.json').read_bytes())
    assert s['compiled_vas']==['0059f050','005a66a7'] and s['fixture']['native_exit_code']==0
    receipts=['first-compile.execution.json','compile.execution.json','first-fixture-link.execution.json','first-fixture-repair-compile.execution.json','fixture-repair-compile.execution.json','first-fixture-native.execution.json','fixture-native.execution.json','fixture-link.execution.json']
    codes=[json.loads((OUT/n).read_bytes())['exit_code'] for n in receipts]
    assert codes[0]!=0 and codes[2]!=0 and codes[5]==3221225477 and all(c==0 for c in (codes[1],codes[3],codes[4],codes[6],codes[7])),codes
    observed=json.loads((OUT/'compile.execution.json').read_bytes())['command']
    roots=[Path(observed[i+1]).resolve() for i,item in enumerate(observed[:-1]) if item=='/I']
    assert len(roots)==5 and all(p.is_dir() for p in roots)
    for row in s['results']:
        assert row['compiler_command']==observed
        row['include_directories']=[rel(p) if p.is_relative_to(ROOT) else p.as_posix() for p in roots]
    s['actual_compiler_batches']=4;s['recompilations']=3
    s['fixture_repair_history']=[rel(OUT/n) for n in receipts[2:]]
    for p in [ROOT/'scripts/research/experiment-v2-canonical-reuse-259.py',ROOT/'scripts/research/repair-v2-fixture-259.py',ROOT/'scripts/research/repair-v2-stack-probe-259.py',ROOT/'scripts/research/finalize-v2-metadata-259.py',*[OUT/n for n in receipts],*[OUT/n for n in ('first-native-fixture.cpp','first-native-fixture.obj','second-native-fixture.cpp','second-native-fixture.obj','second-native-fixture.exe','second-native-fixture.map','first-fixture-link.log','second-fixture-link.log','first-fixture-repair-compile.log','first-fixture-native.log','stale-executable-native-observation.json') if (OUT/n).exists()]]:
        s['input_sha256'][rel(p)]=sha(p)
    write(RUN/'summary.json',s)
    b['input_sha256']={**s['input_sha256'],rel(RUN/'summary.json'):sha(RUN/'summary.json')}
    b['ordinary_summary_sha256']=sha(RUN/'summary.json')
    write(RUN/'bindings/summary.json',b)
    print(json.dumps(dict(compilers=4,recompilations=3,original_bodies=2)))
if __name__=='__main__':main()

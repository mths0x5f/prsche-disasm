"""Read-only census audit: same identities/counts and four gained whole bodies."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/277-x86-extended-integer'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def main():
    s=load(RUN/'census.json');native=load(RUN/'summary.json');v=load(RUN/'validation.json')
    assert v['passed'] and v['summary_sha256']==digest(RUN/'summary.json') and native['backend_sha256']==s['backend_sha256']
    for name,h in s['input_sha256'].items():assert digest(ROOT/name)==h,('input drift',name)
    old=load(ROOT/'iterations/v2/001-original-recovery/runs/260-x86-backend-coverage/summary.json')
    original=load(ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json')
    qmap={r['va']:r for r in original['rows']};omap={r['va']:r for r in old['rows']};rmap={r['va']:r for r in s['rows']}
    assert len(rmap)==85 and set(rmap)==set(qmap)==set(omap)
    assert all(rmap[va]['body_sha256']==qmap[va]['body_sha256'] and rmap[va]['body_bytes']==qmap[va]['body_bytes'] for va in rmap)
    assert s['baseline_supported']==25 and s['syntax_supported']==29 and s['syntax_rejected']==56 and s['baseline_syntax_regressions']==0
    assert sum(r['classification']=='syntax_supported' for r in s['rows'])==29
    assert all(rmap[va]['classification']=='syntax_supported' for va in omap if omap[va]['classification']=='syntax_supported')
    gained=[va for va in rmap if rmap[va]['classification']=='syntax_supported' and omap[va]['classification']!='syntax_supported']
    assert gained==s['newly_whole_syntax_supported_vas']==['005a7673','00536df0','004ede20','005349e0'] and s['supported_delta']==4
    backend=module('backend277censusaudit','scripts/research/x86-cpp-backend-277.py')
    pe_map=module('census260map277','scripts/research/census-v2-x86-cpp-260.py').pe_map
    image=(ROOT/'local/game/Porsche.exe').read_bytes();get=pe_map(image)
    for va in gained:
        raw=get(int(va,16),rmap[va]['body_bytes']);assert hashlib.sha256(raw).hexdigest()==rmap[va]['body_sha256']
        _,witness=backend.translate(raw,int(va,16));assert b''.join(bytes.fromhex(w['bytes']) for w in witness)==raw
    assert s['accepted_functions_added']==s['compiler_commands']==s['native_commands']==0 and s['before_after_guards']
    result=dict(passed=True,census_sha256=digest(RUN/'census.json'),audit_source_sha256=digest(__file__),input_pins=len(s['input_sha256']),
                frozen_source_bodies=85,baseline_syntax_supported=25,new_syntax_supported=29,gained_whole_body_redecodes=4,
                gained_vas=gained,baseline_syntax_regressions=0,semantic_acceptance=False,native_commands=0,compiler_commands=0)
    (RUN/'census-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':main()

"""Same85 frozen PE bodies as260, syntax-only measurement after native277 proof."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import capstone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/277-x86-extended-integer'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
BACKEND_SHA='7dd257f43dc304ad183f25dd483a33dd9f76f285b8a7478dd3c9762debbab42b'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def main():
    assert not(RUN/'census.json').exists(),'completed census immutable'
    pins={}
    def pin(p,expected=None):
        p=Path(p).resolve();h=digest(p);assert expected is None or h==expected,('pin',p);pins[relative(p)]=h;return p
    pin(Path(__file__));pin(ROOT/'scripts/research/x86-cpp-backend-257.py',BASE_SHA);pin(ROOT/'scripts/research/x86-cpp-backend-277.py',BACKEND_SHA)
    backend=module('backend277census','scripts/research/x86-cpp-backend-277.py')
    oldscript=module('census260reuse','scripts/research/census-v2-x86-cpp-260.py');pin(ROOT/'scripts/research/census-v2-x86-cpp-260.py')
    source252=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json'))
    source260=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/260-x86-backend-coverage/summary.json'))
    native=load(pin(RUN/'summary.json'));validation=load(pin(RUN/'validation.json'))
    assert validation['passed'] and validation['summary_sha256']==digest(RUN/'summary.json') and native['backend_sha256']==BACKEND_SHA
    assert source252['original_sha256']==source260['original_sha256']==SHA and source260['frontier']['source_bodies']==85
    assert len(source252['rows'])==len(source260['rows'])==85 and source260['frontier']['syntax_supported']==25
    oldrows={r['va']:r for r in source260['rows']};assert set(oldrows)=={r['va'] for r in source252['rows']}
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();pe_bytes=oldscript.pe_map(image)
    catalog={r['entry_va']:r for r in map(json.loads,pin(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf8').splitlines())}
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    rows=[];new=[];families=Counter();counts=Counter()
    for q in source252['rows']:
        va=q['va'];item=catalog[va];assert len(item['ranges'])==1 and item['ranges'][0][0]==va
        start,end=(int(v,16) for v in item['ranges'][0]);raw=pe_bytes(start,end-start+1)
        assert len(raw)==q['body_bytes'] and hashlib.sha256(raw).hexdigest()==q['body_sha256']
        instructions=list(decoder.disasm(raw,start));assert sum(i.size for i in instructions)==len(raw)
        try:
            source,witness=backend.translate(raw,start);classification='syntax_supported';rejection=None
            assert b''.join(bytes.fromhex(w['bytes']) for w in witness)==raw
        except ValueError as e:classification='syntax_rejected';rejection=str(e)
        baseline=oldrows[va]['classification'];counts[classification]+=1
        if baseline=='syntax_supported':assert classification=='syntax_supported',('baseline syntax regression',va)
        if classification=='syntax_supported' and baseline!='syntax_supported':new.append(va)
        if rejection:
            tail=rejection.split(': ',1)[-1];families[tail.split(' ',1)[0]]+=1
        rows.append(dict(va=va,body_bytes=len(raw),body_sha256=q['body_sha256'],decoded_instructions=len(instructions),baseline_classification=baseline,
                         classification=classification,first_rejection=rejection,baseline_first_rejection=oldrows[va]['first_rejection'],
                         direct_calls=oldrows[va]['direct_calls'],indirect_call=oldrows[va]['indirect_call'],global_operands=oldrows[va]['global_operands'],
                         external_jmp_targets=oldrows[va]['external_jmp_targets']))
    # Navigation filter identical in scope to260. No provider/memory/callee is invented.
    rowmap={r['va']:r for r in rows};chains=[]
    for r in rows:
        if not r['direct_calls']:continue
        seen=set();todo=[r['va']];closed=True
        while todo:
            va=todo.pop()
            if va in seen:continue
            seen.add(va);q=rowmap.get(va)
            if not q or q['classification']!='syntax_supported' or q['indirect_call'] or q['global_operands']:closed=False;break
            todo.extend(q['direct_calls'])
        if closed:chains.append(dict(root=r['va'],transitive_vas=sorted(seen),external_jmp_exits=r['external_jmp_targets']))
    for name,h in pins.items():assert digest(ROOT/name)==h,('input drift',name)
    result=dict(schema=1,kind='same85-body-syntax-census',original_sha256=SHA,backend_sha256=BACKEND_SHA,baseline_backend_sha256=BASE_SHA,
                source_bodies=85,baseline_supported=25,syntax_supported=counts['syntax_supported'],syntax_rejected=counts['syntax_rejected'],
                newly_whole_syntax_supported_vas=new,supported_delta=len(new),baseline_syntax_regressions=0,remaining_first_rejection_families=dict(families),
                rows=rows,next_closed_call_chain_navigation=chains[:3],input_sha256=pins,before_after_guards=True,compiler_commands=0,native_commands=0,
                accepted_functions_added=0,limits=['Same frozen252/26085bodies, not the latest whole-game/nativefrontier estimate.',
                'Whole-body syntax support is not originalsemantic/ABI/provider/data/nativeacceptance.',
                'Native277proof covers syntheticintegerlemmas; originalper-bodyalgorithms were not manually written or executed here.',
                'Closedchainnavigation requires everydirectcallee inside85bodyset and rejectsindirectCALL/absolute globals; externalJMP exits remain explicit.'])
    (RUN/'census.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k] for k in ['source_bodies','baseline_supported','syntax_supported','syntax_rejected','newly_whole_syntax_supported_vas','supported_delta']}))


if __name__=='__main__':main()

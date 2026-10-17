"""Bounded original-x86 free cutpoints using the existing heap Unicorn verifier."""
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local/experiments/v2-canonical-heap-release-263'
SRC=ROOT/'scripts/research/verify-v2-heap.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 sys.path.insert(0,str(SRC.parent))
 spec=importlib.util.spec_from_file_location('heap263original',SRC);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 module=next(r for r in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if r['file']=='Porsche.exe')
 data=(ROOT/'local/game'/module['path']).read_bytes();assert sha(ROOT/'local/game'/module['path'])==module['sha256']
 functions={r['entry_va']:r for r in map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines())}
 wires=['8|64|0|0|0|0|512|A,32,0,-|F,0','8|64|0|0|0|1|512|A,32,0,-|F,0','8|64|0|0|0|0|512|A,32,0,-|A,32,0,-|F,0|F,1']
 cases=[]
 for wire in wires:
  result,coverage=m.original(wire,module,data,functions)
  assert '00531f90' in coverage
  ops=wire.split('|')[7:];values=result['returns'];state=result['states'];frees=[]
  for i,op in enumerate(ops):
   if not op.startswith('F,'):continue
   slot=int(op.split(',')[1]);allocation_index=next(j for j,q in enumerate(ops[:i]) if q.startswith('A,') and sum(x.startswith('A,') for x in ops[:j])==slot)
   frees.append(dict(pointer_offset=values[allocation_index+1],before=state[i],after=state[i+1],return_value=values[i+1]))
  assert frees and all(q['return_value']==1 and q['pointer_offset']>=0 for q in frees)
  cases.append(dict(wire=wire,locked=int(wire.split('|')[5])!=0,arena_bytes=512,frees=frees,calls=result['calls']))
 report=dict(schema=1,kind='bounded-original-x86-heap-free-oracles',original_sha256=module['sha256'],original_verifier=SRC.relative_to(ROOT).as_posix(),original_verifier_sha256=sha(SRC),cases=cases,whole_551_case_verifier_not_rerun=True)
 (OUT/'original-oracles.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(wires=len(cases),free_cutpoints=sum(len(x['frees']) for x in cases),bytes=sum(len(x['frees'])*512 for x in cases))))
if __name__=='__main__':main()

"""Run260 bounded syntax census for the frozen 252 body frontier."""
import argparse, capstone, hashlib, importlib.util, json, re, struct, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/260-x86-backend-coverage'
OUT=ROOT/'local/experiments/v2-x86-cpp-coverage-260'
PE_SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BACKEND_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'

def digest(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def relative(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p): return json.loads(Path(p).read_bytes())
def mod(p):
 spec=importlib.util.spec_from_file_location('backend257',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def pe_map(data):
 pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]; oh=struct.unpack_from('<H',data,pe+20)[0]; base=struct.unpack_from('<I',data,pe+24+28)[0]; sh=pe+24+oh; ss=[]
 for i in range(n):
  q=sh+40*i; name=data[q:q+8].split(b'\0',1)[0].decode('ascii'); vs,va,raw,ptr=struct.unpack_from('<IIII',data,q+8); ss.append((name,va,vs,raw,ptr))
 def get(va,size):
  r=va-base
  for name,sv,vsize,rsize,ptr in ss:
   if sv<=r and r+size<=sv+vsize and r+size<=sv+rsize:return data[ptr+r-sv:ptr+r-sv+size]
  raise ValueError(f'no raw body {va:08x}+{size}')
 return get

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--rewrite-existing',action='store_true')
 parser.add_argument('--validate-existing',action='store_true')
 args=parser.parse_args()
 summary_path=RUN/'summary.json'
 if args.validate_existing:
  old=load(summary_path); assert old['kind']=='bounded-x86-backend-coverage' and old['frontier']['source_bodies']==85
  assert old['frontier']['syntax_supported'] + old['frontier']['syntax_rejected'] == 85
  assert old['closed_chain_filter']['requires_all_direct_callees_in_85_body_frontier']
  for name,sha in old['input_sha256'].items():
   if name != relative(Path(__file__)): assert digest(ROOT/name)==sha,(name,digest(ROOT/name),sha)
  print(json.dumps({'validated':True,'syntax_supported':old['frontier']['syntax_supported'],'syntax_rejected':old['frontier']['syntax_rejected']})); return
 if summary_path.exists() and not args.rewrite_existing:
  raise SystemExit('completed summary exists; use --validate-existing or explicit --rewrite-existing')
 RUN.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
 source252=ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json'; backend_path=ROOT/'scripts/research/x86-cpp-backend-257.py'; census_path=ROOT/'scripts/research/census-v2-x86-cpp-252.py'; pe_path=ROOT/'local/game/Porsche.exe'
 assert digest(backend_path)==BACKEND_SHA
 s252=load(source252); assert s252['queue_original_body_trace_required']==85 and s252['original_sha256']==PE_SHA
 pe=pe_path.read_bytes(); assert digest(pe_path)==PE_SHA; get=pe_map(pe); backend=mod(backend_path)
 cat={}
 cp=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
 for line in cp.read_text(encoding='utf-8-sig').splitlines():
  if line.strip():
   x=json.loads(line); cat[x['entry_va']]=x
 rows=[]; supported=[]; opcode=Counter(); rejected=Counter()
 for q in s252['rows']:
  va=q['va']; c=cat[va]; ranges=c['ranges']; assert len(ranges)==1 and ranges[0][0]==va
  start,end=(int(z,16) for z in ranges[0]); raw=get(start,end-start+1); assert hashlib.sha256(raw).hexdigest()==q['body_sha256']
  cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); cs.detail=True; ins=list(cs.disasm(raw,start)); counts=Counter(i.mnemonic for i in ins); opcode.update(counts)
  try:
   code,witness=backend.translate(raw,start); cls='syntax_supported'; rej=None
   supported.append(va)
  except ValueError as e:
   code=''; witness=[]; cls='syntax_rejected'; rej=str(e); rejected[rej.split(':',1)[0]]=rejected[rej.split(':',1)[0]]+1
  calls=[]; indirect=False; globals=[]; external_jmps=[]
  for i in ins:
   if i.mnemonic=='call':
    if i.operands and i.operands[0].type==capstone.x86.X86_OP_IMM:calls.append(f'{i.operands[0].imm:08x}')
    else:indirect=True
   if i.mnemonic=='jmp' and i.operands and i.operands[0].type==capstone.x86.X86_OP_IMM and not (start <= i.operands[0].imm < end): external_jmps.append(f'{i.operands[0].imm:08x}')
   for op in i.operands:
    if op.type==capstone.x86.X86_OP_MEM and op.mem.base==0 and op.mem.index==0:globals.append(f'{op.mem.disp & 0xffffffff:08x}')
  rows.append({'va':va,'body_bytes':q['body_bytes'],'decoded_instructions':len(ins),'classification':cls,'first_rejection':rej,'opcode_counts':dict(sorted(counts.items())),'direct_calls':calls,'indirect_call':indirect,'global_operands':sorted(set(globals)),'external_jmp_targets':sorted(set(external_jmps))})
 supported_set=set(supported); rowmap={r['va']:r for r in rows}; chains=[]
 def closed(root):
  seen=set(); stack=[root]
  if not rowmap[root]['direct_calls']: return False
  while stack:
   va=stack.pop()
   if va in seen: continue
   seen.add(va); r=rowmap.get(va)
   if not r or r['classification']!='syntax_supported' or r['indirect_call'] or r['global_operands']: return False
   for callee in r['direct_calls']:
    if callee not in rowmap: return False
    stack.append(callee)
  return True
 for r in rows:
  if closed(r['va']): chains.append({'root':r['va'],'callees':sorted(set(r['direct_calls'])),'external_jmp_exits':r['external_jmp_targets']})
 supported_opcode=Counter(); rejected_opcode=Counter(); remaining_families=Counter()
 for rr in rows:
  target=supported_opcode if rr['classification']=='syntax_supported' else rejected_opcode
  target.update(rr['opcode_counts'].keys())
 for rr in rows:
  if rr['classification']=='syntax_rejected' and rr['first_rejection']:
   text=rr['first_rejection'].split(': ',1)[-1]; remaining_families[text.split(' ',1)[0]]=remaining_families[text.split(' ',1)[0]]+1
 out={'schema':1,'run':260,'kind':'bounded-x86-backend-coverage','original_sha256':PE_SHA,'input_sha256':{'scripts/research/census-v2-x86-cpp-260.py':digest(Path(__file__)), 'scripts/research/census-v2-x86-cpp-252.py':digest(census_path),'scripts/research/x86-cpp-backend-257.py':digest(backend_path),'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json':digest(source252),'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl':digest(cp),'local/game/Porsche.exe':digest(pe_path)},'frontier':{'source_bodies':85,'syntax_supported':len(supported),'syntax_rejected':len(rows)-len(supported),'baseline_246_syntax_supported':0,'supported_delta_vs_246':len(supported),'supported_vas':supported},'opcode_counts':dict(opcode),'supported_opcode_families':sorted(supported_opcode),'rejected_opcode_families':sorted(rejected_opcode),'remaining_rejection_families':dict(sorted(remaining_families.items())),'rows':rows,'next_closed_direct_call_chains':chains[:3],'closed_chain_filter':{'requires_all_direct_callees_in_85_body_frontier':True,'recursive':True,'rejects_indirect_calls':True,'rejects_global_operands':True,'records_external_jmp_exits':True},'acceptance_boundary':'Syntax translation coverage only; no compiler, native execution, ABI/semantic/original-fidelity acceptance. Direct call/global operand chain filter is navigation.'}
 summary_path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n'); (RUN/'README.md').write_text(f'''# Run 260 — x86 backend coverage\n\n- Frozen 252 frontier: 85 original bodies; backend 257 syntax census: {len(supported)} supported, {len(rows)-len(supported)} rejected.\n- Exact PE body bytes/call graph are pinned in `summary.json`; remaining opcode families and supported instruction counts are recorded there.\n- Up to three closed direct-call chains are selected only when syntax-supported and free of indirect calls/global operands; this is navigation, not acceptance.\n- No compiler, native execution, gameplay implementation, ABI or fidelity claim.\n''',encoding='utf-8',newline='\n')
 print(json.dumps({'supported':len(supported),'rejected':len(rows)-len(supported),'chains':chains[:3]}))
if __name__=='__main__':main()

"""Read-only indexed small-body selection for the bounded Run258 CALL pilot."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import capstone
from capstone.x86 import X86_OP_REG,X86_OP_MEM,X86_OP_IMM

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/258-x86-call-chain'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CAT=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    RUN.mkdir(exist_ok=True,parents=True)
    pins={str(p.relative_to(ROOT)):digest(p) for p in [CAT,Path(__file__),ROOT/'research/binary-index/README.md',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json']}
    image=(ROOT/'local/game/Porsche.exe').read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    spec=importlib.util.spec_from_file_location('pe258',ROOT/'scripts/research/audit-v2-x86-tail-dispatch-253.py');pe=importlib.util.module_from_spec(spec);spec.loader.exec_module(pe)
    catalog={r['entry_va']:r for r in map(json.loads,CAT.read_text(encoding='utf8').splitlines())}
    registry=json.loads((ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    registered={r['entry_va']:r for r in registry if r['module']=='Porsche.exe'}
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    allowed={'mov','lea','xor','and','test','cmp','sbb','neg','jl','jge','je','jne','jmp','ret','push','pop','add','sub'}
    regs={'eax','ecx','edx','ebx','esp','ebp','esi','edi','al'}
    bodies={};calls={};total=0
    for va,row in catalog.items():
        if row['body_bytes']>96 or len(row['ranges'])!=1:continue
        lo,hi=row['ranges'][0]
        if lo!=va or int(hi,16)-int(lo,16)+1!=row['body_bytes']:continue
        total+=1;raw=pe.original_bytes(image,va,row['body_bytes']);ins=list(decoder.disasm(raw,int(va,16)))
        if sum(i.size for i in ins)!=len(raw) or not ins or ins[-1].mnemonic!='ret':continue
        starts={i.address for i in ins};valid=True;edges=[]
        for i in ins:
            if i.mnemonic not in allowed|{'call'}:valid=False;break
            if i.mnemonic in {'call','jmp','jl','jge','je','jne'}:
                if len(i.operands)!=1 or i.operands[0].type!=X86_OP_IMM:valid=False;break
                if i.mnemonic=='call':edges.append(f'{i.operands[0].imm&0xffffffff:08x}')
                elif i.operands[0].imm not in starts:valid=False;break
            for op in i.operands:
                if op.type==X86_OP_REG and (i.reg_name(op.reg) not in regs or op.size not in [1,4]):valid=False
                if op.type==X86_OP_MEM:
                    if op.size not in [1,4] or op.mem.segment or not(op.mem.base or op.mem.index):valid=False
                    for reg in [op.mem.base,op.mem.index]:
                        if reg and i.reg_name(reg) not in regs-{'al'}:valid=False
        if valid:bodies[va]=(raw,ins);calls[va]=edges
    candidates=[]
    for va,edges in calls.items():
        if not edges or len(set(edges))>2 or va in edges:continue
        if any(t not in bodies or calls[t] or len(bodies[t][0])>64 for t in edges):continue
        graph=[va]+sorted(set(edges))
        score=sum(len(bodies[v][0]) for v in graph)
        candidates.append(dict(caller=va,callees=sorted(set(edges)),call_sites=len(edges),total_bytes=score,
            existing_accepted=[v for v in graph if v in registered],bodies={v:dict(bytes=len(bodies[v][0]),hex=bodies[v][0].hex(),instructions=[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in bodies[v][1]]) for v in graph}))
    candidates.sort(key=lambda r:(r['total_bytes'],r['caller']))
    for name,h in pins.items():assert digest(ROOT/name)==h
    result=dict(original_sha256=SHA,selection_scope='Indexed single-span original bodies<=96B; CALL-free callees<=64B; exact PE; no absolute or segment memory; finite supported operand subset',
                indexed_bodies_scanned=total,operand_supported_small_bodies=len(bodies),closed_candidates=len(candidates),candidates=candidates[:30],input_sha256=pins,
                native_execution_commands=0,new_accepted_functions=0)
    (RUN/'selection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(scanned=total,candidates=len(candidates),top=[{k:r[k] for k in ['caller','callees','total_bytes','existing_accepted']} for r in candidates[:12]])))
if __name__=='__main__':main()

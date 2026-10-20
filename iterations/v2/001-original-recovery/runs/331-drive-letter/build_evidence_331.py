"""Read-only original/index/owner evidence; does not rerun native verification."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import capstone

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
index=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
registry=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'
spec=importlib.util.spec_from_file_location('pe331',ROOT/'scripts/research/verify-v2-pr9-resource-313.py')
utility=importlib.util.module_from_spec(spec);spec.loader.exec_module(utility)
pe=ROOT/'local/game/Porsche.exe';data=pe.read_bytes();body=utility.pe_at(data,0x5916a0,111)
functions=[json.loads(x) for x in (index/'functions.jsonl').read_text().splitlines()]
target=next(x for x in functions if x['entry_va']=='005916a0')
accepted=[x for x in json.loads(registry.read_text())['functions'] if x['module']=='Porsche.exe']
by_entry={x['entry_va']:x for x in functions}
containing=[]
for owner in accepted:
    for start,end in by_entry.get(owner['entry_va'],{}).get('ranges',[]):
        if int(start,16)<=0x59170e and int(end,16)>=0x5916a0:containing.append(owner)
assert not containing
matches=[]
for base in ['iterations/v2/001-original-recovery/runs','iterations/v2/001-original-recovery/source']:
    for path in (ROOT/base).rglob('*'):
        if path.suffix not in ('.cpp','.hpp','.h','.c') or RUN in path.parents:continue
        for line,text in enumerate(path.read_text(encoding='utf8',errors='replace').splitlines(),1):
            if re.search('005916a0|5916a0',text,re.I):matches.append(dict(path=rel(path),line=line,text=text))
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
instructions=[dict(va=f'{i.address:08x}',bytes=i.bytes.hex(),text=f'{i.mnemonic} {i.op_str}'.strip()) for i in md.disasm(body,0x5916a0)]
assert sum(len(bytes.fromhex(x['bytes'])) for x in instructions)==111
inputs=[pe,index/'functions.jsonl',index/'disassembly.asm',index/'decompiled.c',registry,ROOT/'research/binary-index/README.md',ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl']
result=dict(schema=1,run=331,query='005916a0;005a2780;005cd1f4;005b221c/GetFullPathNameA;005b2290/CharUpperA;00591760',module='Porsche.exe',original_sha256=sha(pe),indexed_function=target,body_sha256=hashlib.sha256(body).hexdigest(),instructions=instructions,literal=dict(va='005cd1f4',bytes=utility.pe_at(data,0x5cd1f4,2).hex(),value='.'),owners=dict(accepted_registry_entries=len(accepted),entry_or_intersecting_body_owners=containing,existing_source_mentions=matches,interpretation='All pre-existing mentions are declarations or calls; no previous implementation body.'),inputs_sha256={rel(p):sha(p) for p in inputs},confirmation=['Search(|) occurs before null fallback; search return is also initial file-part cell.','Null fallback is original literal dot, not empty.','GetFullPathNameA receives261-byte buffer and pointer-to-file-part; CharUpperA always follows even for0/1/high-bit lengths.','Length comparison is signed32; accepted letter is post-CharUpper buffer[0] when buffer[1] is colon.','Return ABI definesAL only; fullEAX is not accepted.'],limits=['Host OS path/uppercase behavior is outside controlled API verification.','Null branch tested only with controlled search; canonical original search does not permit null.'])
(RUN/'evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
print(f'evidence PASS:111 decoded bytes,{len(matches)} old source mentions,no accepted owner')

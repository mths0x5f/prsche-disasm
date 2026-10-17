"""Four bounded raw windows for an accepted HOLD; no function-boundary inference."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import capstone

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/267-heap-table-evidence'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
WINDOWS=((0x5697d0,23,0x5697d5),(0x569a40,43,0x569a4b),(0x569b10,44,0x569b1e),(0x56a1f0,56,0x56a222))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (RUN/'gap-windows.json').exists(),'completed windows immutable'
    paths=[Path(__file__),RUN/'summary.json',ROOT/'local/game/Porsche.exe',ROOT/'scripts/research/audit-v2-x86-call-chain-258.py',
           ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm',
           ROOT/'research/binary-index/manual-functions.jsonl']
    pins={p.resolve().relative_to(ROOT).as_posix():digest(p) for p in paths}
    assert digest(ROOT/'local/game/Porsche.exe')==SHA
    spec=importlib.util.spec_from_file_location('pe267windows',ROOT/'scripts/research/audit-v2-x86-call-chain-258.py')
    pe=importlib.util.module_from_spec(spec);spec.loader.exec_module(pe)
    image=(ROOT/'local/game/Porsche.exe').read_bytes()
    catalog=[json.loads(line) for line in paths[4].read_text(encoding='utf8').splitlines()]
    ranges=sorted((int(a,16),int(b,16),r['entry_va']) for r in catalog for a,b in r['ranges'])
    starts={a for a,n,s in WINDOWS};callrefs={a:[] for a in starts}
    for lineno,line in enumerate(paths[5].read_text(encoding='utf8').splitlines(),1):
        match=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+CALL 0x([0-9a-f]+)$',line)
        if match and int(match[3],16) in starts:
            pc=int(match[1],16);raw=bytes.fromhex(match[2]);assert pe.original_bytes(image,match[1],len(raw))==raw
            callrefs[int(match[3],16)].append(dict(pc=match[1],bytes=match[2],line=lineno,
                      indexed_call=True,owners=[v for a,b,v in ranges if a<=pc<=b]))
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);rows=[]
    for start,n,site in WINDOWS:
        raw=pe.original_bytes(image,f'{start:08x}',n);ins=list(decoder.disasm(raw,start));assert sum(i.size for i in ins)==n
        previous=max((r for r in ranges if r[1]<start),key=lambda r:r[1]);following=min((r for r in ranges if r[0]>=start+n),key=lambda r:r[0])
        rows.append(dict(candidate_window_start=f'{start:08x}',bytes=n,hex=raw.hex(),HIGHLOW_site=f'{site:08x}',
                         instructions=[dict(pc=f'{i.address:08x}',bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins],
                         indexed_CALL_entry_refs=callrefs[start],
                         preceding_indexed_range=dict(start=f'{previous[0]:08x}',end=f'{previous[1]:08x}',entry=previous[2]),
                         following_indexed_range=dict(start=f'{following[0]:08x}',end=f'{following[1]:08x}',entry=following[2]),
                         accepted_as_function=False,navigation_only=True))
    assert rows[0]['hex']=='6a406a0068204f6b00e8b22afdff83c40cb801000000c3'
    for name,h in pins.items():assert digest(ROOT/name)==h,('input mutation',name)
    result=dict(kind='raw-unindexed-heap-table-gap-windows',original_sha256=SHA,windows=rows,input_sha256=pins,before_after_guards=True,
                compiler_commands=0,native_commands=0,new_index_functions=0,
                interpretation=['The first candidate window passes(tablebase,0,64)to0053c290 and returns1, as rawinstruction evidence only.',
                                '0053c290 is a multi-path fill dispatch boundary; no complete fillerbehavior or reachability is proved here.',
                                'No indexed directCALL to the four candidatewindow starts was found; this is not wholeprogram absence proof.',
                                'Candidatewindow alignment and overlapping decode do not establish an executable function entry. HOLD retained.'])
    (RUN/'gap-windows.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(windows=len(rows),raw_bytes=sum(r['bytes'] for r in rows),indexed_direct_entry_CALLs=sum(len(x) for x in callrefs.values()),hold=True)))


if __name__=='__main__':main()

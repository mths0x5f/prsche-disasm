"""Private177 navigation/ABI evidence; not a behavioral verification report."""
import collections
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/177-application-context-core'
INDEX=ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def main():
    functions={x['entry_va']:x for x in map(json.loads,(INDEX/'functions.jsonl').read_text().splitlines())}
    module=next(x for x in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if x['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(binary).hexdigest()==SHA
    def raw(a,n):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=a<0x400000+s['rva']+s['raw_size'])
        return binary[sec['raw_offset']+a-0x400000-sec['rva']:sec['raw_offset']+a-0x400000-sec['rva']+n]
    instructions={}
    for line in (ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text().splitlines():
        parts=line.split(None,3)
        if len(parts)<3:continue
        try:address=int(parts[0],16);code=bytes.fromhex(parts[1])
        except ValueError:continue
        instructions[address]=(code,parts[2],parts[3] if len(parts)>3 else '')
    core={a:v for a,v in instructions.items() if 0x4d3420<=a<=0x4d55ac}
    targets=sorted({int(o,16) for _,m,o in core.values() if m=='CALL' and o.startswith('0x')})
    accepted={x['entry_va'] for x in json.loads((ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_text())['functions']}
    def cleanup(address,seen=()):
        assert address not in seen
        f=functions[f'{address:08x}'];ranges=[(int(a,16),int(b,16)) for a,b in f['ranges']]
        body={a:v for a,v in instructions.items() if any(x<=a<=y for x,y in ranges)}
        returns={int(o,16) if o else 0 for _,m,o in body.values() if m=='RET'}
        for _,m,o in body.values():
            if m=='JMP' and o.startswith('0x') and int(o,16) not in body:
                returns.update(cleanup(int(o,16),seen+(address,)))
        assert len(returns)==1,(hex(address),returns)
        return returns
    pops={a:next(iter(cleanup(a))) for a in targets}
    indirect={0x4d3a76:4,0x4d3a81:0,0x4d3a8c:0,0x4d4119:0,0x4d52c8:0,
              0x4d5303:0,0x4d5319:4,0x4d532e:4,0x4d5343:4,0x4d53e4:0}
    table=list(struct.unpack('<4I',raw(0x4d55b0,16)))
    def depths(assume_cdecl):
        work=[(0x4d3420,0)];at={};conflicts=[];returns=[]
        while work:
            address,depth=work.pop()
            if address in at:
                if at[address]!=depth:conflicts.append({'va':f'{address:08x}','depths':[at[address],depth]})
                continue
            at[address]=depth;code,m,o=core[address];after=address+len(code)
            if m=='PUSH':depth-=4
            elif m=='POP':depth+=4
            elif m in ['ADD','SUB'] and o.startswith('ESP,'):depth+=(1 if m=='ADD' else -1)*int(o.split(',')[1],16)
            elif m=='CALL':depth+=0 if assume_cdecl else pops[int(o,16)] if o.startswith('0x') else indirect[address]
            if m=='RET':returns.append({'va':f'{address:08x}','depth_before_return':depth,'callee_cleanup':int(o,16)});continue
            if m=='JMP':dest=[int(o,16)] if o.startswith('0x') else table
            elif m.startswith('J'):dest=[int(o,16),after]
            else:dest=[after]
            work.extend((a,depth) for a in dest)
        return at,conflicts,returns
    wrong,wrong_conflict,wrong_return=depths(True)
    at,conflicts,returns=depths(False)
    assert len(at)==len(core) and not conflicts and returns[0]['depth_before_return']==0
    callees=[]
    for a in targets:
        f=functions[f'{a:08x}']
        callees.append({'va':f'{a:08x}','registered':f'{a:08x}' in accepted,'indexed_bytes':f['body_bytes'],
            'stack_cleanup_bytes':pops[a],'original_ranges':[{'first':x,'last':y,'sha256':hashlib.sha256(raw(int(x,16),int(y,16)+1-int(x,16))).hexdigest()} for x,y in f['ranges']]})
    pins=[{'va':f'{a:08x}','bytes':n,'sha256':hashlib.sha256(raw(a,n)).hexdigest()} for a,n in [(0x4d3420,8589),(0x4d55b0,16),(0x4155a6,19),(0x4b6c50,16)]]
    report={'schema':1,'kind':'static-navigation-and-stack-evidence-not-recovery','module_sha256':SHA,
        'function_va':'004d3420','indexed_bytes':8589,'instructions':len(core),'direct_calls':sum(m=='CALL' and o.startswith('0x') for _,m,o in core.values()),
        'distinct_direct_callees':len(targets),'indirect_calls':[{ 'call_va':f'{a:08x}','assumed_cleanup':n,'status':'caller-CFG-consistent; actual-target ABI still requires tracing'} for a,n in indirect.items()],
        'jump_table':{'va':'004d55b0','targets':[f'{a:08x}' for a in table]},'pins':pins,'callees':callees,
        'cdecl_hypothesis':{'conflicts':wrong_conflict,'returns':wrong_return},
        'original_RET_hypothesis':{'conflicts':conflicts,'returns':returns,'all_instructions_reached_by_static_CFG':True},
        'stack_depth_at_instruction':{f'{a:08x}':n for a,n in sorted(at.items())}}
    (RUN/'stack-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    # The constructor's actual vptr resolves three adjacent virtual calls.
    # These bodies are absent even from indexed ranges; this evidence does not
    # add them to the shared index or claim their recovery.
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    decoder=Cs(CS_ARCH_X86,CS_MODE_32)
    virtual_targets=[]
    for first,last,slot in [(0x4d7fd0,0x4d81bf,0x54),(0x4e0880,0x4e088f,0x6c),(0x4e09a0,0x4e09bf,0x78)]:
        seen={};work=[first];returns=[]
        while work:
            a=work.pop()
            if a in seen:continue
            assert first<=a<=last
            ins=next(decoder.disasm(raw(a,15),a));seen[a]=ins
            if ins.mnemonic=='ret':
                returns.append({'va':f'{a:08x}','bytes_hex':ins.bytes.hex(),'stack_cleanup':int(ins.op_str,16) if ins.op_str else 0});continue
            if ins.mnemonic=='jmp':dest=[int(ins.op_str,16)]
            elif ins.mnemonic.startswith('j'):dest=[int(ins.op_str,16),a+ins.size]
            else:dest=[a+ins.size]
            assert all(first<=n<=last for n in dest)
            work.extend(dest)
        cell=0x5b6888+slot;assert struct.unpack('<I',raw(cell,4))[0]==first
        runs=[]
        for a in sorted(seen):
            end=a+seen[a].size
            if runs and runs[-1][1]==a:runs[-1][1]=end
            else:runs.append([a,end])
        virtual_targets.append({'slot':f'{slot:x}','vtable_cell_va':f'{cell:08x}','vtable_cell_hex':raw(cell,4).hex(),
            'target_va':f'{first:08x}','indexed':False,'instructions':len(seen),'returns':returns,
            'ranges':[{'start_va':f'{a:08x}','last_va_inclusive':f'{z-1:08x}','bytes':z-a,
                'sha256':hashlib.sha256(raw(a,z-a)).hexdigest()} for a,z in runs]})
    (RUN/'virtual-target-evidence.json').write_text(json.dumps({'schema':1,'kind':'unindexed-target-navigation-not-body-recovery',
        'module_sha256':SHA,'constructor_vptr_store_va':'004d7e7b','constructor_vptr_store_hex':raw(0x4d7e7b,6).hex(),
        'vtable_va':'005b6888','targets':virtual_targets},indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['instructions','direct_calls','distinct_direct_callees']}))
    print('cdecl_conflicts',len(wrong_conflict),'original_RET_conflicts',len(conflicts),'end_depth',returns[0]['depth_before_return'])

if __name__=='__main__':main()

"""Differential oracle for complete network session and connection teardown."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from v2_source_dependencies import source_hashes

ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE,STACK,EXIT=0x400000,0x2201000,0x222F000
B=0x23000000
S,S2,D,D2,N,N2,K,K2,M,M2,L,P,W,TK,REF,C=[B+x for x in (
    0,0x400,0x800,0x900,0xA00,0xB00,0x1000,0x1010,0x2000,0x2200,0x3000,0x5000,0x6000,0x6020,0x6100,0x7000)]
FUNCTIONS={0:(0x492260,42),1:(0x491FC0,664),2:(0x48B310,39),3:(0x493130,79),4:(0x48B250,192)}
RANGES=((B,0xC20),(K,0x20),(M,0x400),(L,0x1000),(P,0x800),(W,0x160),(C,4))
BOUNDARIES={0x5322B0:(1,0),0x5322C0:(1,0),0x5322D0:(1,0),0x59F050:(1,0),
    0x531F90:(1,0),0x55BFD0:(1,0),0x492770:(1,4),0x55D1B0:(1,0),0x55D9B0:(0,0)}


def cases():
    result=[]
    def add(op,*args):result.append([op,*args,*([0]*(12-len(args)))])
    for active in (0,1,255):
        for mutation in (0,4,8,12):add(0,3,0,active,1,mutation)
    for count in (0,1,3,6):
        for pattern in range(4):
            for active,mode in ((0,1),(1,1),(0,2),(255,2)):add(1,count,pattern,active,mode)
    for count in (0,3):add(1,count,0,0,0)
    for mutation in (1,2,3,4,8,16,32,64,128,256,512,1024,2047):add(1,6,1,1,2,mutation)
    for mutation in (0,4,8,12,512,520):add(2,3,0,1,1,mutation)
    for count in (0,1,3,6):
        for mutation in (0,1,2,3):add(3,count,0,0,0,mutation)
    for count in (0,1,3,6):
        for mode in (1,2):add(4,count,0,0,mode)
    for mutation in (1,2,3,64,128,192,256,512,963):add(4,6,0,0,2,mutation)
    return result


def original(module,image,case):
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,
        UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    assert uc.mem_read(0x628C78,4)==bytes(4)
    assert uc.mem_read(0x5D07D0,1)==b'\x01'
    uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000)
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    def put(va,v):uc.mem_write(va,struct.pack('<I',v&0xFFFFFFFF))
    def byte(va):return uc.mem_read(va,1)[0]
    def pb(va,v):uc.mem_write(va,bytes([v&255]))
    def head(group):return L+group*0x100
    def node(group,i):return head(group)+0x20+i*0x10
    def payload(group,i):return P+group*0x100+i*0x20
    def init_list(group,count,pattern):
        h=head(group);put(h,node(group,0) if count else h);put(h+4,node(group,count-1) if count else h)
        for i in range(count):
            item=node(group,i);put(item,node(group,i+1) if i+1<count else h);put(item+4,node(group,i-1) if i else h)
            value=payload(group,i)
            if pattern==1:value=payload(group,i%3)
            if pattern==2 or (pattern==3 and i%2==0):value=0
            put(item+8,value)
    op,*a=case;uc.mem_write(B,b'\xCC'*0x10000);pool_count=enter_count=0
    for session in (S,S2):
        put(session,D);put(session+8,0x25000008);put(session+0xC,0x2500000C);put(session+0x10,0x25000010)
        for i in range(6):put(session+0x164+i*4,head(i))
        pb(session+0x17D,0x55);pb(session+0x17E,a[2])
    for conn in (D,D2):
        put(conn,0x11111111);put(conn+4,0x29000000);put(conn+8,0x28000088)
        put(conn+0xC,N if a[3]==2 else 0);put(conn+0x10,0x25000020);pb(conn+0x16,0x66);put(conn+0x18,head(6))
    for nested in (N,N2):
        put(nested,0x22222222);put(nested+4,0x29000001);put(nested+8,0x28000099);put(nested+0xC,head(7))
    if op==1 and a[3]==0:put(S,0)
    put(K,0x28001000);put(K2,0x28001001);put(TK,0x28002000);put(W,head(10));put(C,M)
    for manager in (M,M2):
        put(manager+0x28,0x27000000 if manager==M else 0x27000001)
        put(manager+0x38,0x26000000 if manager==M else 0x26000001);put(manager+0xB0,0x26001000)
    for group in range(11):init_list(group,a[0],a[1])
    for i in range(a[0]):put(node(10,i)+8,REF+i*0x10);put(REF+i*0x10,payload(3,i%3))
    put(0x628C60,W);put(0x628C64,TK);put(0x628C74,S);put(0x628C78,K);pb(0x5D07D0,0);put(0x5E4FE8,M)
    for i in range(8):put(0x6B7C20+i*4,0x4906B0 if i%3==0 else 0x410000+i)
    receiver=S if op==1 else W if op==3 else D
    if op==3:put(W,head(0))
    put(STACK,EXIT);uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receiver)
    saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def event(va,values):
        trace.append([va,*values,get(0x628C74),get(0x628C78),byte(0x5D07D0),byte(S+0x17D),byte(S+0x17E),get(S),get(S+8),get(S+0xC),get(S+0x10),
            get(D),get(D+4),get(D+8),get(D+0xC),get(D+0x10),byte(D+0x16),get(N),get(N+8),get(M+0x38),get(M2+0x38),get(C)])
    def hook(machine,address,size,data):
        nonlocal pool_count,enter_count
        if address==EXIT:machine.emu_stop();return
        if address not in BOUNDARIES:return
        argc,pop=BOUNDARIES[address];sp=machine.reg_read(UC_X86_REG_ESP);values=[get(sp+4+i*4) for i in range(argc)]
        if address==0x492770:values.insert(0,machine.reg_read(UC_X86_REG_ECX))
        event(address,values);result=0
        if address==0x5322B0:
            handle=values[0];enter_count+=1
            if enter_count==1 and a[4]&4:put(0x628C78,K2);put(K,0x28001111)
            if 0x27000000<=handle<0x27010000:
                pool_count+=1;captured=M if get(M+0x28)==handle else M2
                if a[4]&1:put(C,M2 if get(C)==M else M);put(0x5E4FE8,get(C))
                if a[4]&2:put(captured+0x38,0x26010000+pool_count);put(captured+0xB0,0x26011000+pool_count);put(captured+0x28,0x27001000+pool_count)
        elif address==0x5322C0:
            if a[4]&512:put(D+8,0x28009999);put(N+8,0x28008888)
        elif address==0x59F050:
            value=values[0];result=0x13579BDF
            if a[4]&16 and value==0x25000010:put(S+0xC,0x2500010C);put(S+8,0x25000108)
            if a[4]&64 and value==0x25000020:put(D+0xC,N2)
            if a[4]&1024:put(0x628C74,S2)
        elif address==0x531F90:result=0x2468ACE0
        elif address==0x5322D0:
            if a[4]&256:put(0x628C78,K)
        elif address==0x55BFD0:
            if a[4]&8:put(D+4,0x29009999);put(D+8,0x28007777);pb(S+0x17E,0x77)
        elif address==0x492770:
            receiver,value=values
            for off in (0x164,0x16C):
                h=get(receiver+off);current=get(h)
                while current!=h:
                    if get(current+8)==value:
                        next_node,prev=get(current),get(current+4);put(prev,next_node);put(next_node+4,prev);break
                    current=get(current)
            if a[4]&32:put(0x628C78,K2);put(S,0)
        elif address==0x55D1B0:
            if a[4]&128:put(N+0xC,head(8));put(N2+0xC,head(8));put(N+8,0x28006666);put(N2+8,0x28006666)
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4+pop);machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start,_=FUNCTIONS[op]
    try:uc.emu_start(start,EXIT+1,count=400000)
    except Exception as error:raise RuntimeError(f'x86 fault {case}, EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace}') from error
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    state=[]
    for va,size in RANGES:state+=list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
    state.extend([get(0x628C74),get(0x628C78),byte(0x5D07D0)])
    state.extend(get(0x6B7C20+i*4) for i in range(8))
    return {'trace':trace,'state':state}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-session-155/bin/Release/network_session_probe.exe')
    parser.add_argument('--report-dir',type=Path,required=True)
    args=parser.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
    module=next(x for x in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if x['file']=='Porsche.exe')
    image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    all_cases=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in all_cases),text=True,capture_output=True,check=True)
    actuals=[json.loads(line) for line in run.stdout.splitlines()];assert len(actuals)==len(all_cases)
    summaries=[]
    for i,(case,actual) in enumerate(zip(all_cases,actuals)):
        expected=original(module,image,case)
        for key in ('trace','state'):
            if expected[key]!=actual[key]:
                diffs=[(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y]
                raise AssertionError(f'case {i} {case} {key}: {diffs[:6]}; x86trace={expected["trace"]}; native trace={actual["trace"]}')
        summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        pos=s['raw_offset']+rva-s['rva'];return image[pos:pos+size]
    assert raw(0x492284,5)==b'\xe9\x87\x90\xff\xff'
    base='iterations/v2/001-original-recovery/'
    names=['network_session','network_services','network_cleanup','network_lifecycle','context_effects']
    compiled=[base+'source/recovered/network_session_probe.cpp']+[base+'source/recovered/Porsche.exe/'+n+'.cpp' for n in names]
    paths=compiled+[base+'runs/155-network-session/'+p for p in ('README.md','CMakeLists.txt')]+[
        'scripts/research/verify-v2-network-session.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    refs=[json.loads(line) for line in (ROOT/paths[-2]).read_text().splitlines()]
    storage_refs=[r for r in refs if r.get('to_va') in ('00628c78','005d07d0')]
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,
        'function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],
        'full_function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'partial_function_vas':[],
        'cases':len(all_cases),'native_cpp_equal_original_x86':True,
        'comparison_boundary':'Complete 492260/491fc0/48b310/493130/48b250 bodies; real recovered 48b660/48c430/48aed0/560180/4237d0 callees. Exact worker/lock/free order, arguments/intermediate state, full session/connection/list/reference/pool backing and callback slots; original nonvolatile registers/ESP. Scripted opaque 492770 effects remove one matching node per list only in the private fixture, without claiming original callee semantics.',
        'index_query':'Run145 session boundaries492260/491fc0, all callers/callees, full ASM; shared48b310, list helper493130 and wrapper48b250. Trace every628c78/5d07d0 reference, constructor491cd0 stores and original initial data.',
        'unresolved_effects':['00492770 thiscall(session,member) RET4','0055bfd0 cdecl(worker)','0055d1b0 cdecl(worker)','005322b0','005322c0','005322d0','00531f90','0059f050'],
        'new_storage':[{'va':'00628c78','bytes':4,'initial':0,'meaning':'allocated session lock cell pointer','write_va':'00491de0'},
            {'va':'005d07d0','bytes':1,'initial':1,'meaning':'session stopped byte','clear_va':'00491df1'}],
        'storage_references':storage_refs,
        'deferred':['00492770 member removal and0055bfd0 worker body','005b4978/005b4970 and prior005b4968 vtable canonical relocations','0048dcb0 poll/0048e1a0 wait','005e8bfc table extent/owner and005e8e50 alias backlog unchanged'],
        'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size in FUNCTIONS.values()],
        'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))


if __name__=='__main__':main()

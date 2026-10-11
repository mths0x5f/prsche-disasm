"""Original x86 oracle for worker shutdown, queues and member removal."""
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
W,MSG,S,D,P,G,R,SENDER,VT,M,M2,L,OUT,C,F=[B+x for x in (
    0,0x1000,0x2000,0x2300,0x2400,0x3000,0x4000,0x4020,0x4040,0x5000,0x5200,0x6000,0x7000,0x7010,0x8000)]
GLOBAL,THREAD,ACTIVE=0x6A3B60,0x6A3D30,0x6A4660
FUNCTIONS={0:(0x55BFD0,136,0),1:(0x55D1B0,131,0),2:(0x55D9B0,94,0),
    3:(0x580050,44,0),4:(0x580080,39,0),5:(0x580020,46,0),6:(0x55C060,70,0),
    7:(0x5806C0,32,0),8:(0x5809F0,7,0),9:(0x492770,570,4),10:(0x48B5A0,101,4),
    11:(0x48A7A0,283,0),12:(0x529050,11,4),13:(0x50E140,13,4),14:(0x4937F0,107,12)}
RANGES=((W,0x300),(MSG,0x200),(S,0x600),(G,0xD00),(R,0x50),(M,0x400),(L,0x900),(OUT,0x20),(F,0x100),(GLOBAL,0x1D0),(THREAD,28))
BOUNDARIES={0x5322B0:(1,0),0x5322C0:(1,0),0x5322D0:(1,0),0x59F050:(1,0),0x531F90:(1,0),
    0x55F780:(1,0),0x5366E0:(1,0),0x55F740:(1,0),0x55FB30:(1,0),0x55FC10:(1,0),
    0x55FA10:(2,0),0x59EEB0:(2,0),0x48BDA0:(1,4),0x24000000:(3,12)}


def cases():
    result=[]
    def add(op,*args):result.append([op,*args,*([0]*(12-len(args)))])
    for op in (0,1,2):
        for active in (0,2,0x12340000):add(op,0,1,0,active)
        for count in (1,3):add(op,count,1,0,0x12340001)
        for delay in (1,2,3):
            for pump in (0,1):add(op,0,delay,pump,0x12340001)
        for mutation in (1,4,8,16,32,64,127):add(op,0,2,1,0x12340001,mutation)
    for count in (0,1,3):
        for mutation in (0,1,4,5):add(3,count,0,0,0,mutation)
    add(3,1,0,0,0,0,1)
    for null in (0,1):
        for mutation in (0,1,32,33):add(4,1,0,0,0,mutation,null)
    for mode in range(4):add(5,3,0,0,0,0,mode)
    for flags in (0,1,2,3,0x80000002):add(7,1,0,0,flags)
    for flags in (0,2,3):add(6,0,0,0,flags)
    for count in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):add(8,count)
    for count in (0,1,3,6):
        for branch in range(6):add(9,count,branch,1,1)
    for count in (1,6):
        for signed in (0,0xFFFFFFFF,0x80000000):add(9,count,2,signed,0)
    for gate in (1,2):add(9,6,4,1,1,0,1,gate)
    for counter in (0,2,0xFFFFFFFF):add(9,6,4,1,counter,0,1)
    for mutation in (1,2,3,128,1024,2048,2178):add(9,6,4,1,1,mutation,1)
    for count in (0,1,6):
        for signed in (0,1,0xFFFFFFFF,0x80000000):add(10,count,0,signed,0,0,1)
    for mutation in (1,2,3):add(10,6,0,1,0,mutation,1)
    for count in (0,1,6):
        for mutation in (0,1,2,3):add(11,count,0,0,0,mutation)
    for alias in (0,1):add(12,1,alias);add(13,1,alias)
    for grow in (0,1):
        for alias in (0,1):
            for mutation in (0,1,2,256,512,770):add(14,3,alias,0,0,mutation,grow)
    return result


def original(module,image,case):
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,
        UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    assert uc.mem_read(GLOBAL,0x1D0)==bytes(0x1D0) and uc.mem_read(THREAD,28)==bytes(28) and uc.mem_read(ACTIVE,4)==bytes(4)
    uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000);uc.mem_map(0x24000000,0x1000)
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    def put(va,v):uc.mem_write(va,struct.pack('<I',v&0xFFFFFFFF))
    def byte(va):return uc.mem_read(va,1)[0]
    def pb(va,v):uc.mem_write(va,bytes([v&255]))
    def head(group):return L+group*0x100
    def node(group,i):return head(group)+0x20+i*0x10
    def init_list(group,count,value):
        h=head(group);put(h,node(group,0) if count else h);put(h+4,node(group,count-1) if count else h)
        for i in range(count):
            put(node(group,i),node(group,i+1) if i+1<count else h);put(node(group,i)+4,node(group,i-1) if i else h)
            put(node(group,i)+8,P+0x20 if a[5] and i%2 else value)
    def queue(q,count,lock):
        put(q,count);put(q+4,0x12340002);put(q+8,MSG if count else 0);put(q+0xC,MSG+(count-1)*0x20 if count else 0);put(q+0x18,lock)
        for i in range(count):put(MSG+i*0x20,MSG+(i+1)*0x20 if i+1<count else 0);put(MSG+i*0x20+4,0xAAAAAAAA+i)
    op,*a=case;uc.mem_write(B,b'\xCC'*0x10000);uc.mem_write(GLOBAL,b'\xCC'*0x1D0);uc.mem_write(THREAD,b'\xCC'*28)
    pool_count=enter_count=sleep_count=0;put(ACTIVE,a[3]);count=0 if op==8 else a[0]
    queue(W+0x198,count,0x28000000);queue(W+0x1B4,0,0x28000001);put(W+0x194,0x28000002)
    queue(GLOBAL+0x198,count,0x28000010);queue(GLOBAL+0x1B4,0,0x28000011);put(GLOBAL+0x194,0x28000012)
    for off in (0x244,0x260,0x298,0x27C,0x2B4):queue(W+off,0,0x28000100+off)
    put(W+0x240,a[3]);put(W+0x248,a[3])
    if op==8:put(W+0x198,a[0])
    if op==7:put(W+0x19C,a[3])
    if op==5:put(W+0x19C,2 if a[5]&1 else 0);put(W+0x1B8,2 if a[5]&2 else 0)
    if op==3 and a[5]:put(W+0x198,0xFFFFFFFF)
    put(C,M);put(0x5E4FE8,M)
    for manager in (M,M2):put(manager+0x28,0x27000000 if manager==M else 0x27000001);put(manager+0x38,F);put(manager+0xB0,0x26000000)
    for i in range(6):put(F+i*0x20+4,F+(i+1)*0x20 if i+1<6 else 0);put(F+i*0x20,0xAAAAAAAA)
    put(S,D);put(S+0xC,R);put(S+0x10,R);put(S+0x154,a[3]);put(S+0x158,0x1234);put(S+0x15C,a[3])
    put(D+8,0x28000200);pb(D+0x14,0);put(D+0x10,R);put(D+0x18,head(0))
    for i in range(6):put(S+0x164+i*4,head(i+1))
    put(P+0xA4,G if a[1]>=3 else 0);put(P+0xAC,0x12345678);put(P+0xB4,a[2]);pb(P+0xB8,1 if a[1]==0 else 0);pb(P+0xBD,1 if a[1]==1 else 0)
    put(P+0xC8,head(7));put(P+0xC4,head(8));pb(G+0xCC3,0 if a[1]==5 else 1)
    if a[6]==1:pb(D+0x14,1)
    if a[6]==2:put(D+0x10,0)
    for i in range(9):init_list(i,a[0] if op>=9 else 0,G if i==6 else G+0x20 if i==5 else P)
    put(R,SENDER);put(R+4,0);put(SENDER,VT);put(VT,0x24000000)
    for i in range(8):put(0x6B7C20+i*4,0x410000+i if i%3 else 0x490640)
    put(0x628C60,0);put(OUT,0xDDDDDDDD);put(OUT+4,0xABCDEF12)
    if op==14 and a[5]:put(M+0x38,0)
    receiver=0xCCCCCCCC;stack_args=[]
    if op in (0,1,3,5,6):stack_args=[W]
    elif op==4:stack_args=[W,0 if a[5] else MSG]
    elif op in (7,8):stack_args=[W+0x198]
    elif op==9:receiver=S;stack_args=[P]
    elif op==10:receiver=D;stack_args=[P]
    elif op==11:receiver=P
    elif op==12:receiver=S+0x174;stack_args=[S+0x174 if a[1] else OUT]
    elif op==13:receiver=OUT+4 if a[1] else OUT;stack_args=[OUT+4]
    elif op==14:receiver=S+0x174;stack_args=[F+4 if a[1] else OUT,head(5),OUT+4]
    put(STACK,EXIT)
    for i,value in enumerate(stack_args):put(STACK+4+i*4,value)
    uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receiver)
    saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def event(va,values):
        trace.append([va,*values,get(W+0x240),get(W+0x248),get(ACTIVE),get(W+0x194),get(W+0x198),get(GLOBAL+0x198),
            get(M+0x38),get(M+0xB0),get(M2+0x38),get(M2+0xB0),get(C),get(S+0x154),get(S+0x15C),get(P+0xA4),byte(G+0xCC3)])
    def hook(machine,address,size,data):
        nonlocal pool_count,enter_count,sleep_count
        if address==EXIT:machine.emu_stop();return
        if address not in BOUNDARIES:return
        argc,pop=BOUNDARIES[address];sp=machine.reg_read(UC_X86_REG_ESP);values=[get(sp+4+i*4) for i in range(argc)];result=0
        if address==0x24000000:
            dest,packet,bytes_count=values;trace.append([address,machine.reg_read(UC_X86_REG_ECX),dest,bytes_count,*uc.mem_read(packet,bytes_count)])
            if a[4]&2048:put(P+0xA4,0)
        else:
            if address==0x48BDA0:values.insert(0,machine.reg_read(UC_X86_REG_ECX))
            if address==0x55F740:values.append(1)
            event(address,values)
            if address==0x5322B0:
                handle=values[0];enter_count+=1
                if a[4]&1:put(W+0x1B0,0x28110000+enter_count);put(W+0x1CC,0x28120000+enter_count);put(GLOBAL+0x1B0,0x28130000+enter_count)
                if a[4]&4:put(W+0x240,get(W+0x240)|0x100);put(W+0x248,get(W+0x248)|0x100)
                if 0x27000000<=handle<0x27010000:
                    pool_count+=1
                    if a[4]&2:put(C,M2 if get(C)==M else M);put(0x5E4FE8,get(C))
            elif address==0x5322C0:
                if a[4]&256:put(OUT+4,0xABCDEF01)
            elif address==0x59F050:
                result=0x13579BDF
                if a[4]&1024:pb(G+0xCC3,0x42)
            elif address==0x531F90:result=0x2468ACE0
            elif address==0x55F780:result=a[2]
            elif address==0x5366E0:
                result=1
                if a[4]&8:put(W+0x240,get(W+0x240)|0x200);put(W+0x248,get(W+0x248)|0x200)
            elif address==0x55F740:
                sleep_count+=1;result=0x99
                if sleep_count>=a[1]:queue(W+0x198,1,0x28000000);queue(GLOBAL+0x198,1,0x28000010)
                if a[4]&16:put(ACTIVE,7);put(W+0x194,0x28116666)
            elif address==0x55FB30:
                result=0x17
                if a[4]&32:put(W+0x194,0x28223344)
            elif address==0x55FC10:result=0x18
            elif address==0x55FA10:
                result=1
                if a[4]&64:put(W+0x19C,0);put(W+0x1B0,0x28334455);put(W+0x1B8,2);put(W+0x1CC,0x28445566)
            elif address==0x59EEB0:
                assert values==[1,0];put(M+0x38,F+0x80);put(M2+0x38,F+0x80)
                if a[4]&512:put(C,M2);put(0x5E4FE8,M2)
            elif address==0x48BDA0:
                if a[1]==4 or a[4]&128:pb(G+0xCC3,0)
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4+pop);machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start,_,pop=FUNCTIONS[op]
    try:uc.emu_start(start,EXIT+1,count=400000)
    except Exception as error:raise RuntimeError(f'x86 fault {case}, EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace}') from error
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4+pop
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    state=[]
    for va,size in RANGES:state+=list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
    state.append(get(ACTIVE));state.extend(get(0x6B7C20+i*4) for i in range(8))
    return {'result':uc.reg_read(UC_X86_REG_EAX) if op in (3,4,5,8,12,13,14) else 0,'trace':trace,'state':state}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-workers-members-159/bin/Release/network_workers_members_probe.exe')
    parser.add_argument('--report-dir',type=Path,required=True)
    args=parser.parse_args();args.report_dir.mkdir(parents=True,exist_ok=True)
    module=next(x for x in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if x['file']=='Porsche.exe')
    image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    all_cases=cases();run=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,c))+'\n' for c in all_cases),text=True,capture_output=True,check=True)
    actuals=[json.loads(line) for line in run.stdout.splitlines()];assert len(actuals)==len(all_cases)
    summaries=[]
    for i,(case,actual) in enumerate(zip(all_cases,actuals)):
        expected=original(module,image,case)
        for key in ('result','trace','state'):
            if expected[key]!=actual[key]:
                diffs=[(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x!=y] if key!='result' else [(expected[key],actual[key])]
                raise AssertionError(f'case {i} {case} {key}: {diffs[:5]}; x86trace={expected["trace"][:20]}; native trace={actual["trace"][:20]}')
        summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        pos=s['raw_offset']+rva-s['rva'];return image[pos:pos+size]
    for va,pop in ((0x529058,4),(0x50E14A,4),(0x493858,12),(0x4929A7,4),(0x48B602,4)):assert raw(va,3)==b'\xc2'+struct.pack('<H',pop)
    base='iterations/v2/001-original-recovery/'
    names=['network_workers_members','network_session','network_services','network_cleanup','network_lifecycle','context_effects','io_lists','io_worker_lists','file_events']
    compiled=[base+'source/recovered/network_workers_members_probe.cpp']+[base+'source/recovered/Porsche.exe/'+n+'.cpp' for n in names]
    paths=compiled+[base+'runs/159-network-workers-members/'+p for p in ('README.md','CMakeLists.txt')]+[
        'scripts/research/verify-v2-network-workers-members.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    refs=[json.loads(line) for line in (ROOT/paths[-2]).read_text().splitlines()]
    storage_refs=[r for r in refs if len(r.get('to_va',''))==8 and all(c in '0123456789abcdef' for c in r['to_va'])
        and (GLOBAL<=int(r['to_va'],16)<THREAD+28 or int(r['to_va'],16)==ACTIVE)]
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,
        'function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],
        'full_function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'partial_function_vas':[],
        'cases':len(all_cases),'native_cpp_equal_original_x86':True,
        'comparison_boundary':'15 complete bodies with real recovered 48b660/493180/4c3150/48c870/560180 and io_pop580790/io_prepend5806e0. Exact initialized packet bytes, boundary arguments/order/state, full worker/session/member/list/queue/manager backing and callback slots, output aliases/returned pointer, original ESP/nonvolatile registers and RET4/12. Static data pointers are explicitly normalized to original addresses. Opaque group/OS/thread/grow effects are scripted private boundaries.',
        'index_query':'Unresolved Run151/155 492770/55bfd0/55d1b0/55d9b0 and complete callers/callees; queue wrappers580050/580080/580020, disposal55c060/5806c0/count5809f0, member helpers48b5a0/48a7a0/529050/50e140/4937f0. Static worker references and generic57ffc0 plus thread-create consumer establish known typed storage extents.',
        'unresolved_effects':['0048bda0 thiscall(group,member) RET4','0055f780 canonical current-thread provider','005366e0 canonical timed-callback provider','0055fa10 canonical thread-wait provider','0059eeb0 canonical pool-grow provider','existing heap/free/event/sleep platform providers'],
        'new_storage':[{'va':'006a3b60','bytes':0x1D0,'initial':0,'meaning':'opaque prefix + event + two canonical28-byte IoLists','evidence':'0055d800 ->0057ffc0 initializes lists+198/+1b4, event+194'},
            {'va':'006a3d30','bytes':28,'initial':0,'meaning':'canonical ThreadRecord','evidence':'0055d7a0 ->0055f420; stop passes same record to0055fa10'},
            {'va':'006a4660','bytes':4,'initial':0,'meaning':'worker-active DWORD','writers':['0055d818','0055d996','0055d9be']}],
        'storage_references':storage_refs,
        'deferred':['0048bda0 and005e8e50 string/alias consumer','existing vtable identity canonical relocations','0048dcb0 poll/0048e1a0 wait','005e8bfc table extent/owner'],
        'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size,_ in FUNCTIONS.values()],
        'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))


if __name__=='__main__':main()

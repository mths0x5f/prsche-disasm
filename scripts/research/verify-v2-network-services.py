"""Compare network message serialization/action/list cleanup with original x86."""
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
N,N2,R,R2,S,S2,V,V2,W,L,P,M,M2,T,K,O,Q,C=[B+x for x in (
    0,0x1000,0x2000,0x2010,0x2100,0x2110,0x2200,0x2210,0x2300,
    0x3000,0x5000,0x7000,0x8000,0xA000,0xB000,0xB010,0xB014,0xB018)]
FUNCTIONS={0:(0x48C870,0x10C,20),1:(0x48DA60,0x63,0),
    2:(0x48B660,0x42,8),3:(0x493180,0x3C,4),4:(0x48E790,0x229,0)}
RANGES=((N,0x268),(N2,0x268),(R,0x18),(S,0x14),(V,0x14),(W,4),
    (L,0x500),(P,0x300),(M,0x100),(M2,0x100),(T,0x400),(K,4),(O,12))
BOUNDARIES={0x5322B0:(1,0,False),0x5322C0:(1,0,False),
    0x59F050:(1,0,False),0x531F90:(1,0,False),0x48C430:(0,0,True),
    0x4904D0:(0,0,True),0x4C3150:(1,4,True)}


def cases():
    result=[]
    def add(op,*args):result.append([op,*args,*([0]*(12-len(args)))])
    for first in (0x80000000,0,0x12345678,0xFFFFFFFF):
        for second in (0x80000000,0,0x87654321,0xFFFFFFFF):
            for text in (0xFFFFFFFF,0,3):add(0,0x1234,first,second,text,0xDEADBEEF,3)
    for text in (190,191,192,197,198,199,200,450):
        for first,second in ((0x80000000,0x80000000),(0xFFFFFFFF,0xFFFFFFFF)):
            add(0,0xB7,first,second,text,0x12345678,0)
    for count in (0,1,3,0xFFFFFFFF):add(0,0xBA,0x80000000,0x80000000,0xFFFFFFFF,0,count)
    for mutation in (1,2,4,8,9,15):add(0,0xB7,0xFFFFFFFE,0xFFFFFFFF,5,0,3,mutation)
    for gate in (0,1,2,3):add(1,0xFFFFFFFE,0xFFFFFFFF,gate,3)
    for mutation in (1,2,4,8,16,32,63):add(1,0xFFFFFFFE,0xFFFFFFFF,1,3,0,0,mutation)
    for index in (0,1,2):
        for alias in (0,1,2):add(2,3,index,alias)
    for mutation in (128,256,384):add(2,3,1,0,0,0,0,mutation)
    for count in (0,1,3,6):
        for match in (0,1,2,5):add(3,count,match)
    for mutation in (64,128,256,448):add(3,6,1,0,0,0,0,mutation)
    for count in (0,1,3,6):
        for pattern in (0,1,2,3):add(4,count,pattern)
    for mutation in (128,256,384,512,1023):add(4,6,1,0,0,0,0,mutation)
    return result


def original(module,image,case):
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,
        UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000);uc.mem_map(0x24000000,0x1000)
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    def put(va,v):uc.mem_write(va,struct.pack('<I',v&0xFFFFFFFF))
    def pb(va,v):uc.mem_write(va,bytes([v&0xFF]))
    def node(group,index):return L+group*0x100+0x20+index*0x10
    def payload(group,kind):return P+group*0x40+kind*0x10
    def init_list(group,count,pattern):
        head=L+group*0x100;put(head,node(group,0) if count else head);put(head+4,node(group,count-1) if count else head)
        for i in range(count):
            item=node(group,i);put(item,node(group,i+1) if i+1<count else head);put(item+4,node(group,i-1) if i else head)
            value=payload(group,i%3)
            if pattern==0:value=payload(group,i)
            if pattern==2 or (pattern==3 and i%2==0):value=0
            put(item+8,value)
    op,*a=case;uc.mem_write(B,b'\xCC'*0x10000);send_count=pool_count=0
    for net,receiver,connection in ((N,R,0x26000000),(N2,R2,0x26001000)):
        put(net+8,connection);put(net+0xC,receiver);put(net+0x10,K);pb(net+0xBF,0)
    for receiver in (R,R2):put(receiver,S);put(receiver+4,W)
    put(S,V);put(S2,V2);put(V,0x24000000);put(V2,0x24000010);put(W,L)
    put(K,0x11112222);put(O,0xDDDDDDDD);put(Q,payload(0,1));put(C,M)
    for manager in (M,M2):put(manager+0x28,0x27000000 if manager==M else 0x27000001);put(manager+0x38,0x25000000)
    for group in range(5):
        init_list(group,0,0);put(N+0x254+group*4,L+group*0x100)
        for i in range(6):put(payload(group,i)+4,0x25001000+group*0x100+i*0x10)
    put(0x628C70,N);put(0x5E4FE8,M)
    if op==0:
        count=0 if a[5]==0xFFFFFFFF else a[5];init_list(0,count,0)
        for i in range(count):put(node(0,i)+8,0x12340000+i)
        if a[5]==0xFFFFFFFF:put(R+4,0)
        if a[3]!=0xFFFFFFFF:
            uc.mem_write(T,bytes(0x41+i%50 for i in range(a[3]))+b'\0')
        stack_args=[a[0],a[1],a[2],0 if a[3]==0xFFFFFFFF else T,a[4]];receiver=R
    elif op==1:
        init_list(0,a[3],0)
        for i in range(a[3]):put(node(0,i)+8,0x12340000+i)
        if a[2]==0:put(0x628C70,0)
        if a[2]==2:put(N+8,0)
        if a[2]==3:pb(N+0xBF,1)
        stack_args=[a[0],a[1]];receiver=0xDDDDDDDD
    elif op==2 or op==3:
        init_list(0,a[0],1);put(Q,payload(0,a[1]));receiver=W
        if op==2:
            target=node(0,a[1]);output=target+4 if a[2]==1 else L if a[2]==2 else O
            stack_args=[output,target]
        else:stack_args=[Q]
    else:
        for group in range(5):init_list(group,a[0],a[1])
        stack_args=[];receiver=N
    put(STACK,EXIT)
    for i,value in enumerate(stack_args):put(STACK+4+i*4,value)
    uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receiver)
    saved={UC_X86_REG_EBX:0x11223344,UC_X86_REG_ESI:0x55667788,UC_X86_REG_EDI:0x99AABBCC,UC_X86_REG_EBP:0xDDEEFF00}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def hook(machine,address,_size,_user):
        nonlocal send_count,pool_count
        if address==EXIT:machine.emu_stop();return
        sp=machine.reg_read(UC_X86_REG_ESP)
        if address in (0x24000000,0x24000010):
            destination,packet,length=[get(sp+4+i*4) for i in range(3)]
            trace.append([address,machine.reg_read(UC_X86_REG_ECX),destination,length,*uc.mem_read(packet,length)])
            send_count+=1
            if send_count==1:
                if a[6]&1:put(R,S2);put(R2,S2)
                if a[6]&2:put(node(0,0),L)
                if a[6]&4:put(0x628C70,N2)
                if a[6]&8:pb(packet,uc.mem_read(packet,1)[0]^0xFF)
                if a[6]&16:put(K,0x33334444)
            pop=12;result=0
        elif address in BOUNDARIES:
            argc,pop,member=BOUNDARIES[address];values=[get(sp+4+i*4) for i in range(argc)]
            row=[address,*([machine.reg_read(UC_X86_REG_ECX)] if member else []),*values]
            if address==0x4C3150:row=[address,machine.reg_read(UC_X86_REG_ECX)]
            if address in (0x5322B0,0x5322C0):row += [get(M+0x38),get(M2+0x38),get(L),get(C)]
            trace.append(row);result=0
            if address==0x5322B0:
                handle=values[0]
                if a[6]&32:put(0x628C70,N2)
                if a[6]&16:put(K,0x33334444)
                if 0x27000000<=handle<=0x2700FFFF:
                    pool_count+=1;captured=M if get(M+0x28)==handle else M2
                    if a[6]&128:
                        put(C,M2 if get(C)==M else M);put(0x5E4FE8,get(C))
                    if a[6]&256:
                        put(captured+0x38,0x25010000+pool_count);put(captured+0x28,0x27001000+pool_count)
                        for g in range(5):
                            for i in range(6):put(payload(g,i)+4,0x25008000+g*0x100+i*0x10)
                    if a[6]&64:put(Q,payload(0,2))
            if address in (0x59F050,0x531F90):result=1
            if address==0x59F050 and a[6]&512:put(N+0xDC,0x76543210);pb(N+0xC3,0x77)
            if address==0x4C3150:
                put(values[0],get(get(machine.reg_read(UC_X86_REG_ECX))));result=values[0]
        else:return
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4+pop);machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start,_,pop=FUNCTIONS[op]
    try:uc.emu_start(start,EXIT+1,count=200000)
    except Exception as error:raise RuntimeError(f'x86 fault{case},EIP={uc.reg_read(UC_X86_REG_EIP):08x},trace={trace}') from error
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4+pop
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    state=[]
    for va,size in RANGES:state+=list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
    state.append(get(0x628C70))
    return {'result':uc.reg_read(UC_X86_REG_EAX) if op==2 else 0,'trace':trace,'state':state}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-services-148/bin/Release/network_services_probe.exe')
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
                raise AssertionError(f'case{i}{case} {key}:{diffs[:6]}; x86trace={expected["trace"]};nativetrace={actual["trace"]}')
        summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        pos=s['raw_offset']+rva-s['rva'];return image[pos:pos+size]
    assert raw(0x48C979,3)==b'\xc2\x14\x00'
    assert raw(0x48B69F,3)==b'\xc2\x08\x00'
    assert raw(0x4931B9,3)==b'\xc2\x04\x00'
    base='iterations/v2/001-original-recovery/'
    compiled=[base+'source/recovered/network_services_probe.cpp',base+'source/recovered/Porsche.exe/network_services.cpp']
    paths=compiled+[base+'runs/148-network-services/'+p for p in ('README.md','CMakeLists.txt')]+[
        'scripts/research/verify-v2-network-services.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,
        'function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],
        'full_function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'partial_function_vas':[],
        'cases':len(all_cases),'native_cpp_equal_original_x86':True,
        'comparison_boundary':'Full48c870/48da60/48b660/493180/48e790 bodies; real action→message and cleanup→unlink/remove_matching. Exact initialized packet bytes/length/virtual receiver/destination/order, full network/list/payload/manager/sender backing, output aliases/return pointer, callbacks mutating sender/list-next/packet/global network/match/pool; original nonvolatile registers/ESP andRET20/8/4.',
        'index_query':'Application_main network boundaries map to48dcb0 poll,48e1a0 wait,48da60 action; query48c870/48e790 and helpers48b660/493180/48c430/4904d0/4c3150, callers/callees and fullASM.',
        'unresolved_effects':['0048c430','004904d0','004c3150','00531f90','005322b0','005322c0','0059f050','sender vtable slot0 thiscall(destination,packet,bytes)'],
        'deferred':['0048dcb0 poll1250bytes','0048e1a0 wait1357bytes','005e8bfc table extent/owner and005e8e50 alias backlog unchanged'],
        'new_storage':[],
        'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size,_ in FUNCTIONS.values()],
        'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))


if __name__=='__main__':main()

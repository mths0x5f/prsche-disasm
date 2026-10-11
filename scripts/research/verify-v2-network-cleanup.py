"""Compare the five complete network cleanup bodies with original Porsche x86."""
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
OBJ,WR,WR2,LOCK,LOCK2,L,L2,P,M,M2,O,C=[B+x for x in (
    0,0x1000,0x1010,0x1100,0x1110,0x2000,0x2200,0x3000,0x4000,0x4200,0x5000,0x5004)]
FUNCTIONS={0:(0x48C430,83,0),1:(0x4904D0,204,0),2:(0x4C3150,13,4),
    3:(0x48C580,177,0),4:(0x48AED0,166,0)}
RANGES=((OBJ,0x100),(WR,0x20),(LOCK,0x20),(L,0x400),(P,0x200),(M,0x400),(O,8))
BOUNDARIES={0x5322B0:1,0x5322C0:1,0x59F050:1,0x531F90:1,
    0x5322D0:1,0x55D9B0:0,0x55D1B0:1}


def cases():
    result=[]
    def add(op,*args):result.append([op,*args,*([0]*(12-len(args)))])
    for count in (0,1,3,6):
        for pattern in range(4):add(0,count,pattern)
    for count in (0,3):add(0,count,1,1)
    for mutation in (4,16,20):add(0,6,2,0,0,mutation)
    for count in (0,1,3,6):
        for pattern in range(4):add(1,count,pattern)
    for mutation in (1,2,3,16,128,512,659):add(1,6,1,0,0,mutation)
    for count in (0,1,6):
        for alias in range(4):add(2,count,0,0,alias)
    for count in (0,1,3,6):
        for mode in range(4):add(3,count,0,mode)
    for mutation in (1,2,3,8,16,32,128,256,512,939):add(3,6,0,0,0,mutation)
    for mode in (1,2,3):add(3,3,0,mode,0,32)
    for count in (0,1,3,6):add(4,count)
    for mutation in (1,2,3,64,512,576,579,256):add(4,6,0,0,0,mutation)
    return result


def original(module,image,case):
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,
        UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(BASE+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    assert uc.mem_read(0x628C60,8)==bytes(8)
    uc.mem_map(0x2200000,0x30000);uc.mem_map(B,0x10000)
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    def put(va,v):uc.mem_write(va,struct.pack('<I',v&0xFFFFFFFF))
    def node(group,i):return L+group*0x200+0x20+i*0x10
    def payload(i):return P+i*0x20
    def init_list(group,count,pattern):
        head=L+group*0x200;put(head,node(group,0) if count else head);put(head+4,node(group,count-1) if count else head)
        for i in range(count):
            item=node(group,i);put(item,node(group,i+1) if i+1<count else head);put(item+4,node(group,i-1) if i else head)
            value=payload(i)
            if pattern==1:value=payload(i%3)
            if pattern==2 or (pattern==3 and i%2==0):value=0
            put(item+8,value)
    op,*a=case;uc.mem_write(B,b'\xCC'*0x10000);pool_count=enter_count=0
    put(OBJ,0x11111111);put(OBJ+4,0x29000000);put(OBJ+8,0x28000088)
    put(OBJ+0xC,L);put(OBJ+0x5C,L);put(WR,L);put(WR2,L2)
    put(LOCK,0x28000000);put(LOCK2,0x28000001);put(C,M);put(O,0xDDDDDDDD)
    for manager in (M,M2):
        put(manager+0x28,0x27000000 if manager==M else 0x27000001)
        put(manager+0x38,0x26000000 if manager==M else 0x26000001)
        put(manager+0xB0,0x26001000 if manager==M else 0x26001001)
    for i in range(8):
        target=OBJ+0x80
        if a[1]==1 or (a[1]==2 and i%2==0):target=OBJ
        if a[1]==3:target=OBJ+0x80 if i%2 else 0
        put(payload(i),target);put(payload(i)+4,0x25001000+i*0x10)
    pattern=0 if op==0 else a[1]
    init_list(0,a[0],pattern);init_list(1,a[0],pattern)
    put(0x628C60,0 if a[2] in (1,3) else WR);put(0x628C64,0 if a[2] in (2,3) else LOCK)
    put(0x5E4FE8,M)
    output=WR if a[3]==1 else L if a[3]==2 else node(0,0)+4 if a[3]==3 else O
    receiver=0 if op==0 and a[1]==3 else WR if op==2 else OBJ
    stack_args=[output] if op==2 else []
    put(STACK,EXIT)
    for i,value in enumerate(stack_args):put(STACK+4+i*4,value)
    uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_ECX,receiver)
    saved={UC_X86_REG_EBX:0x31415926,UC_X86_REG_ESI:0x27182818,UC_X86_REG_EDI:0x16180339,UC_X86_REG_EBP:0x11235813}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def event(va,values):
        trace.append([va,*values,get(0x628C60),get(0x628C64),get(OBJ),get(OBJ+8),get(OBJ+0xC),
            get(WR),get(L),get(L+4),get(L2),get(L2+4),get(M+0x38),get(M+0xB0),get(M2+0x38),get(M2+0xB0),get(C)])
    def hook(machine,address,size,data):
        nonlocal pool_count,enter_count
        if address==EXIT:machine.emu_stop();return
        if address not in BOUNDARIES:return
        sp=machine.reg_read(UC_X86_REG_ESP);values=[get(sp+4+i*4) for i in range(BOUNDARIES[address])]
        event(address,values);result=0
        if address==0x5322B0:
            handle=values[0];enter_count+=1
            if a[4]&16:put(LOCK,0x28112233);put(LOCK2,0x28445566)
            if enter_count==1 and a[4]&4:put(0x628C60,WR2);put(0x628C64,LOCK2)
            if 0x27000000<=handle<0x27010000:
                pool_count+=1;captured=M if get(M+0x28)==handle else M2
                if a[4]&1:put(C,M2 if get(C)==M else M);put(0x5E4FE8,get(C))
                if a[4]&2:
                    put(captured+0x38,0x26010000+pool_count);put(captured+0xB0,0x26011000+pool_count)
                    put(captured+0x28,0x27001000+pool_count)
                    for i in range(8):put(payload(i)+4,0x25008000+i*0x10+pool_count)
                if a[4]&8:put(0x628C60,WR2);put(0x628C64,LOCK2)
        elif address==0x5322C0:
            if a[4]&512:put(OBJ+8,0x28009999);put(OBJ+4,0x29009999)
        elif address==0x59F050:
            result=0x13579BDF
            if a[4]&128:put(0x628C64,LOCK2)
        elif address==0x531F90:result=0x2468ACE0
        elif address==0x5322D0:
            if a[4]&256:put(0x628C60,WR2);put(0x628C64,LOCK)
        elif address==0x55D9B0:
            if a[4]&32:put(0x628C60,WR2);put(0x628C64,LOCK2)
        elif address==0x55D1B0:
            if a[4]&64:put(OBJ+0xC,L2);put(OBJ+8,0x28008888)
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4);machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start,_,pop=FUNCTIONS[op]
    try:uc.emu_start(start,EXIT+1,count=200000)
    except Exception as error:raise RuntimeError(f'x86 fault {case}, EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace}') from error
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4+pop
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    state=[]
    for va,size in RANGES:state+=list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
    state.extend([get(0x628C60),get(0x628C64)])
    return {'result':uc.reg_read(UC_X86_REG_EAX) if op==2 else 0,'trace':trace,'state':state}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-cleanup-151/bin/Release/network_cleanup_probe.exe')
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
                raise AssertionError(f'case {i} {case} {key}: {diffs[:6]}; x86trace={expected["trace"]}; native trace={actual["trace"]}')
        summaries.append({'index':i,'function_va':f'{FUNCTIONS[case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        pos=s['raw_offset']+rva-s['rva'];return image[pos:pos+size]
    assert raw(0x4C315A,3)==b'\xc2\x04\x00'
    base='iterations/v2/001-original-recovery/'
    compiled=[base+'source/recovered/network_cleanup_probe.cpp',base+'source/recovered/Porsche.exe/network_cleanup.cpp',base+'source/recovered/Porsche.exe/network_services.cpp']
    paths=compiled+[base+'runs/151-network-cleanup/'+p for p in ('README.md','CMakeLists.txt')]+[
        'scripts/research/verify-v2-network-cleanup.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    refs=[json.loads(line) for line in (ROOT/paths[-2]).read_text().splitlines()]
    storage_refs=[r for r in refs if r.get('to_va') in ('00628c60','00628c64')]
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,
        'function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],
        'full_function_vas':[f'{va:08x}' for va,_,_ in FUNCTIONS.values()],'partial_function_vas':[],
        'cases':len(all_cases),'native_cpp_equal_original_x86':True,
        'comparison_boundary':'Full 48c430/4904d0/4c3150/48c580/48aed0 bodies. Destroy calls real recovered 48b660. Exact lock/free/worker order and arguments, complete object/list/payload/manager/lock fixture backing, intermediate boundary state, output aliases and return pointer; original ESP/nonvolatile registers and RET4. Effects can replace global list/lock, manager, captured pool heads/handles and destructor fields.',
        'index_query':'Run148 unresolved 48c430/4904d0/4c3150 and Run145 48c580/48aed0: functions, all callers/callees and full ASM. Trace every 628c60/64 reference and 48c4d0 initialization stores before establishing storage owners.',
        'unresolved_effects':['0055d9b0 cdecl()','0055d1b0 cdecl(worker)','00531f90','005322b0','005322c0','005322d0','0059f050'],
        'new_storage':[{'va':'00628c60','bytes':4,'initial':0,'meaning':'allocated list wrapper pointer','writer':'0048c4d0','clearer':'0048c580'},
            {'va':'00628c64','bytes':4,'initial':0,'meaning':'allocated lock cell pointer','writer':'0048c4d0','clearer':'0048c580'}],
        'storage_references':storage_refs,
        'deferred':['00492260/00491fc0 session lifecycle','0048dcb0 poll/0048e1a0 wait','005e8bfc table extent/owner and005e8e50 alias backlog unchanged'],
        'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size,_ in FUNCTIONS.values()],
        'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))


if __name__=='__main__':main()

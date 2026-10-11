"""Original x86 oracle for network reset, member destruction and callback removal."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
BASE, STACK, EXIT = 0x400000, 0x2201000, 0x222F000
NET, OTHER, MEMBER, LOCK, LISTS, MANAGER_A, MANAGER_B = (
    0x23000000, 0x23001000, 0x23002000, 0x23004000, 0x23005000, 0x23007000, 0x23008000)
FUNCTIONS = {0:(0x48E9C0,0x15B),1:(0x4935C0,0x152),2:(0x560180,0x27)}
# Stack arguments, callee-pop bytes, record ECX.
BOUNDARIES = {
    0x5322B0:(1,0,False),0x5322C0:(1,0,False),0x5322D0:(1,0,False),
    0x561110:(1,0,False),0x561B50:(0,0,False),0x531F90:(1,0,False),
    0x561730:(1,0,False),0x5617D0:(1,0,False),0x48C580:(0,0,False),
    0x48C870:(5,20,True),0x53C380:(1,0,False),0x492260:(0,0,False),
    0x59F050:(1,0,False),0x48AED0:(0,0,True),0x491FC0:(0,0,True),
    0x48E790:(0,0,True),0x48A9A0:(0,0,False),
}


def cases():
    result=[]
    def add(op,*args):result.append([op,*args,*([0]*(12-len(args)))])
    # flags, mode, global-network variant, signed timer bits, tick,
    # callback mutation mask, list1/list0 node counts, cancel byte, buffer flag,
    # manager index, unused.
    for flags in (0,1,4,8,16,32,64,2|8|16,127):
        for mode in (0,2):add(0,flags,mode,0,1001,0x12345678,0,0,0,0,0)
    for global_variant in (0,1,2,3):
        for timer in (0,1,3,0x7FFFFFFF,0x80000000,0xFFFFFFFF,0xFFFFFFFD):
            add(0,2|8|16|64,1,global_variant,timer,0xFFFFFFFF)
    for tick in (0,1,0x07FFFFFF,0x08000000,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        add(0,0,0,0,1,tick)
    for first,second in ((0,0),(1,0),(0,1),(1,1),(3,2)):
        for active,buffer in ((0,0),(1,0),(0,1),(0xFF,1)):
            add(1,0,0,0,0,0,0,first,second,active,buffer)
    for mutation in (1,2,4,8,16,32,64,128,512,1024,1536,2047):
        add(0,127,1,1,0xFFFFFFFD,0xF1234567,mutation,3,2,1,1)
        add(1,0,0,0,0,0,mutation,3,2,1,1,1)
    for target in (0,0x48EE90,0x11111111,0x55555555,0xDEADBEEF):add(2,target)
    for flags in (0,32,127):add(3,flags,2,1,1000,0xFFFFFFFF,0,1,1,1,1)
    return result


def original(module,image,case):
    sys.path.insert(0,str(ROOT / "local/tools/python-unicorn"))
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,
        UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(BASE,0x300000)
    for s in module['sections']:
        if s['raw_size']:uc.mem_write(BASE+s['rva'],image[s['raw_offset']:s['raw_offset']+s['raw_size']])
    uc.mem_map(0x2200000,0x30000);uc.mem_map(NET,0x10000)
    def put(va,v):uc.mem_write(va,struct.pack('<I',v&0xFFFFFFFF))
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    def byte(va):return uc.mem_read(va,1)[0]
    def putbyte(va,v):uc.mem_write(va,bytes([v&0xFF]))
    def words(va,size):return list(struct.unpack(f'<{size//4}I',uc.mem_read(va,size)))
    def fill(va,size,value):uc.mem_write(va,struct.pack(f'<{size//4}I',*([value]*(size//4))))
    op,*a=case;flags=a[0];manager_index=a[10]&1;pool_enters=0
    for va,size,value in ((NET,0x268,0xABABABAB),(OTHER,0x268,0xCDCDCDCD),
        (MEMBER,0x40,0xD0D0D0D0),(LISTS,0x200,0xE0E0E0E0),
        (MANAGER_A,0x100,0xF0F0F0F0),(MANAGER_B,0x100,0xF1F1F1F1)):fill(va,size,value)
    put(LOCK,0x44440000)
    put(NET+8,0x26000000 if flags&8 else 0);put(NET+0xC,0x26001000 if flags&16 else 0)
    put(NET+0x10,LOCK);put(NET+0x14,MEMBER if flags&4 else 0);put(NET+0x28,a[1])
    putbyte(NET+0xC7,flags&1);putbyte(NET+0xC2,1 if flags&2 else 0);putbyte(NET+0xBF,0)
    putbyte(NET+0x106,1 if flags&32 else 0);put(NET+0xDC,0x12345678)
    put(OTHER+8,0 if a[2]==2 else 0x26002000);put(OTHER+0xC,0x26004000)
    putbyte(OTHER+0xBF,1 if a[2]==3 else 0);put(OTHER+0xDC,0x87654321)
    put(0x628C70,OTHER if a[2] else NET);put(0x628C74,0x26003000 if flags&64 else 0)
    put(0x628C7C,MEMBER);put(0x5DEB48,a[3]);put(0x5E4FE8,MANAGER_B if manager_index else MANAGER_A)
    def init_list(offset,count,stride):
        head=LISTS+offset
        put(head,head+0x20 if count else head);put(head+4,head+0x20+(count-1)*stride if count else head)
        for i in range(count):
            node=head+0x20+i*stride;put(node,node+stride if i+1<count else head);put(node+4,node-stride if i else head)
    init_list(0,a[6],0x10);init_list(0x100,a[7],0x18)
    for off,v in ((0,LISTS+0x100),(4,LISTS),(8,0x11112222),(0x14,0x33334444),
                  (0x1C,0x25002000 if a[9] else 0),(0x20,0x25003000)):put(MEMBER+off,v)
    putbyte(MEMBER+0x10,a[8])
    for i,m in enumerate((MANAGER_A,MANAGER_B)):
        put(m+0x28,0x27000000+i);put(m+0x38,0x25001000+i);put(m+0x3C,0x25001100+i)
    callbacks=[0x48EE90,0x11111111,0x48EE90,0x22222222,0,0x33333333,0x44444444,0x55555555]
    uc.mem_write(0x6B7C20,struct.pack('<8I',*callbacks))
    put(STACK,EXIT);put(STACK+4,a[0]);uc.reg_write(UC_X86_REG_ESP,STACK)
    uc.reg_write(UC_X86_REG_ECX,MEMBER if op==1 else NET)
    saved={UC_X86_REG_EBX:0x11223344,UC_X86_REG_ESI:0x55667788,
           UC_X86_REG_EDI:0x99AABBCC,UC_X86_REG_EBP:0xDDEEFF00}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def hook(machine,address,_size,_user):
        nonlocal manager_index,pool_enters
        if address==EXIT:machine.emu_stop();return
        if address not in BOUNDARIES:return
        argc,pop,member_call=BOUNDARIES[address];sp=machine.reg_read(UC_X86_REG_ESP)
        values=[get(sp+4+i*4) for i in range(argc)]
        row=[address,*([machine.reg_read(UC_X86_REG_ECX)] if member_call else []),*values]
        row += [get(NET+off) for off in (8,0xC,0x14)]
        row += [byte(NET+off) for off in (0xC2,0xC3,0xC7)]
        row += [byte(MEMBER+0x10),get(0x628C7C),get(0x628C74),manager_index]
        trace.append(row);result=0
        if address==0x5322B0:
            handle=values[0]
            if handle==get(LOCK) and a[5]&8:put(LOCK,0x44441111)
            if 0x27000000 <= handle <= 0x2700FFFF:
                pool_enters+=1;captured=MANAGER_A if get(MANAGER_A+0x28)==handle else MANAGER_B
                if a[5]&512:
                    manager_index^=1;put(0x5E4FE8,MANAGER_B if manager_index else MANAGER_A)
                if a[5]&1024:
                    put(captured+0x38,0x25100000+pool_enters);put(captured+0x3C,0x25200000+pool_enters);put(captured+0x28,0x27001000+pool_enters)
        if address==0x561B50 and a[5]&64:put(MEMBER+0x1C,0x25002100)
        if address==0x561730 and a[5]&128:put(MEMBER+8,0x11113333)
        if address==0x48C580 and a[5]&1:putbyte(NET+0xC2,0)
        if address==0x53C380 and a[5]&2:putbyte(NET+0xC2,0)
        if address==0x59F050:
            result=1
            if a[5]&4:put(NET+8,0x26006000)
        if address==0x531F90:result=1
        if address==0x491FC0 and a[5]&32:put(0x628C74,0x26007000)
        if address==0x48E790 and a[5]&16:
            putbyte(NET+0xC2,1);putbyte(NET+0xC0,0x77);put(NET+0xE0,0x98765432)
        if address==0x48A9A0:result=a[4]
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ESP,sp+4+pop)
        machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start=FUNCTIONS[0 if op==3 else op][0]
    try:uc.emu_start(start,EXIT+1,count=100000)
    except Exception as error:raise RuntimeError(f'x86 fault case={case}, EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace}') from error
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    state=[]
    for va,size in ((NET,0x268),(OTHER,0x268),(MEMBER,0x40),(LISTS,0x200),(MANAGER_A,0x100),(MANAGER_B,0x100),(0x6B7C20,0x20)):state+=words(va,size)
    state += [get(0x628C70),get(0x628C74),get(0x628C7C),get(LOCK),manager_index]
    return {'result':uc.reg_read(UC_X86_REG_EAX) if op==0 else 0,'trace':trace,'state':state}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/network-lifecycle-145/bin/Release/network_lifecycle_probe.exe')
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
                raise AssertionError(f'case{i} {case} {key}: {diffs[:6]}; x86trace={expected["trace"]}; nativetrace={actual["trace"]}')
        summaries.append({'index':i,'function_va':f'{FUNCTIONS[0 if case[0]==3 else case[0]][0]:08x}','input':case,'boundary_calls':len(expected['trace'])})
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        pos=s['raw_offset']+rva-s['rva'];return image[pos:pos+size]
    assert raw(0x48A9A0,6)==b'\xff\x25\x80\x20\x5b\x00', 'GetTickCount exact source IAT thunk'
    for va,size in ((0x628C74,4),(0x628C7C,4),(0x6B7C20,0x20)):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['vsize'])
        assert rva>=s['rva']+s['raw_size'],'new state must be original zero-fill'
    # Preserve every count/table/shared-empty index hit with nearby ASM rather
    # than turning the neighboring symbols into an invented extent.
    refs=list(map(json.loads,(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl').read_text().splitlines()))
    asm=(ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm').read_text(encoding='utf-8').splitlines()
    line_numbers={line[:8]:i for i,line in enumerate(asm) if len(line)>10 and line[8:10]=='  '}
    trace={}
    for target in ('005e8bfc','005e8c00','005e8e50'):
        hits=[]
        for ref in refs:
            if ref.get('to_va')!=target:continue
            number=line_numbers.get(ref['from_va']);entry=dict(ref)
            entry['asm_context']=asm[max(0,number-3):number+5] if number is not None else []
            hits.append(entry)
        trace[target]=hits
    storage_trace={'module_sha256':SHA,'all_index_hits':trace,
        'confirmed':'411165 zeros count;40f24d/258 read count;40f25d stores object pointer to table[count];40f265 increments count. No capacity check in writer40f160. 5e8c24 is a separate table, not proof of5e8c00 capacity.',
        'open':'Production table extent/valid index domain;5e8e50 canonical alias and original initial/runtime bytes. Existing one-byte null,32-byte heap label and renderer constant remain distinct current implementations; this packet changes none of them.'}
    (args.report_dir/'storage-trace.json').write_text(json.dumps(storage_trace,indent=2)+'\n',encoding='utf-8',newline='\n')
    base='iterations/v2/001-original-recovery/'
    compiled=[base+'source/recovered/network_lifecycle_probe.cpp',base+'source/recovered/Porsche.exe/network_lifecycle.cpp']
    paths=compiled+[base+'runs/145-network-lifecycle/'+p for p in ('README.md','CMakeLists.txt','storage-trace.json')]+[
        'scripts/research/verify-v2-network-lifecycle.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/static/imports.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'module_sha256':SHA,
        'function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],
        'full_function_vas':[f'{va:08x}' for va,_ in FUNCTIONS.values()],'partial_function_vas':[],
        'cases':len(all_cases),'native_cpp_equal_original_x86':True,
        'comparison_boundary':'Complete48e9c0/4935c0/560180 bodies, including connected reset-to-member destructor and real callback removal. Full two network objects/member/list backing/two canonical-manager views/callback table/pointer/lock snapshots, ordered boundary arguments and state observations; original nonvolatile registers/ESP, reset final EAX tick<<5.',
        'index_query':'All005e8bfc/005e8c00/005e8e50 refs and40f160/411130 writers;48e9c0/4935c0/560180 callers/callees→full ASM. GetTickCount thunk48a9a0→IAT5b2080.',
        'storage_trace':'storage-trace.json','unresolved_storage':['005e8bfc/count005e8c00 table extent and owner','005e8e50 alias backlog'],
        'new_storage':[{'va':'00628c74','bytes':4,'initial':'PE zero-fill'},{'va':'00628c7c','bytes':4,'initial':'PE zero-fill'},{'va':'006b7c20','bytes':32,'initial':'PE zero-fill; eight slots proven by00560180 scan endpoint006b7c40'}],
        'unresolved_effects':[f'{va:08x}' for va in BOUNDARIES],
        'original_functions':[{'va':f'{va:08x}','body_bytes':size,'body_sha256':hashlib.sha256(raw(va,size)).hexdigest()} for va,size in FUNCTIONS.values()],
        'cases_summary':summaries,'source_sha256':source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('function_vas','cases','native_cpp_equal_original_x86')}))


if __name__=='__main__':main()

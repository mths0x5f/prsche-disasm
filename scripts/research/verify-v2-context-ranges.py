import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/149-context-ranges'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
B,M,ALT,S=0x25000000,0x25000400,0x25000700,0x25000200
OBJ,BLOCK,ARR,P,Q,Z=B+0x1000,B+0x1500,B+0x1800,B+0x2000,B+0x4000,B+0x6000
STACK,EXIT=0x02200000,0x02210000
FULL=['00529c20','00529c50','004e4560','004d7da0','0059eeb0']
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,
    UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,
    UC_X86_REG_ESI,UC_X86_REG_EDI)
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def h(x):return f'{x & 0xffffffff:08x}'
def mode(case):return 1 if case==22 else 2 if case==35 else 0
def kind(case):return 0 if case in (22,32) else 31 if case==33 else 1 if case==35 else 3
def state(case):return M-mode(case)*140+0x28

def oracle(case,binary,module):
    machine=Uc(UC_ARCH_X86,UC_MODE_32)
    machine.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:
            machine.mem_write(0x400000+sec['rva'],binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    machine.mem_map(B,0x7000)
    machine.mem_map(STACK-0x10000,0x20000)
    machine.mem_map(EXIT,0x1000)
    machine.mem_write(B,bytes((i*13+0x35)&255 for i in range(0x7000)))
    def get(a):return struct.unpack('<I',machine.mem_read(a & 0xffffffff,4))[0]
    def put(a,x):machine.mem_write(a & 0xffffffff,struct.pack('<I',x & 0xffffffff))
    put(0x5e4fe8,M);put(0x5e4fec,S)
    put(0x6af3f8,24 if case==22 else 8 if case in (23,24,36) else 40 if case==35 else 4096)
    for m in range(3):
        s=M-m*140+0x28;put(s,0x11110000+m);put(s+4,P);put(s+8,Z)
        for k in range(32):put(s+0xc+k*4,BLOCK)
    put(ALT+0x28,0x22220000);put(ALT+0x2c,Q);put(S,7)
    put(M+4,0x6f0000);put(ALT+4,0x6f0000)
    put(OBJ,BLOCK);put(OBJ+8,BLOCK+32);put(P+4,Q);put(Q+4,0)
    put(ARR+4,Q);put(ARR+8,Z)
    if case==8:put(OBJ,0)
    if case==9:put(OBJ+8,BLOCK)
    if case==11:put(OBJ+8,BLOCK+257)
    if case==12:put(OBJ+8,BLOCK-4)
    if case in (21,23,27,28,29,32,34):put(state(case)+4,0)
    if case==36:put(state(case)+4,state(case)-4)
    if case==37:put(OBJ,OBJ);put(OBJ+8,OBJ+32)
    events=[];enters=leaves=copies=0;reads=[]
    def event(name,a,b=0,c=0):events.append(f'{name}:{h(a)}:{h(b)}:{h(c)};')
    def memory_read(uc,access,address,size,value,data):
        if case in (4,5,6,7) and ARR<=address<ARR+16:reads.append({'va':h(address),'bytes':size})
    machine.hook_add(UC_HOOK_MEM_READ,memory_read)
    def hook(uc,address,size,data):
        nonlocal enters,leaves,copies
        if address==EXIT:uc.emu_stop();return
        if address not in (0x5322b0,0x5322c0,0x59ecd0,0x59f050,0x6f0000,0x5299d0,0x529c50):return
        if address==0x529c50 and case>=4:return
        esp=uc.reg_read(UC_X86_REG_ESP);a=get(esp+4);result=0xcafe0071;pop=0
        if address==0x5322b0:
            event('enter',a);enters+=1
            if case==14:put(OBJ,0);put(OBJ+8,0xffffffff);put(M+0x28,0x88880000)
            if case==25:put(state(case)+4,Q)
            if case==26:put(0x5e4fe8,ALT)
            if case==27 and enters==2:put(0x5e4fe8,ALT)
            if case==30:put(state(case),0x99990000)
            if case==34 and enters==2:put(S,99)
        elif address==0x5322c0:
            event('leave',a);leaves+=1
            if case==29 and leaves==1:put(state(case)+4,Q)
        elif address==0x59ecd0:event('table_release',a)
        elif address==0x59f050:event('heap_release',a)
        elif address==0x6f0000:
            event('alloc',a,get(esp+8),get(esp+12));result=P
            if case==27:put(M+0x2c,Q)
            if case==28:put(0x6af3f8,64)
        elif address==0x5299d0:
            source=a;dest=uc.reg_read(UC_X86_REG_ECX);pop=4
            event('copy01',get(source),get(source+4),get(source+8));event('copy3',get(source+12))
            copies+=1
            if case==1 and copies==1:put(source,0xabcdef12)
            if case==2 and copies==2:put(source+8,0x31415926)
            for off in range(0,16,4):put(dest+off,get(source+off))
            result=dest
        else:
            words=[get(esp+4+i*4) for i in range(9)]
            event('walk01',*words[:3]);event('walk3',words[3])
            event('walk45',*words[4:7]);event('walk7',words[7],words[8])
        uc.reg_write(UC_X86_REG_EAX,result)
        uc.reg_write(UC_X86_REG_ECX,0xcccccccc);uc.reg_write(UC_X86_REG_EDX,0xdddddddd)
        uc.reg_write(UC_X86_REG_EIP,get(esp));uc.reg_write(UC_X86_REG_ESP,esp+4+pop)
    machine.hook_add(UC_HOOK_CODE,hook)
    if case<4:
        a=[P+0x1fc,0x11223344,P+0x200,ARR];b=[Z+4,0x55667788,0x99aabbcc,0xdeadbeef]
        if case==3:a=b=[0,0,0,0]
        va,args=0x529c20,a+b+[0x98765432]
    elif case<8:
        a=[P,0,P+0x200,ARR];b=[P,0,0,0]
        if case==5:b[0]=P+16
        if case==6:a[0]=P+0x1fc;b[0]=Q+8
        if case==7:a[0]=P+0x1fc;b[0]=Z+4
        va,args=0x529c50,a+b+[0x98765432]
    elif case<15 or case==37:
        flags=1 if case==9 else 3 if case==11 else 0x100 if case==13 else 1 if case==37 else 0
        va,args=0x4e4560,[flags]
    elif case<20:va,args=0x4d7da0,[BLOCK,[0,1,8,9,0x08000001][case-15]]
    else:va,args=0x59eeb0,[kind(case),mode(case)]
    machine.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
    machine.reg_write(UC_X86_REG_ESP,STACK);machine.reg_write(UC_X86_REG_ECX,OBJ)
    machine.reg_write(UC_X86_REG_EDX,0x12345678);machine.reg_write(UC_X86_REG_EAX,0x13579bdf)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():machine.reg_write(reg,value)
    machine.emu_start(va,EXIT+1,count=100000)
    assert machine.reg_read(UC_X86_REG_EIP)==EXIT
    pop=4 if va==0x4e4560 else 0
    assert machine.reg_read(UC_X86_REG_ESP)==STACK+4+pop
    assert all(machine.reg_read(reg)==value for reg,value in saved.items())
    result=machine.reg_read(UC_X86_REG_EAX) if va==0x4e4560 else 0
    return {'case':case,'result':h(result),'manager':h(get(0x5e4fe8)),
        'page_size':h(get(0x6af3f8)),'trace':''.join(events),
        'memory':bytes(machine.mem_read(B,0x7000)).hex(),'range_node_reads':reads}, {
        'va':h(va),'stack_pop':pop,'callee_saved_preserved':True,
        'eax_compared':va==0x4e4560,'original_range_node_reads':reads}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/context-ranges-149/bin/Release/context_ranges_probe.exe')
    parser.add_argument('--wrapper-probe',type=Path)
    parser.add_argument('--report-dir',type=Path,default=RUN)
    args=parser.parse_args()
    wrapper=args.wrapper_probe or args.probe.with_name('context_range_wrapper_probe.exe')
    modules=[json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text(encoding='utf-8').splitlines()]
    module=next(x for x in modules if x['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(binary).hexdigest()==SHA
    def original_bytes(start,count):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=start<0x400000+s['rva']+max(s['raw_size'],s['vsize']))
        delta=start-0x400000-sec['rva']
        assert delta+count<=max(sec['raw_size'],sec['vsize'])
        initialized=max(0,min(count,sec['raw_size']-delta))
        pos=sec['raw_offset']+delta
        return binary[pos:pos+initialized]+bytes(count-initialized)
    hashes=[]
    for probe in (args.probe,wrapper):
        exe=probe.read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
        assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c
        assert struct.unpack_from('<H',exe,pe+24)[0]==0x10b
        hashes.append({'probe':probe.name,'sha256':hashlib.sha256(exe).hexdigest()})
    build=args.probe.resolve().parents[2]
    cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def compiler_value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert compiler_value('CMAKE_CXX_COMPILER_ID')=='MSVC' and compiler_value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    fixtures=[];abi=[]
    for case in range(38):
        probe=wrapper if case<4 else args.probe
        actual=json.loads(subprocess.check_output([str(probe),str(case)],text=True,timeout=15))
        expected,checks=oracle(case,binary,module)
        for key in expected:
            if actual[key]!=expected[key]:
                if key=='memory':
                    aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key])
                    at=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                    raise AssertionError(f'case{case} memory +{at:#x}: {aa[at]:02x}!={bb[at]:02x}')
                raise AssertionError(f'case{case} {key}: {actual[key]} != {expected[key]}')
        fixtures.append({'case':case,'probe':probe.name,'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()})
        abi.append({'case':case,**checks})
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf-8').splitlines()]
    pins=[]
    for va in FULL+['005299d0','0059ecb0','0059ecd0','0059f050']:
        f=next(x for x in functions if x['entry_va']==va);spans=[]
        for first,last in f['ranges']:
            raw=original_bytes(int(first,16),int(last,16)+1-int(first,16))
            spans.append({'start_va':first,'end_va_inclusive':last,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        pins.append({'entry_va':va,'ranges':spans})
    compiled=['iterations/v2/001-original-recovery/source/recovered/context_ranges_probe.cpp',
              'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/context_ranges.cpp']
    paths=compiled+['iterations/v2/001-original-recovery/runs/149-context-ranges/CMakeLists.txt',
        'iterations/v2/001-original-recovery/runs/149-context-ranges/README.md',
        'scripts/research/verify-v2-context-ranges.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':FULL,
        'full_function_vas':FULL,'partial_function_vas':[],'cases':len(fixtures),
        'native_cpp_equal_original_x86':True,'original_body_pins':pins,
        'native_toolchain':{'compiler_id':'MSVC','compiler_version':compiler_value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':compiler_value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32',
            'native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Full 28672-byte poisoned arena, manager/page-size globals, destructor pointer return, ordered callbacks, aggregate-copy and nine-DWORD walk forwarding, original ABI. Actual native walker node-read addresses are observed using a private PAGE_GUARD/VEH fixture and match the original read trace.',
        'wrapper_seam':'CONTEXT_RANGES_EXTERNAL_WALK replaces only00529c50 by an explicit recording boundary in private secondtarget; the normaltarget compiles the complete00529c50 body.',
        'unknown_boundaries':['005322b0/005322c0 canonical locks','0059f050 canonical heap release','0059ecd0/0059ecb0 canonical manager wrappers','005299d0 canonical range copy','manager/selector storage accessors'],
        'original_global_pins':[{'va':h(a),'bytes_hex':original_bytes(a,4).hex(),'sha256':hashlib.sha256(original_bytes(a,4)).hexdigest()} for a in (0x5e4fe8,0x5e4fec,0x6af3f8)],
        'original_abi_checks':abi,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashes[0]['sha256'],'wrapper_probe_sha256':hashes[1]['sha256'],
        'native_probe_hashes':hashes}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':len(FULL),'cases':len(fixtures),'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

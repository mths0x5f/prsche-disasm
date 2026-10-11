import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/139-context-effects'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
B, M, ALT, S = 0x24000000, 0x24000400, 0x24000700, 0x24000200
N, C, T, R = B+0x1000, B+0x1100, B+0x1200, B+0x1500
STACK, EXIT = 0x02200000, 0x02210000
FULL = ['004211d0', '004237d0', '00441200', '00424000',
        '005262e0', '0059ecb0', '0059ecd0']
sys.path.insert(0, str(ROOT / 'local/tools/python-unicorn'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EDX,
    UC_X86_REG_ESP, UC_X86_REG_EIP, UC_X86_REG_EBX, UC_X86_REG_EBP,
    UC_X86_REG_ESI, UC_X86_REG_EDI)
sys.path.insert(0, str(ROOT / 'scripts/research'))
from v2_source_dependencies import source_hashes

def h(value): return f'{value & 0xffffffff:08x}'

def oracle(case, binary, module):
    machine = Uc(UC_ARCH_X86, UC_MODE_32)
    machine.mem_map(0x400000, 0x300000)
    for sec in module['sections']:
        if sec['raw_size']:
            machine.mem_write(0x400000+sec['rva'], binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    machine.mem_map(B, 0x2000)
    machine.mem_map(STACK-0x10000, 0x20000)
    machine.mem_map(EXIT, 0x1000)
    machine.mem_write(B, bytes((i*19+0x17)&255 for i in range(0x2000)))
    def get(a): return struct.unpack('<I', machine.mem_read(a & 0xffffffff, 4))[0]
    def put(a, x): machine.mem_write(a & 0xffffffff, struct.pack('<I', x & 0xffffffff))
    put(0x5e4fe8, M); put(0x5e4fec, S)
    for mode in range(3):
        p=M-mode*140+0x28
        put(p, 0x11110000+mode)
        for k in range(32): put(p+0xc+k*4, N)
        put(S-mode*4, 7+mode)
    put(ALT+0x28, 0x22220000)
    for k in range(32): put(ALT+0x34+k*4, T)
    for a in (M, ALT): put(a+4, 0x6f0000); put(a+8, 0x6f0010)
    put(N+4,C); put(C+4,T); put(T+4,0)
    if case==6: put(M+0x28+0xc+3*4,0)
    if case>=19:
        for n in (N,C,T):
            for off in (8,0xc,0x10,0x18): put(n+off,0)
        put(N+0xc,C);put(N+8,T)
        put(C+0x10,R);put(C+0x18,R+16)
        put(N+0x10,R+0x100);put(N+0x18,R+0x100+257)
        if case==22: put(C+0x10,R);put(C+0x18,R)
    events=[]
    def event(name,a,b=0,c=0): events.append(f'{name}:{h(a)}:{h(b)}:{h(c)};')
    def hook(uc, address, size, _):
        if address==EXIT: uc.emu_stop();return
        if address not in (0x6f0000,0x6f0010,0x5322b0,0x5322c0,0x59eeb0): return
        esp=uc.reg_read(UC_X86_REG_ESP)
        a=get(esp+4); result=0xcafe0071
        if address==0x6f0000:
            event('alloc',a,get(esp+8),get(esp+12))
            if case==1:put(0x5e4fe8,ALT)
            result=0 if case==0 else R
        elif address==0x6f0010:
            event('release',a)
            if case==21:put(0x5e4fe8,ALT)
        elif address==0x5322b0:
            event('enter',a)
            if case==7:put(M+0x28,0x55550000);put(M+0x28+0xc+3*4,C)
            if case==8:put(0x5e4fe8,ALT)
            if case==23:put(C+8,T);put(N+8,0)
        elif address==0x5322c0: event('leave',a)
        else:
            mode=get(esp+8);event('refill',a,mode)
            put(M-mode*140+0x28+0xc+a*4,C)
            put(M-mode*140+0x28,0x77770000);result=R
        uc.reg_write(UC_X86_REG_EAX,result)
        uc.reg_write(UC_X86_REG_ECX,0xcccccccc)
        uc.reg_write(UC_X86_REG_EDX,0xdddddddd)
        uc.reg_write(UC_X86_REG_EIP,get(esp))
        uc.reg_write(UC_X86_REG_ESP,esp+4)
    machine.hook_add(UC_HOOK_CODE,hook)
    if case in (0,1): va,args=0x59ecb0,[123 if case else 0,0x89abcdef,0x5cbdb4]
    elif case==2:va,args=0x59ecd0,[0]
    elif case==3:va,args=0x4237d0,[R,257,1]
    elif case==4:va,args=0x4211d0,[1,0]
    elif case==5:va,args=0x4211d0,[256,1]
    elif case in (6,7,8):va,args=0x4211d0,[32,0]
    elif case==9:va,args=0x4211d0,[257,0]
    elif case==10:va,args=0x4211d0,[0xffffffff,2]
    elif case==11:va,args=0x4237d0,[R,1,0]
    elif case==12:va,args=0x4237d0,[R,256,1]
    elif case==13:va,args=0x4237d0,[R,257,2]
    elif case in (14,15):va,args=0x441200,[R,256 if case==14 else 257]
    elif case in (16,17,18):va,args=0x424000,[R,{16:0,17:8,18:257}[case]]
    else:va,args=0x5262e0,[0 if case==19 else N]
    machine.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
    machine.reg_write(UC_X86_REG_ESP,STACK)
    machine.reg_write(UC_X86_REG_ECX,B+0x1800)
    machine.reg_write(UC_X86_REG_EDX,0x12345678)
    machine.reg_write(UC_X86_REG_EAX,0x13579bdf)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,
           UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():machine.reg_write(reg,value)
    machine.emu_start(va,EXIT+1,count=100000)
    assert machine.reg_read(UC_X86_REG_EIP)==EXIT
    assert machine.reg_read(UC_X86_REG_ESP)==STACK+4+(4 if va==0x5262e0 else 0)
    assert all(machine.reg_read(reg)==value for reg,value in saved.items())
    result=machine.reg_read(UC_X86_REG_EAX) if va in (0x59ecb0,0x4211d0) else 0
    return {'case':case,'result':h(result),'manager':h(get(0x5e4fe8)),
            'trace':''.join(events),'memory':bytes(machine.mem_read(B,0x2000)).hex()}, {
            'va':h(va),'stack_pop':4 if va==0x5262e0 else 0,
            'callee_saved_preserved':True,'eax_compared':va in (0x59ecb0,0x4211d0)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/context-effects-139/bin/Release/context_effects_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN)
    args=parser.parse_args()
    modules=[json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text(encoding='utf-8').splitlines()]
    module=next(x for x in modules if x['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes()
    assert hashlib.sha256(binary).hexdigest()==SHA
    def original_bytes(start,count):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=start<0x400000+s['rva']+s['raw_size'])
        pos=sec['raw_offset']+start-0x400000-sec['rva'];return binary[pos:pos+count]
    exe=args.probe.read_bytes(); pe=struct.unpack_from('<I',exe,0x3c)[0]
    assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c
    assert struct.unpack_from('<H',exe,pe+24)[0]==0x10b
    build=args.probe.resolve().parents[2]
    cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def compiler_value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert compiler_value('CMAKE_CXX_COMPILER_ID')=='MSVC'
    assert compiler_value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    fixtures=[];abi=[]
    for case in range(24):
        actual=json.loads(subprocess.check_output([str(args.probe),str(case)],text=True))
        expected,checks=oracle(case,binary,module)
        for key in expected:
            if actual[key]!=expected[key]:
                if key=='memory':
                    aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key])
                    at=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                    raise AssertionError(f'case{case} memory +{at:#x}: {aa[at]:02x}!={bb[at]:02x}')
                raise AssertionError(f'case{case} {key}: {actual[key]} != {expected[key]}')
        fixtures.append({'case':case,'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()})
        abi.append({'case':case,**checks})
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf-8').splitlines()]
    pins=[]
    for va in FULL+['0059eeb0','00529c20','00529c50']:
        f=next(x for x in functions if x['entry_va']==va);spans=[]
        for first,last in f['ranges']:
            raw=original_bytes(int(first,16),int(last,16)+1-int(first,16))
            spans.append({'start_va':first,'end_va_inclusive':last,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        pins.append({'entry_va':va,'ranges':spans})
    compiled=['iterations/v2/001-original-recovery/source/recovered/context_effects_probe.cpp',
              'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/context_effects.cpp']
    paths=compiled+['iterations/v2/001-original-recovery/runs/139-context-effects/CMakeLists.txt',
        'iterations/v2/001-original-recovery/runs/139-context-effects/README.md',
        'scripts/research/verify-v2-context-effects.py',
        'research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':FULL,
        'full_function_vas':FULL,'partial_function_vas':[], 'cases':len(fixtures),
        'native_cpp_equal_original_x86':True,'original_body_pins':pins,
        'native_toolchain':{'compiler_id':'MSVC','compiler_version':compiler_value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':compiler_value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32',
            'native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Full 8192-byte poisoned mapped arena, manager pointer, allocation pointer returns, ordered callbacks; original stack cleanup/nonvolatile registers. Void functions have no EAX contract.',
        'unknown_boundaries':['0059eeb0 pool refill','005322b0/005322c0 canonical locks','manager indirect allocation/release callbacks','00529c20/00529c50 remain unrecovered range services'],
        'original_global_pins':[{'va':h(a),'bytes_hex':original_bytes(a,4).hex(),'sha256':hashlib.sha256(original_bytes(a,4)).hexdigest()} for a in (0x5e4fe8,0x5e4fec)],
        'original_abi_checks':abi,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':len(FULL),'cases':len(fixtures),'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

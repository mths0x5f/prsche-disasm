import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/150-context-services'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
B,OBJ,SRC,STR,BLOCK,ALT,M=0x26000000,0x26001000,0x26001100,0x26001400,0x26002000,0x26002800,0x26000400
STACK,EXIT=0x02200000,0x02210000
FULL=['00423610','00505810','004d55c0','004d64a0','004298a0','00429bf0',
      '00429840','004d6510','004d6520','004d6530','004d67b0']
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,
    UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,
    UC_X86_REG_ESI,UC_X86_REG_EDI)
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def h(x):return f'{x & 0xffffffff:08x}'
def text_size(case):return 0 if case in (4,9) else 1 if case==5 else 255 if case in (6,10,18) else 511 if case==61 else 7

def oracle(case,binary,module):
    machine=Uc(UC_ARCH_X86,UC_MODE_32)
    machine.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:
            machine.mem_write(0x400000+sec['rva'],binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    machine.mem_map(B,0x5000);machine.mem_map(STACK-0x10000,0x20000);machine.mem_map(EXIT,0x1000)
    machine.mem_write(B,bytes((i*17+0x29)&255 for i in range(0x5000)))
    def get(a):return struct.unpack('<I',machine.mem_read(a & 0xffffffff,4))[0]
    def put(a,x):machine.mem_write(a & 0xffffffff,struct.pack('<I',x & 0xffffffff))
    put(0x5e4fe8,M)
    put(OBJ,BLOCK);put(OBJ+4,BLOCK+7);put(OBJ+8,BLOCK+8)
    put(SRC,STR);put(SRC+4,STR+7);put(SRC+8,STR+20)
    machine.mem_write(STR,bytes(65+i%26 for i in range(text_size(case)))+b'\0')
    put(M+0x28,0x11110000)
    for k in range(32):put(M+0x34+k*4,ALT)
    if case==25:put(SRC+4,STR)
    if case==27:put(OBJ-4,0)
    if case==30:put(OBJ,0)
    if case==31:put(OBJ+8,BLOCK)
    if case==33:put(OBJ+8,BLOCK+256)
    if case==34:put(OBJ+8,BLOCK+257)
    if case==35:put(OBJ+8,BLOCK-1)
    if case==37:put(OBJ,OBJ);put(OBJ+8,OBJ+32)
    if 38<=case<=44:put(OBJ+4,BLOCK+[0,4,7,0xffffffff,0xfffffffc,0x80000000,0x7fffffff][case-38])
    if 50<=case<=52:put(OBJ+4,[0,7,0xffffffff][case-50])
    if 53<=case<=57:
        put(SRC,[0,0xffffffff,0,0xffffffff,0x12345678][case-53])
        put(SRC+4,[0,0xffffffff,1,0,0x87654321][case-53])
    if case==60:put(SRC+1,STR+1);put(SRC+5,STR+6)
    events=[];abi=[]
    def event(name,a,b=0,c=0):events.append(f'{name}:{h(a)}:{h(b)}:{h(c)};')
    def hook(uc,address,size,data):
        if address==EXIT:uc.emu_stop();return
        if address not in (0x4211d0,0x5a1a40,0x59ecd0,0x5322b0,0x5322c0):return
        esp=uc.reg_read(UC_X86_REG_ESP);a=get(esp+4);result=0xcafe0071
        if address==0x4211d0:
            event('allocate',a,get(esp+8))
            if case in (12,22):machine.mem_write(STR,b'\0')
            if case==13:
                put(OBJ,ALT);put(OBJ+4,ALT);put(OBJ+8,ALT);put(OBJ+12,0x13572468)
            if case==28:put(SRC,ALT);put(SRC+4,ALT)
            result=OBJ if case in (15,23) else STR+2 if case==19 else BLOCK
        elif address==0x5a1a40:
            source,bytes_count=get(esp+8),get(esp+12)
            event('copy',a,source,bytes_count)
            if case in (14,21,29):put(OBJ,ALT);put(OBJ+4,0x12345678);put(OBJ+8,0x87654321)
            if 0<bytes_count<0x10000:machine.mem_write(a,bytes(machine.mem_read(source,bytes_count)))
            result=a
        elif address==0x59ecd0:event('table_release',a)
        elif address==0x5322b0:
            event('enter',a)
            if case==36:put(OBJ,0);put(OBJ+8,0);put(M+0x28,0x88880000)
        else:event('leave',a)
        uc.reg_write(UC_X86_REG_EAX,result);uc.reg_write(UC_X86_REG_ECX,0xcccccccc);uc.reg_write(UC_X86_REG_EDX,0xdddddddd)
        uc.reg_write(UC_X86_REG_EIP,get(esp));uc.reg_write(UC_X86_REG_ESP,esp+4)
    machine.hook_add(UC_HOOK_CODE,hook)
    def invoke(va,ecx,args=(),pop=0,compare_eax=True):
        machine.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
        machine.reg_write(UC_X86_REG_ESP,STACK);machine.reg_write(UC_X86_REG_ECX,ecx)
        machine.reg_write(UC_X86_REG_EDX,0x12345678);machine.reg_write(UC_X86_REG_EAX,0x13579bdf)
        saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
        for reg,value in saved.items():machine.reg_write(reg,value)
        machine.emu_start(va,EXIT+1,count=100000)
        assert machine.reg_read(UC_X86_REG_EIP)==EXIT
        assert machine.reg_read(UC_X86_REG_ESP)==STACK+4+pop
        assert all(machine.reg_read(reg)==value for reg,value in saved.items())
        abi.append({'va':h(va),'stack_pop':pop,'callee_saved_preserved':True,'eax_compared':compare_eax})
        return machine.reg_read(UC_X86_REG_EAX) if compare_eax else 0
    if case<2:result=invoke(0x423610,OBJ if case else 0)
    elif case<4 or case==63:result=invoke(0x505810,OBJ+(1 if case==3 else 0),[OBJ if case==63 else 0xffffffff],4)
    elif case<8 or case==61:result=invoke(0x4d55c0,OBJ,[STR+(1 if case==7 else 0)])
    elif case<16 or case==58:
        result=invoke(0x4d64a0,OBJ,[OBJ if case==11 else STR,0xdeadbeef],8)
        if case==58:invoke(0x429840,OBJ,compare_eax=False)
    elif case<24 or case==59:
        last=STR+(0 if case==16 else 255 if case==18 else 7)
        if case==20:last=STR-2
        result=invoke(0x4298a0,OBJ,[STR,last],8)
        if case==59:result=invoke(0x4d6510,OBJ)
    elif case<30 or case==60:result=invoke(0x429bf0,OBJ,[OBJ if case==26 else OBJ-4 if case==27 else SRC+1 if case==60 else SRC],4)
    elif case<38:result=invoke(0x429840,OBJ,compare_eax=False)
    elif case<45:result=invoke(0x4d6510,OBJ)
    elif case<50:result=invoke(0x4d6520,OBJ,[[0,1,0xffffffff,0x40000000,0x80000001][case-45]],4)
    elif case<53:result=invoke(0x4d6530,OBJ,compare_eax=False)
    else:result=invoke(0x4d67b0,OBJ,[SRC,SRC if case==62 else SRC+4])
    return {'case':case,'result':h(result),'trace':''.join(events),'memory':bytes(machine.mem_read(B,0x5000)).hex()},abi

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/context-services-150/bin/Release/context_services_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN)
    args=parser.parse_args()
    modules=[json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text(encoding='utf-8').splitlines()]
    module=next(x for x in modules if x['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(binary).hexdigest()==SHA
    def original_bytes(start,count):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=start<0x400000+s['rva']+s['raw_size'])
        pos=sec['raw_offset']+start-0x400000-sec['rva'];return binary[pos:pos+count]
    exe=args.probe.read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
    assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c
    assert struct.unpack_from('<H',exe,pe+24)[0]==0x10b
    build=args.probe.resolve().parents[2];cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def compiler_value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert compiler_value('CMAKE_CXX_COMPILER_ID')=='MSVC' and compiler_value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    fixtures=[];abi=[]
    for case in range(64):
        actual=json.loads(subprocess.check_output([str(args.probe),str(case)],text=True,timeout=15))
        expected,checks=oracle(case,binary,module)
        for key in expected:
            if actual[key]!=expected[key]:
                if key=='memory':
                    aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key])
                    at=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                    raise AssertionError(f'case{case} memory +{at:#x}: {aa[at]:02x}!={bb[at]:02x}')
                raise AssertionError(f'case{case} {key}: {actual[key]} != {expected[key]}')
        fixtures.append({'case':case,'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()})
        abi.append({'case':case,'calls':checks})
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf-8').splitlines()]
    pins=[]
    for va in FULL+['005a1a40','004211d0','0059ecd0']:
        f=next(x for x in functions if x['entry_va']==va);spans=[]
        for first,last in f['ranges']:
            raw=original_bytes(int(first,16),int(last,16)+1-int(first,16))
            spans.append({'start_va':first,'end_va_inclusive':last,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        pins.append({'entry_va':va,'ranges':spans})
    compiled=['iterations/v2/001-original-recovery/source/recovered/context_services_probe.cpp',
              'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/context_services.cpp']
    paths=compiled+['iterations/v2/001-original-recovery/runs/150-context-services/CMakeLists.txt',
        'iterations/v2/001-original-recovery/runs/150-context-services/README.md',
        'scripts/research/verify-v2-context-services.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':FULL,
        'full_function_vas':FULL,'partial_function_vas':[],'cases':len(fixtures),
        'native_cpp_equal_original_x86':True,'original_body_pins':pins,
        'native_toolchain':{'compiler_id':'MSVC','compiler_version':compiler_value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':compiler_value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32',
            'native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Complete 20480-byte poisoned arena, defined pointer/integer EAX results, ordered allocation/copy/release/lock effects, original stack cleanup/nonvolatile registers; overlap, unsigned capacity guard, signed SAR and wrapping address arithmetic.',
        'unknown_boundaries':['005a1a40 typed copy service','004211d0 canonical pool allocation','0059ecd0 canonical manager release','005322b0/005322c0 canonical locks','005e4fe8 canonical storage accessor'],
        'copy_fixture_scope':'The private copy boundary records every call; for controlled reversed-range case20 it records huge length and deliberately copies no bytes. Both native and original use exactly this declared boundary, not a recovered huge-range copy.',
        'original_global_pins':[{'va':'005e4fe8','bytes_hex':original_bytes(0x5e4fe8,4).hex(),'sha256':hashlib.sha256(original_bytes(0x5e4fe8,4)).hexdigest()}],
        'original_abi_checks':abi,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':len(FULL),'cases':len(fixtures),'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

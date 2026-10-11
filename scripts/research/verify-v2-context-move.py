import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/154-context-move'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
B,WATCH=0x27000000,0x27001000
STACK,EXIT=0x02200000,0x02210000
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,
    UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,
    UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EFLAGS)
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def h(x):return f'{x & 0xffffffff:08x}'
def cases():
    values=[]
    def add(source,destination,length,group):values.append({'source':source,'destination':destination,'bytes':length,'group':group})
    sizes=list(range(41))+[63,64,65,127,128,129,255,256,257,511]
    for length in sizes:
        for sa in range(4):
            add(WATCH+0x400+sa,WATCH+0x400+sa,length,'self-copy')
            for da in range(4):
                add(WATCH+0x100+sa,WATCH+0x800+da,length,'disjoint-destination-higher')
                add(WATCH+0x800+sa,WATCH+0x100+da,length,'disjoint-destination-lower')
    overlaps=[2,3,4,5,7,8,15,16,27,28,29,31,32,33,35,36,63,64,65,127,128,129,255,256,257,511]
    for length in overlaps:
        for sa in range(4):
            for delta in (1,2,3,4,7,8,15,31):
                if delta>=length:continue
                source=WATCH+0x400+sa
                add(source,source+delta,length,'backward-overlap')
                add(source,source-delta,length,'forward-overlap')
    add(0,0,0,'null-zero');add(0,WATCH+0x100,0,'null-source-zero');add(WATCH+0x100,0,0,'null-destination-zero')
    return values

def oracle(case_id,case,binary,module):
    machine=Uc(UC_ARCH_X86,UC_MODE_32)
    machine.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:
            machine.mem_write(0x400000+sec['rva'],binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    machine.mem_map(B,0x3000);machine.mem_map(STACK-0x10000,0x20000);machine.mem_map(EXIT,0x1000)
    machine.mem_write(B,bytes((i*29+case_id*7+0x31)&255 for i in range(0x3000)))
    accesses=[]
    def memory_read(uc,access,address,size,value,data):
        if WATCH<=address<WATCH+0x1000:
            value=int.from_bytes(uc.mem_read(address,size),'little')
            accesses.append({'op':'r','va':h(address),'bytes':size,'value':h(value)})
    def memory_write(uc,access,address,size,value,data):
        if WATCH<=address<WATCH+0x1000:accesses.append({'op':'w','va':h(address),'bytes':size,'value':h(value & ((1<<(size*8))-1))})
    def hook(uc,address,size,data):
        if address==EXIT:uc.emu_stop()
    machine.hook_add(UC_HOOK_MEM_READ,memory_read);machine.hook_add(UC_HOOK_MEM_WRITE,memory_write);machine.hook_add(UC_HOOK_CODE,hook)
    args=[EXIT,case['destination'],case['source'],case['bytes']]
    machine.mem_write(STACK,struct.pack('<4I',*args));machine.reg_write(UC_X86_REG_ESP,STACK)
    machine.reg_write(UC_X86_REG_EAX,0x13579bdf);machine.reg_write(UC_X86_REG_ECX,0x12345678);machine.reg_write(UC_X86_REG_EDX,0x87654321)
    machine.reg_write(UC_X86_REG_EFLAGS,2)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():machine.reg_write(reg,value)
    machine.emu_start(0x5a1a40,EXIT+1,count=100000)
    assert machine.reg_read(UC_X86_REG_EIP)==EXIT
    assert machine.reg_read(UC_X86_REG_ESP)==STACK+4
    assert all(machine.reg_read(reg)==value for reg,value in saved.items())
    df_clear=(machine.reg_read(UC_X86_REG_EFLAGS)&0x400)==0
    assert df_clear
    return {'case':case_id,'result':h(machine.reg_read(UC_X86_REG_EAX)),
        'direction_flag_clear':df_clear,'memory':bytes(machine.mem_read(B,0x3000)).hex(),'accesses':accesses}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/context-move-154/bin/Release/context_move_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN)
    parser.add_argument('--limit',type=int)
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
    all_cases=cases();selected=all_cases[:args.limit] if args.limit else all_cases
    fixtures=[];native_opcodes=Counter();event_count=0
    for base in range(0,len(selected),64):
        chunk=selected[base:base+64]
        inputs=''.join(f'{base+i} {x["source"]:x} {x["destination"]:x} {x["bytes"]}\n' for i,x in enumerate(chunk))
        output=subprocess.check_output([str(args.probe)],input=inputs,text=True,timeout=45)
        lines=output.splitlines();assert len(lines)==len(chunk)
        for i,(case,line) in enumerate(zip(chunk,lines)):
            case_id=base+i;actual=json.loads(line)
            for access in actual['accesses']:
                opcode=access.pop('native_opcode');native_opcodes[opcode]+=1
                assert opcode in ('008b','0089','008a','0088','0fb6')
                assert access['bytes']==(4 if opcode in ('008b','0089') else 1)
                assert access['op']==('w' if opcode in ('0089','0088') else 'r')
            expected=oracle(case_id,case,binary,module)
            for key in expected:
                if actual[key]!=expected[key]:
                    if key=='memory':
                        aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key])
                        at=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                        raise AssertionError(f'case{case_id} memory +{at:#x}: {aa[at]:02x}!={bb[at]:02x}')
                    if key=='accesses':
                        at=next((i for i,(a,b) in enumerate(zip(actual[key],expected[key])) if a!=b),min(len(actual[key]),len(expected[key])))
                        raise AssertionError(f'case{case_id} access#{at} actual={actual[key][at:at+1]} expected={expected[key][at:at+1]}')
                    raise AssertionError(f'case{case_id} {key}: {actual[key]} != {expected[key]}')
            event_count+=len(expected['accesses'])
            fixtures.append({'case':case_id,**case,'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest(),
                'memory_accesses':len(expected['accesses']),'access_trace_sha256':hashlib.sha256(json.dumps(expected['accesses'],sort_keys=True).encode()).hexdigest()})
        if (base+len(chunk))%512==0:print(json.dumps({'verified_cases':base+len(chunk),'total':len(selected)}),flush=True)
    if args.limit:
        print(json.dumps({'smoke_cases':len(fixtures),'native_cpp_equal_original_x86':True}));return
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text(encoding='utf-8').splitlines()]
    f=next(x for x in functions if x['entry_va']=='005a1a40');spans=[]
    for first,last in f['ranges']:
        raw=original_bytes(int(first,16),int(last,16)+1-int(first,16))
        spans.append({'start_va':first,'end_va_inclusive':last,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    tables=[]
    for address,size,label in [(0x5a1aa0,16,'forward destination alignment'),(0x5a1b1c,32,'forward short DWORD count'),
        (0x5a1b88,16,'forward byte tails'),(0x5a1c28,16,'backward destination end alignment'),
        (0x5a1cb4,32,'backward negated short DWORD count'),(0x5a1d20,16,'backward byte tails')]:
        raw=original_bytes(address,size)
        tables.append({'va':h(address),'bytes':size,'label':label,'bytes_hex':raw.hex(),'sha256':hashlib.sha256(raw).hexdigest()})
    compiled=['iterations/v2/001-original-recovery/source/recovered/context_move_probe.cpp',
              'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/context_move.cpp']
    paths=compiled+['iterations/v2/001-original-recovery/runs/154-context-move/CMakeLists.txt',
        'iterations/v2/001-original-recovery/runs/154-context-move/README.md',
        'scripts/research/verify-v2-context-move.py','research/binary-index/static/binaries.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':['005a1a40'],
        'full_function_vas':['005a1a40'],'partial_function_vas':[],'cases':len(fixtures),
        'native_cpp_equal_original_x86':True,'original_body_pins':[{'entry_va':'005a1a40','ranges':spans}],
        'original_jump_table_pins':tables,
        'native_toolchain':{'compiler_id':'MSVC','compiler_version':compiler_value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':compiler_value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32',
            'native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Full 12288-byte poisoned arena, destination EAX, exact ordered native/original memory read/write address, byte width and payload sequences; original cdecl stack cleanup/nonvolatile registers and cleared DF. Native access observation uses private PAGE_GUARD/VEH single stepping without production instrumentation.',
        'memory_access_events':event_count,'native_access_opcodes':dict(sorted(native_opcodes.items())),
        'case_groups':dict(Counter(x['group'] for x in selected)),
        'original_abi_checks':{'cases':len(fixtures),'stack_pop':0,'callee_saved_preserved':True,'eax_destination_equal':True,'direction_flag_clear':True,'precondition':'Win32 x86 ABI DF clear on entry'},
        'unknown_boundaries':[],'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':1,'cases':len(fixtures),'access_events':event_count,'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

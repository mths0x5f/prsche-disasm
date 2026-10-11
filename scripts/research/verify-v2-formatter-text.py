import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE='iterations/v2/001-original-recovery'
RUN=ROOT/BASE/'runs/158-formatter-text'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
FULL=['005a2248','005a22b7','005a262c','005a269b','005a2eae','005a2c24',
      '005a2c52','005a2c7a','005a2210','005a2e70','005a2870']
B,FIRST,SECOND,TABLE,ALT=0x28000000,0x28000400,0x28000800,0x28001400,0x28002400
STACK,EXIT,INCREMENT,DECREMENT,ALTERNATE=0x2200000,0x2210000,0x2300000,0x2300010,0x2300020
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,
    UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,
    UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EFLAGS)
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def h(x):return f'{x & 0xffffffff:08x}'

def cases():
    rows=[]
    def add(fn,c=0,mask=0xffff,locale=0,width=1,writer=0,variant=0,n=0,left=b'\0',right=b'\0'):
        rows.append(dict(case=len(rows),fn=fn,c=c&0xffffffff,mask=mask&0xffffffff,
            locale=locale,width=width,writer=writer,variant=variant,n=n,left=left,right=right))
    edges=[-0x80000000,-256,-2,-1]+list(range(257))+[0x8141,0xff41,0x7fffffff]
    for fn in range(4):
        for c in edges:add(fn,c)
    for fn in range(4):
        for c in [-1,0,64,65,90,91,96,97,122,123,128,255,256,0x141,0x8141,0xff41]:
            for width in [1,2]:
                for writer in [0,1]:
                    for variant in [0,1,2,3,4,9,17,33,65,129,257,258,260,321,385]:
                        add(fn,c,locale=0x409,width=width,writer=writer,variant=variant)
    for fn in range(4,8):
        for c in [-256,-2,-1]+list(range(257))+[511,0x8141,0xff41,0x7fffffff,0x80000000]:
            for width in [1,2]:
                # Direct wrappers intentionally have no byte-domain guard.
                if fn!=4 and width==1 and c>511:continue
                for variant in ([0,256,512,768] if c in [256,511,0x8141,0xff41,0x7fffffff,0x80000000] else [0]):
                    add(fn,c,mask=[0,1,0x103,0x8765,0xffff,0xffff0000,0xffffffff][(c+fn)%7],width=width,variant=variant)
    strings=[b'',b'A',b'ABC',b'ABCD',b'ABCDE',b'\x80\xffA',b'A'*31,b'AB'*32]
    for left in strings:
        for right in strings:
            for n in sorted({0,1,2,3,4,7,len(left),len(left)+1,len(left)+5,0xffffffff}):
                add(8,n=n,left=left+b'\0',right=right+b'\0'+b'Z'*100)
            add(9,left=left+b'\0',right=right+b'\0')
        for c in [0,65,66,67,0x80,0xff,0x141,0xffffffff]:add(10,c,left=left+b'\0')
    for fn in [8,9]:
        for variant in [2048,4096]:
            for left in strings:
                add(fn,variant=variant,n=0xffffffff,left=left+b'\0',right=b'ABC\0')
    all_bytes=bytes(range(1,256))+b'\0'
    for c in range(256):add(10,c,left=all_bytes)
    add(9,left=all_bytes,right=all_bytes)
    add(9,left=all_bytes,right=b'\xff\0')
    for fn in range(8):
        for width in [-1,0]:
            for c in [-1,65,97,255]:add(fn,c,locale=0x409,width=width,variant=1)
    for fn in [0,2]:
        for writer in [0,1]:
            for variant in [8193,16385,8257,16449]:
                add(fn,65,locale=0x409,writer=writer,variant=variant)
    return rows

def descriptor(row):
    return ('{case} {fn} {c:x} {mask:x} {locale:x} {width} {writer:x} {variant} {n:x} '
        .format(**row)+row['left'].hex()+' '+row['right'].hex()+'\n')

def oracle(row,binary,module,original_table):
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(0x400000+sec['rva'],binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    uc.mem_map(B,0x3000);uc.mem_map(STACK-0x10000,0x20000);uc.mem_map(EXIT,0x1000);uc.mem_map(INCREMENT,0x1000)
    def get(a,size=4):return int.from_bytes(uc.mem_read(a&0xffffffff,size),'little')
    def put(a,x,size=4):uc.mem_write(a&0xffffffff,(x&((1<<(size*8))-1)).to_bytes(size,'little'))
    uc.mem_write(B,bytes((i*23+row['case']*7+0x35)&255 for i in range(0x3000)))
    uc.mem_write(TABLE-2,original_table);uc.mem_write(ALT-2,original_table)
    variant=row['variant']
    if variant&256:
        for v in [1,0x81,0xff]:put(TABLE+v*2+1,get(TABLE+v*2+1,1)|0x80,1)
    first=FIRST+(row['case']&3)
    second=first if variant&2048 else first+1 if variant&4096 else SECOND+((row['case']>>2)&3)
    uc.mem_write(first,row['left']);uc.mem_write(second,row['right'])
    put(0x5e52d0,TABLE);put(0x5e54dc,row['width']);put(0x6afd80,row['locale'])
    put(0x6c02e4,row['writer']);put(0x6c02e8,0x7fffffff if variant&8192 else 0xffffffff if variant&16384 else row['case']*3-17)
    put(0x5b2258,INCREMENT);put(0x5b2254,DECREMENT)
    events=[];reads=[]
    def mutation():
        if variant&64:
            put(0x6afd80,0x4321);put(0x6c02e4,get(0x6c02e4)^1);put(0x5e54dc,2);put(0x5e52d0,ALT)
    def input_event(name,a,b,pointer,count,capacity,cp,strict):
        events.append(f'{name}:{h(a)}:{h(b)}:{h(count)}:'+bytes(uc.mem_read(pointer,count+1)).hex()+f':{h(capacity)}:{h(cp)}:{h(strict)};')
    def hook(machine,address,size,data):
        if address==EXIT:machine.emu_stop();return
        if address not in [INCREMENT,DECREMENT,ALTERNATE,0x5a4ba4,0x5a4c05,0x5a7e05,0x5a98c2]:return
        esp=machine.reg_read(UC_X86_REG_ESP)
        args=[get(esp+4+i*4) for i in range(8)]
        result=0xabcdef12;pop=0
        if address in [INCREMENT,DECREMENT,ALTERNATE]:
            pop=4;pointer=args[0];assert pointer==0x6c02e8
            value=(get(pointer)+(1 if address==INCREMENT else -1))&0xffffffff;put(pointer,value);result=value
            name='increment' if address==INCREMENT else 'decrement' if address==DECREMENT else 'alternate'
            events.append(f'{name}:{h(value)};')
            if address==INCREMENT:
                if variant&8:put(0x6c02e4,get(0x6c02e4)^1)
                if variant&16:put(0x6afd80,0)
            elif address==DECREMENT and variant&32:put(0x5b2254,ALTERNATE)
        elif address==0x5a4ba4:
            events.append(f'lock:{h(args[0])};')
            if variant&128:put(0x6afd80,0)
        elif address==0x5a4c05:events.append(f'unlock:{h(args[0])};')
        elif address==0x5a7e05:
            l,flags,inp,count,out,capacity,cp,strict=args
            input_event('map',l,flags,inp,count,capacity,cp,strict)
            uc.mem_write(out,b'\xa1\xb2\0');mutation()
            if variant&64:put(0x5b2254,ALTERNATE)
            result=0xffffffff if variant&4 else variant&3
        else:
            kind,inp,count,out,cp,l,strict=args[:7]
            input_event('type',kind,l,inp,count,2,cp,strict)
            put(out,0x8765,2);mutation();result=0 if variant&512 else 1
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ECX,0xcccccccc);machine.reg_write(UC_X86_REG_EDX,0xdddddddd)
        machine.reg_write(UC_X86_REG_EIP,get(esp));machine.reg_write(UC_X86_REG_ESP,esp+4+pop)
    def memory(machine,access,address,size,value,data):
        if B<=address<B+0x3000:reads.append(f'r:{h(address)}:{size}:{h(get(address,size))};')
    uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ,memory)
    fn=row['fn'];args=[row['c']]
    if fn==4:args.append(row['mask'])
    elif fn==8:args=[first,second,row['n']]
    elif fn==9:args=[first,second]
    elif fn==10:args=[first,row['c']]
    uc.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
    uc.reg_write(UC_X86_REG_ESP,STACK);uc.reg_write(UC_X86_REG_EFLAGS,2)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():uc.reg_write(reg,value)
    uc.reg_write(UC_X86_REG_EAX,0x13579bdf);uc.reg_write(UC_X86_REG_ECX,0x12345678);uc.reg_write(UC_X86_REG_EDX,0x87654321)
    uc.emu_start(int(FULL[fn],16),EXIT+1,count=100000)
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    width=get(0x5e54dc);width=width if width<0x80000000 else width-0x100000000
    expected={'case':row['case'],'result':h(uc.reg_read(UC_X86_REG_EAX)),'events':''.join(events),'reads':''.join(reads),
        'locale':h(get(0x6afd80)),'writer':h(get(0x6c02e4)),'readers':h(get(0x6c02e8)),
        'width':width,'table':h(get(0x5e52d0)),'decrement_changed':get(0x5b2254)==ALTERNATE,
        'df':(uc.reg_read(UC_X86_REG_EFLAGS)>>10)&1,'memory':bytes(uc.mem_read(B,0x3000)).hex()}
    return expected,len(reads)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/formatter-text-158/bin/Release/formatter_text_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN)
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    module=next(json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines() if json.loads(x)['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(binary).hexdigest()==SHA
    def original_bytes(start,n):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=start<0x400000+s['rva']+max(s['raw_size'],s['vsize']))
        delta=start-0x400000-sec['rva'];available=max(0,min(n,sec['raw_size']-delta))
        offset=sec['raw_offset']+delta
        return binary[offset:offset+available]+bytes(n-available)
    original_table=original_bytes(0x5e52d8,514)
    exe=args.probe.read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
    assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c and struct.unpack_from('<H',exe,pe+24)[0]==0x10b
    build=args.probe.resolve().parents[2];cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert value('CMAKE_CXX_COMPILER_ID')=='MSVC' and value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    rows=cases();rows=rows[:args.limit] if args.limit else rows
    fixtures=[];accesses=0;counts={va:0 for va in FULL}
    for start in range(0,len(rows),64):
        chunk=rows[start:start+64]
        output=subprocess.check_output([str(args.probe),str(ROOT/'local/game'/module['path'])],input=''.join(map(descriptor,chunk)),text=True,timeout=30)
        actual_rows=[json.loads(line) for line in output.splitlines()];assert len(actual_rows)==len(chunk)
        for row,actual in zip(chunk,actual_rows):
            expected,count=oracle(row,binary,module,original_table)
            for key in expected:
                if actual[key]!=expected[key]:
                    raise AssertionError(f'case {row["case"]} fn{row["fn"]} c{h(row["c"])} variant{row["variant"]} {key}: {str(actual[key])[:1500]} != {str(expected[key])[:1500]}')
            counts[FULL[row['fn']]]+=1;accesses+=count
            fixtures.append({'case':row['case'],'entry_va':FULL[row['fn']],
                'input':{k:v for k,v in row.items() if k not in ['left','right']},
                'left_hex':row['left'].hex(),'right_hex':row['right'].hex(),
                'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest(),'read_accesses':count,
                'cdecl_stack_pop':0,'callee_saved_preserved':True,'direction_flag':0})
    if args.limit:print(json.dumps({'checked':len(fixtures)}));return
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    pins=[]
    for va in FULL:
        f=next(x for x in functions if x['entry_va']==va)
        pins.append({'entry_va':va,'ranges':[{'start_va':a,'end_va_inclusive':b,'bytes':int(b,16)+1-int(a,16),
            'sha256':hashlib.sha256(original_bytes(int(a,16),int(b,16)+1-int(a,16))).hexdigest()} for a,b in f['ranges']]})
    global_pins=[{'va':h(a),'bytes':n,'bytes_hex':original_bytes(a,n).hex(),
        'sha256':hashlib.sha256(original_bytes(a,n)).hexdigest()} for a,n in [(0x5e52d0,4),(0x5e52d8,514),(0x5e54dc,4),(0x6afd80,4),(0x6c02e4,4),(0x6c02e8,4)]]
    imports=[json.loads(x) for x in (ROOT/'research/binary-index/static/imports.jsonl').read_text().splitlines()]
    iat=[x for x in imports if x['path']=='Porsche.exe' and int(x['iat_rva'],16) in [0x1b2254,0x1b2258]]
    assert {x['symbol'] for x in iat}=={'InterlockedIncrement','InterlockedDecrement'}
    compiled=[BASE+'/source/recovered/formatter_text_probe.cpp',BASE+'/source/recovered/Porsche.exe/formatter_text.cpp']
    paths=compiled+[BASE+'/runs/158-formatter-text/CMakeLists.txt',BASE+'/runs/158-formatter-text/README.md',
        'scripts/research/verify-v2-formatter-text.py','research/binary-index/static/binaries.jsonl','research/binary-index/static/imports.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':FULL,'full_function_vas':FULL,
        'partial_function_vas':[],'cases':len(fixtures),'native_cpp_equal_original_x86':True,
        'original_body_pins':pins,'original_global_pins':global_pins,'iat_imports':iat,
        'native_toolchain':{'compiler_id':'MSVC','compiler_version':value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32','native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Defined integer/pointer EAX, full 12288-byte poisoned arena, complete ordered source/table reads, ordered atomic/lock/map/classify boundary calls, mutable locale/writer/readers/width/table/atomic pointer state, original cdecl cleanup/nonvolatile registers and DF.',
        'memory_observer':'Private C++ read helper records the value immediately after each volatile load; production has no observer. Original memory reads captured by Unicorn, no guessed host ctype table.',
        'unknown_boundaries':['005a7e05 locale mapping engine','005a98c2 locale classification engine','005a4ba4/005a4c05 canonical CRT locks','005b2258/005b2254 typed Kernel32 atomic imports'],
        'fixture_scope':'Locale engines are controlled typed boundaries: map outputs a1 b2 00 with return 0/1/2/3/-1; classification outputs 8765 with success/failure. Original C table bytes loaded from original PE in native probe; synthetic lead-byte mutations are explicit fixture inputs. No host tolower/toupper/ctype/str* substitutions.',
        'read_accesses':accesses,'case_counts':counts,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':len(FULL),'cases':len(fixtures),'read_accesses':accesses,'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

"""Run166: compare original x86 formatter output against private MSVC Win32 C++."""
import argparse
import hashlib
import itertools
import json
import re
import struct
import subprocess
import sys
from pathlib import Path
from v2_source_dependencies import source_hashes

ROOT=Path(__file__).resolve().parents[2]
BASE='iterations/v2/001-original-recovery'
RUN=ROOT/BASE/'runs/166-formatter-output'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=[0x5abf5e,0x5abfb7,0x5a9e49,0x5a9eae,0x5a9ab8,0x5a9b1d,0x5abef1,0x5abf35,0x5a662b]
NAMES=['id','flags','length','variant','seek','error','cap','failcall','locale','width','cp','value','writer','readers','allocs','origin']
B,INPUT,OUTPUT,DESC,HEAP=0x29000000,0x29004000,0x29005000,0x29007000,0x29008000
STACK,EXIT,BRIDGE=0x2200000,0x2210000,0x2300000
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBP,
                              UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EIP)

def h(x):return f'{x&0xffffffff:08x}'
def cases():
    rows=[]
    def add(fn,**values):
        row=dict(id=0,flags=0x81,length=19,variant=0,seek=0x1234,error=0,cap=0xffffffff,
                 failcall=1,locale=0x409,width=2,cp=932,value=0x12340041,writer=0,readers=7,allocs=9,origin=2)
        row.update(values);row={k:v&0xffffffff for k,v in row.items()};row.update(case=len(rows),fn=fn);rows.append(row)
    for fn,locale,value,variant in itertools.product([0,1],[0,0x409],[0,65,255,256,0xffff,0x12340041,0xffffffff],
                                                    [0,2,8,16,24,256,512,768,1024]):
        add(fn,locale=locale,value=value,variant=variant,cap=2)
    for fn,writer,readers in itertools.product([0,1],[0,1,0xffffffff],[0,0x7fffffff,0xffffffff]):
        add(fn,writer=writer,readers=readers,cap=1,variant=768)
    for width in [-1,0,1,2,4]:add(1,width=width,cap=3)
    for fn,flags,length,cap in itertools.product([2,3],[0,1,0x81,0xa1,0x41,0xe1],
                                               [0,1,4,1023,1024,1025,2048],[0,1,3,1024,0xffffffff]):
        add(fn,flags=flags,length=length,cap=cap)
    for fn,variant,error in itertools.product([2,3],[4,36,68,132,4|4096,4|8192],[0,5,19,109,200,123456]):
        add(fn,flags=0xe1,length=2048,variant=variant,error=error,failcall=2)
    for fn,id,flags,variant in itertools.product([2,3,4,5,7],[0,31,32,63],[0,1,0x81,0xa1,0xe1],[0,32,64,128]):
        add(fn,id=id,flags=flags,variant=variant)
    for fn in [2,4,7]:
        for id in [64,65,0x7fffffff,0x80000000,0xffffffff]:add(fn,id=id)
    for fn,seek,error,variant in itertools.product([4,5],[0,0x80000000,0xffffffff],[0,5,19,109],[0,128,2048]):
        add(fn,seek=seek,error=error,variant=variant,value=0x87654321,origin=0x12345678)
    for fn in [2,3]:
        for variant in [0,4,32,64,128,4096,8192]:
            add(fn,length=4096,variant=variant,failcall=2,error=5)
            add(fn,length=4096,variant=variant,failcall=1,error=109,cap=0)
        for flags,error in itertools.product([1,0x81,0x41],[0,5,19,109]):
            add(fn,flags=flags,variant=4,failcall=1,error=error)
        add(fn,flags=0x41,variant=8192,cap=0,length=1)
        for cap in [0x7fffffff,0x80000000,0xffffffff]:
            add(fn,flags=0x81,variant=32768,cap=cap,length=2048)
    for variant in [0,1,16384]:
        for allocs in [0,0xffffffff]:add(6,variant=variant,allocs=allocs)
    for error in list(range(256))+[1816,0x7fffffff,0x80000000,0xffffffff]:
        add(8,error=error,variant=16384 if error&1 else 0)
    return rows

def descriptor(row):return f'{row["case"]} {row["fn"]} '+' '.join(h(row[k]) for k in NAMES)+'\n'

def original(row,image,module):
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(0x400000+sec['rva'],image[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    uc.mem_map(B,0x10000);uc.mem_map(STACK-0x10000,0x10000);uc.mem_map(STACK,0x2000);uc.mem_map(EXIT,0x1000);uc.mem_map(BRIDGE,0x1000)
    def get(a,n=4):return int.from_bytes(uc.mem_read(a&0xffffffff,n),'little')
    def put(a,value,n=4):uc.mem_write(a&0xffffffff,(value&((1<<(n*8))-1)).to_bytes(n,'little'))
    uc.mem_write(B,bytes((i*13+row['case']*7+0x21)&255 for i in range(0x10000)))
    for bank in range(3):
        for i in range(32):
            a=B+0x1000+bank*0x1000+i*36;put(a,0x7000+bank*0x100+i);put(a+4,row['flags']^(0xc0 if bank==2 else 0),1)
    variant=row['variant']
    uc.mem_write(INPUT,bytes(0x1a if variant&8192 else 10 if variant&4096 else 10 if i%11==3 else ord('A')+i%26 for i in range(4096)))
    uc.mem_write(0x6c01e0,bytes(256));put(0x6c01e0,B+0x1000);put(0x6c01e4,B+0x2000);put(0x6c02e0,64)
    for a,k in [(0x6afd80,'locale'),(0x6c02e4,'writer'),(0x6c02e8,'readers'),(0x6afd90,'cp'),(0x5e54dc,'width'),(0x6afcf8,'allocs')]:put(a,row[k])
    put(B+0x100,0x11111111);put(B+0x104,0x22222222)
    api={0x5b21f0:('write',5),0x5b223c:('seek',4),0x5b213c:('error',0),0x5b2110:('wide',8),
         0x5b2258:('inc',1),0x5b2254:('decA',1)}
    stubs={}
    for i,(iat,info) in enumerate(api.items()):
        address=BRIDGE+0x100+i*16;put(iat,address);stubs[address]=info
    dec_b=BRIDGE+0x300;stubs[dec_b]=('decB',1)
    boundaries={0x5a669e:'errno',0x5a66a7:'doserrno',0x5ab726:'lockfile',0x5ab785:'unlockfile',
                0x5ab6e4:'handle',0x5a3be5:'malloc',0x5a4ba4:'lockcrt',0x5a4c05:'unlockcrt'}
    events=[];writes=0
    def event(name,values=()):events.append(name+''.join(':'+h(x) for x in values)+';')
    def swap_bank():put(0x6c01e0+((row['id']&63)>>5)*4,B+0x3000)
    def hook(machine,address,size,data):
        nonlocal writes
        if address==EXIT:machine.emu_stop();return
        if address not in stubs and address not in boundaries:return
        esp=machine.reg_read(UC_X86_REG_ESP);a=[get(esp+4+i*4) for i in range(8)];result=0xabcdef12;pop=0
        if address in boundaries:
            name=boundaries[address]
            if name=='errno':event(name);result=B+0x100
            elif name=='doserrno':
                event(name);result=B+0x104
                if variant&16384:put(B+0x100,0x55667788)
            elif name in ['lockfile','unlockfile','lockcrt','unlockcrt']:
                event(name,a[:1])
                if name=='lockfile' and variant&32:swap_bank()
            elif name=='handle':
                event(name,a[:1]);result=0xffffffff if variant&2048 else get(get(0x6c01e0+(a[0]>>5)*4)+(a[0]&31)*36)
            elif name=='malloc':event(name,[a[0],get(0x6afcf8)]);result=0 if variant&1 else HEAP
        else:
            name,nargs=stubs[address];pop=nargs*4
            if name=='write':
                handle,ptr,n,written,overlapped=a[:5];writes+=1;amount=row['cap'] if variant&32768 else min(n,row['cap']);put(written,amount)
                fail=bool(variant&4 and writes==row['failcall']);event(name,[handle,n,int(bool(overlapped)),amount,int(not fail)])
                events.append('data:'+bytes(uc.mem_read(ptr,n)).hex()+';')
                if variant&64:swap_bank()
                result=int(not fail)
            elif name=='seek':
                event(name,a[:4]);result=row['seek']
                if variant&128:swap_bank()
            elif name=='error':event(name,[row['error']]);result=row['error']
            elif name=='wide':
                cp,flags,ptr,n,out,cap,fallback,used=a;event(name,[cp,flags,get(ptr,2),n,cap,int(bool(fallback)),int(bool(used))])
                if cap<0x80000000:
                    for i in range(min(cap,4)):put(out+i,0x91+i,1)
                put(used,int(bool(variant&8)))
                if variant&512:put(0x5b2254,dec_b)
                result=0 if variant&16 else row['cap']
            else:
                old=get(a[0]);event(name,[old]);result=old+(1 if name=='inc' else -1);put(a[0],result)
                if name=='inc':
                    if variant&256:put(0x5b2254,dec_b)
                    if variant&1024:put(0x6c02e4,get(0x6c02e4)^1)
        machine.reg_write(UC_X86_REG_EAX,result&0xffffffff);machine.reg_write(UC_X86_REG_ECX,0xcccccccc);machine.reg_write(UC_X86_REG_EDX,0xdddddddd)
        machine.reg_write(UC_X86_REG_EIP,get(esp));machine.reg_write(UC_X86_REG_ESP,esp+4+pop)
    uc.hook_add(UC_HOOK_CODE,hook)
    fn=row['fn']
    args=[0 if variant&2 else OUTPUT,row['value']] if fn in [0,1] else [row['id'],INPUT,row['length']] if fn in [2,3] else [row['id'],row['value'],row['origin']] if fn in [4,5] else [DESC] if fn==6 else [row['id']] if fn==7 else [row['error']]
    uc.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args));uc.reg_write(UC_X86_REG_ESP,STACK)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():uc.reg_write(reg,value)
    uc.emu_start(VAS[fn],EXIT+1,count=500000)
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    return {'case':row['case'],'result':h(uc.reg_read(UC_X86_REG_EAX)),'events':''.join(events),
            'allocs':h(get(0x6afcf8)),'readers':h(get(0x6c02e8)),'writer':h(get(0x6c02e4)),
            'decrement':int(get(0x5b2254)==dec_b),'banks':[h(get(0x6c01e0)),h(get(0x6c01e4))],
            'memory':bytes(uc.mem_read(B,0x10000)).hex()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/formatter-output-166/bin/Release/formatter_output_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN);parser.add_argument('--limit',type=int);parser.add_argument('--start',type=int,default=0)
    args=parser.parse_args()
    module=next(json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines() if json.loads(x)['file']=='Porsche.exe')
    image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    def raw(a,n):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=a and a+n<=0x400000+s['rva']+max(s['raw_size'],s['vsize']))
        d=a-0x400000-sec['rva'];available=max(0,min(n,sec['raw_size']-d));offset=sec['raw_offset']+d
        return image[offset:offset+available]+bytes(n-available)
    include=ROOT/BASE/'source/recovered/Porsche.exe/formatter_output_data.inc'
    data=struct.pack('<90I',*(int(x,16) for x in re.findall(r'0x([0-9a-f]{8})u',include.read_text())))
    assert data==raw(0x5e5a20,360) and raw(0x6afcf8,4)==bytes(4)
    exe=args.probe.read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
    assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c and struct.unpack_from('<H',exe,pe+24)[0]==0x10b
    build=args.probe.resolve().parents[2];cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert value('CMAKE_CXX_COMPILER_ID')=='MSVC' and value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    rows=cases();rows=rows[args.start:args.start+args.limit] if args.limit else rows[args.start:]
    fixtures=[];counts={h(va):0 for va in VAS}
    for start in range(0,len(rows),8):
        chunk=rows[start:start+8]
        output=subprocess.check_output([str(args.probe)],input=''.join(map(descriptor,chunk)),text=True,timeout=30)
        actual_rows=[json.loads(x) for x in output.splitlines()];assert len(actual_rows)==len(chunk)
        for row,actual in zip(chunk,actual_rows):
            expected=original(row,image,module)
            for key in expected:
                if actual[key]!=expected[key]:
                    if key=='memory':
                        aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key]);i=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                        raise AssertionError(f'case{row["case"]} fn{row["fn"]} memory+{i:#x}: {aa[i]:02x}!={bb[i]:02x}; {row}')
                    raise AssertionError(f'case{row["case"]} fn{row["fn"]} {key}: {str(actual[key])[:2000]} != {str(expected[key])[:2000]}; {row}')
            counts[h(VAS[row['fn']])]+=1
            fixtures.append({'entry_va':h(VAS[row['fn']]),'input':row,'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest(),
                             'abi':{'eax_compared':True,'cdecl_stack_pop':0,'callee_saved_preserved':True}})
    if args.limit or args.start:print(json.dumps({'checked':len(fixtures)}));return
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    def pin(a,n):return {'start_va':h(a),'end_va_inclusive':h(a+n-1),'bytes':n,'sha256':hashlib.sha256(raw(a,n)).hexdigest()}
    pins=[{'entry_va':h(va),'ranges':[pin(int(a,16),int(b,16)-int(a,16)+1) for a,b in next(f for f in functions if f['entry_va']==h(va))['ranges']]} for va in VAS]
    imports=[json.loads(x) for x in (ROOT/'research/binary-index/static/imports.jsonl').read_text().splitlines()]
    iats=[x for x in imports if x['path']=='Porsche.exe' and 0x400000+int(x['iat_rva'],16) in [0x5b21f0,0x5b223c,0x5b213c,0x5b2110,0x5b2258,0x5b2254]];assert len(iats)==6
    compiled=[BASE+'/source/recovered/formatter_output_probe.cpp',BASE+'/source/recovered/Porsche.exe/formatter_output.cpp',BASE+'/source/recovered/Porsche.exe/formatter_cleanup.cpp']
    paths=compiled+[BASE+'/runs/166-formatter-output/CMakeLists.txt',BASE+'/runs/166-formatter-output/README.md',
        'scripts/research/verify-v2-formatter-output.py','research/binary-index/static/binaries.jsonl','research/binary-index/static/imports.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':list(counts),'full_function_vas':list(counts),'partial_function_vas':[],
            'cases':len(fixtures),'native_cpp_equal_original_x86':True,'original_body_pins':pins,
            'original_global_pins':[dict(pin(a,n),va=h(a),bytes_hex=raw(a,n).hex()) for a,n in [(0x5e5a20,360),(0x6afcf8,4),(0x5e54dc,4),(0x6afd80,4),(0x6afd90,4),(0x6c02e4,8)]],
            'error_table_include_equal_original':True,'iat_imports':iats,'native_toolchain':{'compiler_id':'MSVC','compiler_version':value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32','native_pe_machine':'014c','native_pe_magic':'010b'},
            'comparison':'Defined EAX including pointer returns; complete65536-byte poisoned arena with banks/descriptors/input/output/error cells; ordered OS/CRT/lock/atomic boundaries, exact WriteFile buffers and wide-input arguments; mutable bank pointer reloads, locale decrement snapshots, reader/count wrap, canonical global effects; original cdecl cleanup and nonvolatile registers.',
            'unknown_boundaries':['Canonical152 lowio lock/unlock/handle','Canonical157 errno/doserrno/malloc/CRT locks','Six exact Kernel32 imports'],
            'case_counts':counts,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True);(args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':9,'cases':len(fixtures),'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

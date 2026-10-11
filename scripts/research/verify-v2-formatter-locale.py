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
RUN=ROOT/BASE/'runs/162-formatter-locale'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
FULL=['005a7e05','005a98c2','005ad2bf','005a6895','005a6a42','005a6a8c','005a6abf','005a6ae8','005a6c6d']
PARAMS=['mm','mt','request','flags','count','capacity','cp','lcid','strict','variant','query','converted','mapped','encoded','max_info','current','once']
B,INPUT,OUTPUT=0x29000000,0x29001000,0x29002000
STACK,EXIT,BRIDGE=0x2200000,0x2210000,0x2300000
IMPORTS={0x5b2108:('mapW',6),0x5b210c:('mapA',6),0x5b2178:('toW',6),0x5b2110:('fromW',8),
    0x5b20d0:('typeW',4),0x5b20d4:('typeA',5),0x5b2114:('OEMCP',0),0x5b2118:('ACP',0),0x5b211c:('CPInfo',2)}
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESP,
    UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI)
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def h(x):return f'{x&0xffffffff:08x}'
def signed(x):return x if x<0x80000000 else x-0x100000000

def cases():
    rows=[]
    def add(fn,**values):
        row=dict(mm=1,mt=1,request=1252,flags=0x100,count=7,capacity=8,cp=0,lcid=0x409,
            strict=1,variant=0,query=3,converted=2,mapped=4,encoded=5,max_info=2,current=0,once=0,
            text=b'Ab\x81Z\xff09\0')
        row.update(values);row.update(case=len(rows),fn=fn)
        for k in PARAMS:row[k]&=0xffffffff
        rows.append(row)
    for fn in [0,1]:
        for mode in [0,1,2,3,0xffffffff]:
            for variant in [0,1,2,3,4,8,16,32,64,128,256,384,512,4096,8192,16384,32768,0x100000]:
                for cp in [0,932]:
                    add(fn,mm=mode,mt=mode,variant=variant,cp=cp,flags=0x100 if fn==0 else 1)
        for count in [0,1,2,7,8,-1,-2]:
            for strict in [0,1,-1]:
                for lcid in [0,0x411]:add(fn,count=count,strict=strict,lcid=lcid,flags=0x200 if fn==0 else 2)
    for mode in [0,1,2]:
        for cap in [-1,0,1,3,4,5,8]:
            for flags in [0x400,0x401,0x500,0x100]:
                for variant in [0,32,64,8192]:add(0,mm=mode,capacity=cap,flags=flags,variant=variant)
    for fn in [0,1]:
        for query,converted,mapped,encoded in [(1,1,1,1),(2,1,2,1),(4,3,3,2),(256,255,256,256),(0,0,0,0)]:
            add(fn,query=query,converted=converted,mapped=mapped,encoded=encoded,flags=1 if fn else 0x100)
    for text in [b'\0',b'A\0',b'ABCD\0',b'AB\0CD\0',bytes(range(1,256))+b'\0']:
        for count in [0,1,2,3,4,5,255,256,0xffffffff]:add(2,text=text,count=count)
    for requested in [-4,-3,-2,-1,0,1,932,936,949,950,1361,1252,65001,0x7fffffff,0x80000000]:
        add(4,request=requested);add(5,request=requested)
        for variant in [0,32768]:add(4,request=requested,variant=variant)
    for i in range(8):add(6,current=932+i)
    for fn in [3,7,8]:
        requests=[-4,-3,-2,-1,0,932,936,949,950,1361,1252,65001] if fn==3 else [1252]
        for request in requests:
            for modes in [1,2]:
                for max_info in [1,2,0xffffffff]:
                    for variant in [0,1024,2048,3072,32768,65536]:
                        add(fn,request=request,mm=modes,mt=modes,max_info=max_info,variant=variant,
                            query=256,converted=256,mapped=256,encoded=256)
        add(fn,current=1252,once=1,query=256,converted=256,mapped=256,encoded=256)
    # SEH fallbacks at both map allocation sites and classifier allocation/memset.
    for fn in [0,1]:
        for variant in [4096,8192,16384]:
            add(fn,variant=variant,query=256,converted=256,mapped=256,encoded=256)
    for variant in [0,1024,32768,33792]:
        add(3,request=0,current=932,variant=variant,query=256,converted=256,mapped=256,encoded=256)
    add(8,variant=33792,query=256,converted=256,mapped=256,encoded=256)
    return rows

def descriptor(row):return f'{row["case"]} {row["fn"]} '+' '.join(h(row[k]) for k in PARAMS)+' '+row['text'].hex()+'\n'

def oracle(row,binary,module):
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0,0x1000);uc.mem_map(0x400000,0x300000)
    for sec in module['sections']:
        if sec['raw_size']:uc.mem_write(0x400000+sec['rva'],binary[sec['raw_offset']:sec['raw_offset']+sec['raw_size']])
    uc.mem_map(B,0x4000);uc.mem_map(STACK-0x40000,0x50000);uc.mem_map(EXIT,0x1000);uc.mem_map(BRIDGE,0x1000)
    def get(a,n=4):return int.from_bytes(uc.mem_read(a&0xffffffff,n),'little')
    def put(a,value,n=4):uc.mem_write(a&0xffffffff,(value&((1<<(n*8))-1)).to_bytes(n,'little'))
    put(0,0xdeadf00d)
    uc.mem_write(B,bytes((i*13+row['case']*3+0x21)&255 for i in range(0x4000)))
    uc.mem_write(0x6c02ec,bytes((i*31+row['case']*9+0x63)&255 for i in range(0x21c)))
    put(0x6c02ec,row['current']);put(0x6afd68,0x55);put(0x6afd90,1252)
    put(0x6afd98,row['mm']);put(0x6afec4,row['mt']);put(0x6c152c,row['once']);put(0x6afd80,0x409)
    input_address=OUTPUT if row['variant']&0x100000 else INPUT;uc.mem_write(input_address,row['text'])
    stubs={}
    for index,(iat,description) in enumerate(IMPORTS.items()):
        address=BRIDGE+0x100+index*16;put(iat,address);stubs[address]=description
    events=[];cp_calls=0;zeroed=None;pending_handler=None;exceptions=[];stack_calls=[]
    def event(name,values=()):events.append(name+''.join(':'+h(x) for x in values)+';')
    def effective(pointer,count,unit):
        count=signed(count)
        if count==-1:
            for i in range(512):
                if not get(pointer+i*unit,unit):return i+1
            return 512
        return max(0,min(count,512))
    def api(name,values,pointer,count,unit):
        event(name,values);events.append('data:'+bytes(uc.mem_read(pointer,effective(pointer,count,unit)*unit)).hex()+';')
    def mutate():
        if row['variant']&32768:
            put(0x6afd90,0x9876);put(0x6afd80,0x7654);put(0x6c02ec,0x5432);put(0x6c0504,0x4321)
    def dispatch(filter_va,handler_va,esp):
        nonlocal pending_handler
        frame=uc.reg_read(UC_X86_REG_EBP)
        scope=get(frame-8)+12*get(frame-4)
        assert get(scope)==0xffffffff
        assert (get(scope+4),get(scope+8))==(filter_va,handler_va)
        pending_handler=handler_va;put(esp,BRIDGE);uc.reg_write(UC_X86_REG_EIP,filter_va)
        exceptions.append({'filter_va':h(filter_va),'handler_va':h(handler_va),'dispatcher':'controlled OS SEH boundary'})
    def hook(machine,address,size,data):
        nonlocal cp_calls,zeroed,pending_handler
        if address==EXIT:machine.emu_stop();return
        if address==BRIDGE:
            assert machine.reg_read(UC_X86_REG_EAX)==1 and pending_handler
            machine.reg_write(UC_X86_REG_EIP,pending_handler);pending_handler=None;return
        esp=machine.reg_read(UC_X86_REG_ESP)
        if address==0x5a1e90:
            return_address=get(esp);site={0x5a7f07:0,0x5a7fbb:1,0x5a99a6:2}[return_address]
            fail=bool(row['variant']&(8192 if site==1 else 4096));n=machine.reg_read(UC_X86_REG_EAX)
            event('stack',[n,site,int(fail)]);stack_calls.append({'bytes':n,'site':site,'exception':fail})
            if fail:
                filter_va,handler={0:(0x5a7f15,0x5a7f19),1:(0x5a7fc9,0x5a7fcd),2:(0x5a99bb,0x5a99bf)}[site]
                dispatch(filter_va,handler,esp)
            return
        if address not in stubs and address not in [0x5a4ba4,0x5a4c05,0x5abe90]:return
        a=[get(esp+4+i*4) for i in range(8)];result=0xabcdef12;pop=0;variant=row['variant']
        if address==0x5a4ba4:
            event('lock',a[:1])
            if variant&65536:put(0x6c02ec,row['request'])
        elif address==0x5a4c05:event('unlock',a[:1])
        elif address==0x5abe90:
            dest,value,n=a[:3];fail=bool(variant&16384);event('memset',[value,n,int(fail)])
            if fail:dispatch(0x5a99bb,0x5a99bf,esp);return
            uc.mem_write(dest,bytes([value&255])*n);zeroed=dest;result=dest
        else:
            name,nargs=stubs[address];pop=nargs*4
            if name in ['mapW','mapA']:
                locale,flags,inp,count,out,cap=a[:6];unit=2 if name=='mapW' else 1
                api(name,[locale,flags,count,int(bool(out)),cap],inp,count,unit)
                probe=count==1 and get(inp,unit)==0 and locale==0 and flags==0x100 and not out
                if name=='mapA':
                    if out and signed(cap)>0:
                        for i in range(min(effective(inp,count,1),cap)):put(out+i,get(inp+i,1)+(7 if flags==0x100 else -7),1)
                    result=(0 if variant&2 else 1) if probe else row['encoded']
                elif probe:result=0 if variant&1 else 1
                else:
                    if out and signed(cap)>0:
                        for i in range(min(cap,row['mapped'])):put(out+i*(1 if flags&0x400 else 2),0x91+i if flags&0x400 else 0x5100+i,1 if flags&0x400 else 2)
                    result=0 if variant&(32 if out else 16) else row['encoded'] if out else row['mapped']
                mutate()
            elif name=='toW':
                cp,flags,inp,count,out,cap=a[:6];api(name,[cp,flags,count,int(bool(out)),cap],inp,count,1)
                if out and out==zeroed:events.append('prezero:'+bytes(uc.mem_read(out,cap*2)).hex()+';');zeroed=None
                if out and signed(cap)>0:
                    for i in range(cap):put(out+i*2,0x4100+i,2)
                mutate();result=0 if variant&(8 if out else 4) else row['converted'] if out else row['query']
            elif name=='fromW':
                cp,flags,inp,count,out,cap,fallback,used=a
                api(name,[cp,flags,count,int(bool(out)),cap,int(bool(fallback)),int(bool(used))],inp,count,2)
                if out and signed(cap)>0:
                    for i in range(min(cap,row['encoded'])):put(out+i,0x61+i,1)
                mutate();result=0 if variant&64 else row['encoded']
            elif name in ['typeW','typeA']:
                if name=='typeW':kind,inp,count,out=a[:4];values=[kind,count];unit=2;probe=count==1 and not get(inp,2)
                else:locale,kind,inp,count,out=a[:5];values=[locale,kind,count];unit=1;probe=count==1 and not get(inp,1) and locale==0 and kind==1
                api(name,values,inp,count,unit)
                for i in range(effective(inp,count,unit)):put(out+i*2,0x200+i%3+1,2)
                mutate();result=0 if variant&((128 if name=='typeW' else 256) if probe else 512) else 1
            elif name in ['OEMCP','ACP']:
                result=932 if name=='OEMCP' else 1252;event(name,[result])
                if variant&32768:put(0x6afd68,0)
            else:
                cp,out=a[:2];cp_calls+=1;event(name,[cp,cp_calls]);uc.mem_write(out,bytes(20))
                put(out,row['max_info']);put(out+4,ord('?'),1);uc.mem_write(out+6,bytes.fromhex('8182908fe0e2000000000000'))
                mutate();result=0 if variant&(1024 if cp_calls==1 else 2048) else 1
        machine.reg_write(UC_X86_REG_EAX,result);machine.reg_write(UC_X86_REG_ECX,0xcccccccc);machine.reg_write(UC_X86_REG_EDX,0xdddddddd)
        machine.reg_write(UC_X86_REG_EIP,get(esp));machine.reg_write(UC_X86_REG_ESP,esp+4+pop)
    uc.hook_add(UC_HOOK_CODE,hook)
    fn=row['fn'];args=[]
    if fn==0:args=[row['lcid'],row['flags'],input_address,row['count'],OUTPUT,row['capacity'],row['cp'],row['strict']]
    elif fn==1:args=[row['flags'],input_address,row['count'],OUTPUT,row['cp'],row['lcid'],row['strict']]
    elif fn==2:args=[input_address,row['count']]
    elif fn in [3,4,5]:args=[row['request']]
    uc.mem_write(STACK,struct.pack('<'+'I'*(len(args)+1),EXIT,*args))
    uc.reg_write(UC_X86_REG_ESP,STACK)
    saved={UC_X86_REG_EBX:0xb1b2b3b4,UC_X86_REG_EBP:0xc1c2c3c4,UC_X86_REG_ESI:0xd1d2d3d4,UC_X86_REG_EDI:0xe1e2e3e4}
    for reg,value in saved.items():uc.reg_write(reg,value)
    uc.emu_start(int(FULL[fn],16),EXIT+1,count=300000)
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT and uc.reg_read(UC_X86_REG_ESP)==STACK+4 and get(0)==0xdeadf00d
    assert all(uc.reg_read(reg)==value for reg,value in saved.items())
    expected={'case':row['case'],'result':h(uc.reg_read(UC_X86_REG_EAX)) if fn<6 else h(0),'events':''.join(events),
        'resolved':h(get(0x6afd68)),'default_cp':h(get(0x6afd90)),'map_mode':h(get(0x6afd98)),
        'type_mode':h(get(0x6afec4)),'initialized':h(get(0x6c152c)),'locale':h(get(0x6afd80)),
        'state':bytes(uc.mem_read(0x6c02ec,0x21c)).hex(),'memory':bytes(uc.mem_read(B,0x4000)).hex()}
    return expected,{'seh_chain_restored':True,'callee_saved_preserved':True,'cdecl_stack_pop':0,
        'eax_compared':fn<6,'stack_allocations':stack_calls,'exceptions':exceptions}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--probe',type=Path,default=ROOT/'local/builds/v2/formatter-locale-162/bin/Release/formatter_locale_probe.exe')
    parser.add_argument('--report-dir',type=Path,default=RUN);parser.add_argument('--limit',type=int);parser.add_argument('--start',type=int,default=0)
    args=parser.parse_args()
    module=next(json.loads(x) for x in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines() if json.loads(x)['file']=='Porsche.exe')
    binary=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(binary).hexdigest()==SHA
    def raw(start,n):
        sec=next(s for s in module['sections'] if 0x400000+s['rva']<=start<0x400000+s['rva']+max(s['raw_size'],s['vsize']))
        d=start-0x400000-sec['rva'];available=max(0,min(n,sec['raw_size']-d));offset=sec['raw_offset']+d
        return binary[offset:offset+available]+bytes(n-available)
    preset_include=ROOT/BASE/'source/recovered/Porsche.exe/formatter_locale_data.inc'
    preset_bytes=bytes(int(x,16) for x in re.findall(r'0x([0-9a-fA-F]{2})',preset_include.read_text(encoding='utf-8')))
    assert preset_bytes==raw(0x5e5b90,248)
    assert raw(0x5c1bac,12)==bytes(12)
    initial_cells=[(0x6afd68,4),(0x6afd90,4),(0x6afd98,4),(0x6afec4,4),(0x6c02ec,0x21c),(0x6c152c,4)]
    assert all(raw(a,n)==bytes(n) for a,n in initial_cells)
    scope_entries=[struct.unpack('<III',raw(a,12)) for a in [0x5c1bb8,0x5c1bc4,0x5c1ec0]]
    assert scope_entries==[(0xffffffff,0x5a7f15,0x5a7f19),(0xffffffff,0x5a7fc9,0x5a7fcd),(0xffffffff,0x5a99bb,0x5a99bf)]
    exe=args.probe.read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
    assert exe[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<H',exe,pe+4)[0]==0x14c and struct.unpack_from('<H',exe,pe+24)[0]==0x10b
    build=args.probe.resolve().parents[2];cache=(build/'CMakeCache.txt').read_text(encoding='utf-8')
    assert re.search(r'^CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32$',cache,re.M)
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text(encoding='utf-8')
    def value(key):return re.search(r'set\('+key+r' "?([^"\)]+)"?\)',compiler)[1]
    assert value('CMAKE_CXX_COMPILER_ID')=='MSVC' and value('CMAKE_CXX_SIZEOF_DATA_PTR')=='4'
    rows=cases();rows=rows[args.start:args.start+args.limit] if args.limit else rows[args.start:]
    fixtures=[];counts={va:0 for va in FULL};exceptions=0
    for start in range(0,len(rows),32):
        chunk=rows[start:start+32];output=subprocess.check_output([str(args.probe)],input=''.join(map(descriptor,chunk)),text=True,timeout=30)
        actual_rows=[json.loads(x) for x in output.splitlines()];assert len(actual_rows)==len(chunk)
        for row,actual in zip(chunk,actual_rows):
            expected,abi=oracle(row,binary,module)
            for key in expected:
                if actual[key]!=expected[key]:
                    if key in ['state','memory']:
                        aa,bb=bytes.fromhex(actual[key]),bytes.fromhex(expected[key]);i=next(i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b)
                        raise AssertionError(f'case{row["case"]} fn{row["fn"]} {key}+{i:#x}: {aa[i]:02x}!={bb[i]:02x}; {row}')
                    raise AssertionError(f'case{row["case"]} fn{row["fn"]} {key}: {str(actual[key])[:3000]} != {str(expected[key])[:3000]}')
            counts[FULL[row['fn']]]+=1;exceptions+=len(abi['exceptions'])
            fixtures.append({'case':row['case'],'entry_va':FULL[row['fn']],'input':{k:v for k,v in row.items() if k!='text'},
                'text_hex':row['text'].hex(),'sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest(),'abi':abi})
    if args.limit or args.start:print(json.dumps({'checked':len(fixtures),'exception_cases':exceptions}));return
    functions=[json.loads(x) for x in (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()]
    def pin(a,b):return {'start_va':h(a),'end_va_inclusive':h(b),'bytes':b-a+1,'sha256':hashlib.sha256(raw(a,b-a+1)).hexdigest()}
    pins=[{'entry_va':va,'ranges':[pin(int(a,16),int(b,16)) for a,b in next(x for x in functions if x['entry_va']==va)['ranges']]} for va in FULL]
    seh_ranges=[(0x5a7f15,0x5a7f27),(0x5a7fc9,0x5a7fda),(0x5a99bb,0x5a99c5),(0x5c1bb8,0x5c1bcf),(0x5c1ec0,0x5c1ecb)]
    globals=[(0x5e5b90,248),(0x5c1bac,12),(0x6afd68,4),(0x6afd90,4),(0x6afd98,4),(0x6afec4,4),(0x6c02ec,0x21c),(0x6c152c,4)]
    imports=[json.loads(x) for x in (ROOT/'research/binary-index/static/imports.jsonl').read_text().splitlines()]
    iat=[x for x in imports if x['path']=='Porsche.exe' and 0x400000+int(x['iat_rva'],16) in IMPORTS]
    assert len(iat)==9
    compiled=[BASE+'/source/recovered/formatter_locale_probe.cpp',BASE+'/source/recovered/Porsche.exe/formatter_locale.cpp']
    paths=compiled+[BASE+'/runs/162-formatter-locale/CMakeLists.txt',BASE+'/runs/162-formatter-locale/README.md',
        'scripts/research/verify-v2-formatter-locale.py','research/binary-index/static/binaries.jsonl','research/binary-index/static/imports.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl','research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl','research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':FULL,'full_function_vas':FULL,'partial_function_vas':[],
        'cases':len(fixtures),'native_cpp_equal_original_x86':True,'original_body_pins':pins,'original_seh_pins':[pin(a,b) for a,b in seh_ranges],
        'original_stack_helper_pin':pin(0x5a1e90,0x5a1ebe),
        'original_global_pins':[{'va':h(a),'bytes':n,'bytes_hex':raw(a,n).hex(),'sha256':hashlib.sha256(raw(a,n)).hexdigest()} for a,n in globals],
        'iat_imports':iat,'native_toolchain':{'compiler_id':'MSVC','compiler_version':value('CMAKE_CXX_COMPILER_VERSION'),
            'compiler':value('CMAKE_CXX_COMPILER'),'pointer_size':4,'generator_platform':'Win32','native_pe_machine':'014c','native_pe_magic':'010b'},
        'comparison':'Defined EAX; complete 16384-byte poisoned arena and 540-byte codepage state; ordered API/lock/stack-allocation/memset effects; all callback input bytes, output capacities and strict/default arguments; mutable mode/locale/codepage/once flags; original cdecl cleanup/nonvolatile registers/FS SEH chain.',
        'seh_proof':'Native RaiseException in private stack observer or memset boundary is caught by actual MSVC __try/__except(1). Oracle models the OS exception-dispatch boundary, executes original filter (assert return1), then original handler bytes from indexed scope tables. Successful original005a1e90 executes unmodified, not replaced by heap allocation. Exception paths compare complete outputs/state/effects and restored chain.',
        'native_seh_chain_checked':True,'preset_include_equal_original':True,'initial_zero_cells_checked':True,
        'seh_scope_entries':[{'enclosing_scope':h(parent),'filter_va':h(f),'handler_va':h(handler)} for parent,f,handler in scope_entries],
        'exception_cases':exceptions,'unknown_boundaries':['Nine exact Kernel32 imports pinned by IAT identity','005a4ba4/005a4c05 canonical CRT locks','005abe90 canonical memset'],
        'case_counts':counts,'fixtures':fixtures,'source_sha256':source_hashes(paths,compiled_sources=compiled),'probe_sha256':hashlib.sha256(exe).hexdigest()}
    args.report_dir.mkdir(parents=True,exist_ok=True);(args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'full_functions':9,'cases':len(fixtures),'exception_cases':exceptions,'native_cpp_equal_original_x86':True}))

if __name__=='__main__':main()

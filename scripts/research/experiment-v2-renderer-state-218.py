"""One original renderer-state consumer: PE dataflow, bounded native COFF/fixture.

Frozen inputs, no Ghidra, registry, game, provider, production or union writes.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'218-renderer-state-consumer'
OUT=ROOT/'local/experiments/v2-renderer-state-consumer-218'
VA='00537b40'
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


abi=module('abi218','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff218','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER='''#pragma once
static_assert(sizeof(void*)==4 && sizeof(int)==4 && sizeof(uint)==4,"original raw32 ABI");
typedef undefined4 (__stdcall *OriginalSetState207)(undefined4,undefined4);
typedef undefined4 (__stdcall *OriginalGetState207)(undefined4);
typedef int (__stdcall *OriginalAbout218)(void); // EAX address bits, not a semantic integer result
typedef undefined4 (__stdcall *OriginalSetTexture218)(undefined4); // return discarded here
extern OriginalSetState207 DAT_006bd97c;
extern OriginalGetState207 DAT_006bd984;
extern OriginalAbout218 DAT_006bd934;
extern OriginalSetTexture218 DAT_006bd954;
extern char DAT_005de630; // 537b59 byte snapshot
extern int DAT_005de64c; // 537b94 DWORD
extern int DAT_006a6450; // 537bbe/bef raw address32, no pointee layout claim
// Minimum consumer view, NOT an allocation/owner/semantic array-size claim:
// 537b73/7a/cc8 address base + (0 or255)*4, DWORD; span1024B.
extern uint DAT_006b4b20[256];
extern undefined1 *_DAT_005de784; // 537c72/c96 DWORD overlaps179 byte symbol
extern uint _DAT_005de78c; // 537ca0/ccf DWORD overlaps179 byte symbol
extern byte DAT_005de62d; // 537c7a BYTE, original179 base005de62c+1
extern undefined4 DAT_006bda08;
extern undefined1 LAB_00537ce0; // address-only code boundary, no implementation claim
extern undefined *PTR_LAB_005de770;
static __forceinline int signed_bits218(uint bits){
 int value;unsigned char*d=reinterpret_cast<unsigned char*>(&value);
 const unsigned char*s=reinterpret_cast<const unsigned char*>(&bits);
 d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];return value;
}
'''

FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(uint);
void FUN_00537b40(int,uint,uint);
char DAT_005de630=0;int DAT_005de64c=0,DAT_006a6450=0;
uint DAT_006b4b20[256]={};undefined1 *_DAT_005de784=0;uint _DAT_005de78c=0;
byte DAT_005de62d=0;uint DAT_006bda08=0;undefined1 LAB_00537ce0=0;
undefined *PTR_LAB_005de770=0;
uint failures=0,cases=0,count218=0,format218=4,expected_texture_format218=6;
uint payload218[2]={0,0},about218[13]={},caps218[7]={},texture218[4]={},output218[256]={};
uint old218=0x13579bdfu,p2_218=0x80000001u,p3_218=0xfedcba98u;
uint events218[16][3]={};
void event218(uint id,uint a=0,uint b=0){if(count218>=16){++failures;return;}events218[count218][0]=id;events218[count218][1]=a;events218[count218++][2]=b;}
undefined4 __stdcall get218(uint state){event218(1,state);return state==10?0xa0a0a0a0u:state==1?0xb1b1b1b1u:0xc2c2c2c2u;}
undefined4 __stdcall set218(uint state,uint value){event218(2,state,value);return 0;}
int __stdcall about_call218(){event218(3);return reinterpret_cast<int>(about218);}
undefined4 __stdcall texture_call218(uint value){event218(4,value);return 0;}
OriginalGetState207 DAT_006bd984=&get218;OriginalSetState207 DAT_006bd97c=&set218;
OriginalAbout218 DAT_006bd934=&about_call218;OriginalSetTexture218 DAT_006bd954=&texture_call218;
// Controlled boundary witnesses only. These do not implement game/provider callees.
undefined1 FUN_00537f90(uint*input){if(input!=payload218)++failures;return static_cast<undefined1>(format218);}
int *FUN_00572a90(uint w,uint h,uint format,uint zero){event218(5,w,h);if(format!=expected_texture_format218||zero!=0)++failures;return reinterpret_cast<int*>(texture218);}
uint FUN_00572b40(int texture,int input,int p2,int p3,int width,int height){
 event218(6,static_cast<uint>(p2),static_cast<uint>(p3));
 if(texture!=reinterpret_cast<int>(texture218)||input!=reinterpret_cast<int>(payload218)||width!=-32768||height!=32767)++failures;
 return 0;
}
int FUN_00572ee0(int*texture){event218(7);if(texture!=reinterpret_cast<int*>(texture218))++failures;return 0;}
uint *FUN_005349e0(uint input,uint*buffer){event218(8);if(input!=reinterpret_cast<uint>(payload218))++failures;
 // Exercise the proven stack-buffer end, not just the incorrectly printed1004B.
 buffer[0]=0x13572468u;buffer[255]=0x89abcdefu;return output218;
}
void FUN_00571630(int input,int p2,int p3,uint*dispatch){event218(9,static_cast<uint>(p2),static_cast<uint>(p3));
 if(input!=reinterpret_cast<int>(payload218)||dispatch!=reinterpret_cast<uint*>(&PTR_LAB_005de770))++failures;
 bool special=format218==8&&DAT_005de62d==16;
 if((_DAT_005de784!=0)!=special||_DAT_005de78c!=(special?123u:0u))++failures;
 if(special&&(_DAT_005de784!=&LAB_00537ce0||DAT_006bda08!=reinterpret_cast<uint>(output218)))++failures;
}
void expect218(uint n,uint id,uint a=0,uint b=0){if(n>=count218||events218[n][0]!=id||events218[n][1]!=a||events218[n][2]!=b)++failures;}
extern "C" void __cdecl entry(){
 payload218[1]=0x7fff8000u;about218[12]=reinterpret_cast<uint>(caps218);
 for(uint fmt=0;fmt<2;++fmt)for(uint existing=0;existing<2;++existing)for(uint cap=0;cap<2;++cap)for(uint flag=0;flag<2;++flag){
  format218=fmt?8u:4u;uint index=fmt?255u:0u;DAT_006b4b20[index]=old218;
  DAT_005de630=flag?signed_bits218(0xffffff80u):1;DAT_005de64c=0;
  DAT_006a6450=existing?reinterpret_cast<int>(texture218):0;caps218[6]=cap?0x80000001u:0xfffffffeu;
  expected_texture_format218=cap?6u:7u;count218=0;
  FUN_00537b40(reinterpret_cast<int>(payload218),p2_218,p3_218);
  uint n=0;expect218(n++,1,10);expect218(n++,1,1);expect218(n++,1,12);
  if(!existing){expect218(n++,3);expect218(n++,5,64,64);}
  expect218(n++,2,10,1);expect218(n++,2,12,old218);expect218(n++,6,p2_218,p3_218);expect218(n++,7);
  expect218(n++,2,12,0xc2c2c2c2u);expect218(n++,2,10,0xa0a0a0a0u);expect218(n++,4,0xb1b1b1b1u);
  if(n!=count218||DAT_006a6450!=0||DAT_006b4b20[index]!=0)++failures;++cases;
 }
 for(uint fmt=0;fmt<2;++fmt)for(uint gate=0;gate<3;++gate)for(uint mode=0;mode<2;++mode){
  format218=fmt?8u:4u;uint index=fmt?255u:0u;DAT_006b4b20[index]=old218;
  DAT_005de630=gate==0?0:gate==1?-1:1;DAT_005de64c=gate==2?1:0;DAT_005de62d=mode?16:0;
  _DAT_005de784=&LAB_00537ce0;_DAT_005de78c=0;count218=0;
  FUN_00537b40(reinterpret_cast<int>(payload218),p2_218,p3_218);
  uint n=0;if(fmt&&mode)expect218(n++,8);expect218(n++,9,p2_218,p3_218);
  if(n!=count218||DAT_006b4b20[index]!=old218||_DAT_005de78c!=0)++failures;++cases;
 }
 if(cases!=28)++failures;ExitProcess(failures?1:0);
}
'''


def main():
    resume='--resume-existing-compile' in sys.argv
    assert not (RUN/'summary.json').exists(),'completed218 immutable'
    if resume:
        assert (OUT/'compile.execution.json').exists() and (RUN/'proof-before-compile.json').exists()
    else:
        assert not OUT.exists(),'fresh218 required'
        OUT.mkdir()
    RUN.mkdir(parents=True,exist_ok=True)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();actual=digest(path)
        assert expected is None or actual==expected,('input SHA',path,actual)
        assert path not in pins or pins[path]==actual
        pins[path]=actual;return path
    def guard():
        for path,h in pins.items():assert digest(path)==h,('input mutation',path)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(path)
    if resume:pin(OUT/'captured-compile-driver.py')
    def materialize(path,text):
        if resume:assert Path(path).read_bytes()==text.encode('utf8'),('compiled source drift',path)
        else:Path(path).write_text(text,encoding='utf8',newline='\n')
    source=pin(ROOT/'local/experiments/v2-declaration-compat-184/full/00537b40.cpp','ed787305373b627f4fd7d20264fd4f0e63703d0cef9a02366d4579f0e35dffb1')
    oldheader=pin(source.with_name('00537b40-globals.h'))
    primitive=pin(ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    prior207=pin(RUNS/'207-pointer-call-consumers/summary.json')
    prior207proof=pin(RUNS/'207-pointer-call-consumers/proof-before-compile.json')
    assert load(prior207)['original_sha256']==abi.SHA
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm');by_pc={i['va']:i for i in ix[1]}
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    overlaps=[]
    for r in registry['functions']:
        if r['module']!='Porsche.exe':continue
        if r['entry_va']==VA or any(int(a,16)<=int(d,16) and int(c,16)<=int(b,16)
            for a,b in catalog.get(r['entry_va'],{}).get('ranges',[])for c,d in catalog[VA]['ranges']):overlaps.append(r)
    assert not overlaps,('canonical/interior owner',overlaps)
    wip=[]
    for path in (ROOT/'iterations/v2/001-original-recovery/source/recovered').rglob('*.cpp'):
        if re.search(r'(?i)(?:00537b40|0x537b40)',path.read_text(encoding='utf8')):wip.append(relative(path))
    assert not wip,('WIP ownership',wip)
    decl=next(r for r in abi.rows(pin(abi.DECL))if r['entry_va']==VA)
    binaries=list(abi.rows(pin(ROOT/'research/binary-index/static/binaries.jsonl')))
    evidence=[];original=[];callees={};providers=[];string_proof=[]
    for name in ['Porsche.exe','opengl1z.dll','opengl3z.dll','voodoo2z.dll']:
        binary=next(r for r in binaries if r['file']==name)
        raw=pin(ROOT/'local/game'/binary['path'],binary['sha256']).read_bytes()
        pe=struct.unpack_from('<I',raw,0x3c)[0]
        machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
        base=struct.unpack_from('<I',raw,pe+24+28)[0]
        sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:]for i in range(count)]
        def payload(va,length):
            rva=int(va,16)-base
            start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1])
            return raw[offset+rva-start:offset+rva-start+length]
        def exact(ins):
            for i in ins:assert payload(i['va'],len(i['bytes'])//2).hex()==i['bytes'],i
        if name=='Porsche.exe':
            original=abi.function_instructions(catalog[VA],ix);exact(original)
            for va in ['00537f90','00571630','005349e0','00572a90','00572b40','00572ee0']:
                ins=abi.function_instructions(catalog[va],ix);exact(ins);callees[va]=ins
            for start,end in [('00575033','00575052'),('00575214','0057522c'),('00594dd7','00594e0d')]:
                ins=[i for i in ix[1]if int(start,16)<=int(i['va'],16)<=int(end,16)];exact(ins)
                evidence.append(dict(window=[start,end],instructions=ins))
            for va,value in [('005c0dbc','_THRASH_about@0'),('005c0b7c','_THRASH_settexture@4')]:
                data=payload(va,len(value)+1);assert data==value.encode()+b'\0'
                string_proof.append(dict(va=va,value=value,bytes=data.hex()))
        else:
            corpus=ROOT/'research/v2/binaries'/(name+'-'+binary['sha256'][:12])
            cat=list(abi.rows(pin(corpus/'functions.jsonl')))
            parsed=[]
            for line in pin(corpus/'disassembly.asm').read_text().splitlines():
                m=re.match(r'^([0-9a-f]{8})\s+([0-9a-f]+)\s+(.*)',line)
                if m:parsed.append(dict(va=m[1],bytes=m[2],instruction=m[3]))
            for fn in cat:
                if fn['name'] not in ['_THRASH_about@0','_THRASH_settexture@4']:continue
                ins=[i for i in parsed if any(int(a,16)<=int(i['va'],16)<=int(b,16)for a,b in fn['ranges'])];exact(ins)
                rets=[i for i in ins if i['instruction'].startswith('RET')]
                assert len(rets)==1 and rets[0]['bytes']==('c3' if fn['name']=='_THRASH_about@0' else 'c20400')
                providers.append(dict(module=name,module_sha256=binary['sha256'],entry_va=fn['entry_va'],name=fn['name'],inferred_signature=fn['signature'],instructions=ins,rets=rets))
    assert len(providers)==6
    assert [i['bytes']for i in original if i['instruction'].startswith('RET')]==['c3','c3']
    assert by_pc['00537b81']['bytes']=='895c2410' and by_pc['00537bfe']['bytes']=='8b542410'
    assert by_pc['00537c13']['bytes']=='8b942420040000' and by_pc['00537c1b']['bytes']=='8b842420040000'
    header=OUT/'consumer218.h';materialize(header,HEADER)
    text=source.read_text(encoding='utf8');edits=[]
    oldinclude='#include "'+oldheader.as_posix()+'"';assert text.count(oldinclude)==1
    text=text.replace(oldinclude,'#include "'+header.as_posix()+'"')
    def change(old,new,pcs,reason):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new)
        edits.append(dict(original=old,replacement=new,pcs=pcs,reason=reason,instructions=[by_pc[p]for p in pcs]))
    change('void FUN_00571630(code *param_1,','void FUN_00571630(int param_1,',['00537cbf','00537cc0','00571635','0057164e'],'raw32 data-address argument, read as data in callee; no guessed function pointer cast; native symbol-contract mismatch explicit')
    change('undefined1 local_400 [1004];\n  undefined4 uStack_14;\n  undefined4 uStack_10;','alignas(4) undefined1 local_400 [1024];',['00537b40','00537c83'],'entryS minus0x414 after saves: oldDWORDatS-0x404, bufferS-0x400..S-1')
    change('FUN_00537f90(param_1)','FUN_00537f90(reinterpret_cast<uint *>(param_1))',['00537b4a','00537b51','00537f90','00537f94','00537f96','00537f9b'],'original data pointer bits; callee zeroesEAX then writesAL, full return zeroextended')
    change("bVar7 = DAT_005de630 != '\\0';","bVar7 = cVar1 != '\\0';",['00537b59','00537b71'],'one original CL byte snapshot')
    assert text.count('*(undefined4 *)(&DAT_006b4b20 + uVar6 * 4)')==3
    text=text.replace('*(undefined4 *)(&DAT_006b4b20 + uVar6 * 4)','DAT_006b4b20[uVar6]')
    edits.append(dict(reason='DWORD indexed accesses at537b73/7a/cc8; index0or255; raw minimum-span extern view, no allocation',pcs=['00537b73','00537b7a','00537cc8']))
    change('uVar9 = 10;','uVar9 = uVar3;',['00537b73','00537b81','00537bfe','00537c02'],'saved original tableDWORD survives getstate overwrites; not constant10')
    change('((byte)*(undefined4 *)(*(int *)(iVar2 + 0x30) + 0x18) & 3)','((byte)*(uint *)(*(uint *)(static_cast<uint>(iVar2) + 0x30u) + 0x18u) & 3)',['00537bcd','00537bd2','00537bd5'],'original two DWORD loads through EAX; unsigned address arithmetic preserves32bit bits')
    change('DAT_006a6450 = FUN_00572a90(0x40,0x40,uVar8,0);','DAT_006a6450 = reinterpret_cast<int>(FUN_00572a90(0x40,0x40,uVar8,0));',['00537be7','00537bef'],'pointer32 EAX stored unchanged in DWORD global')
    change('uStack_14,uStack_10','signed_bits218(param_2),signed_bits218(param_3)',['00537c13','00537c1a','00537c1b','00537c22','00537c29','00537c2a'],'entryS+8/+c: ESP+420 resolves to param3 then param2 afterPUSH; rawintbits preserved')
    change('(int)*(short *)(param_1 + 4)','(int)*reinterpret_cast<short *>(static_cast<uint>(param_1) + 4u)',['00537c0f'],'signedWORD load from rawaddress+4')
    change('(int)*(short *)(param_1 + 6)','(int)*reinterpret_cast<short *>(static_cast<uint>(param_1) + 6u)',['00537c0b'],'signedWORD load from rawaddress+6')
    change('FUN_00572ee0(DAT_006a6450);','FUN_00572ee0(reinterpret_cast<int *>(DAT_006a6450));',['00537c32','00537c38','00572ee1','00572eef'],'raw32 pointer passed and dereferenced by callee')
    change("DAT_005de62c._1_1_ == '\\x10'","DAT_005de62d == 0x10",['00537c7a'],'exact byte view at originalbase+1')
    change('DAT_006bda08 = FUN_005349e0(param_1,local_400);','DAT_006bda08 = reinterpret_cast<uint>(FUN_005349e0(static_cast<uint>(param_1),reinterpret_cast<uint *>(local_400)));',['00537c83','00537c87','00537c88','00537c89','00537c91'],'stackbuffer address32 and returned pointerEAX stored as rawDWORD')
    change('FUN_00571630(param_1,param_2,param_3,&PTR_LAB_005de770);','FUN_00571630(param_1,signed_bits218(param_2),signed_bits218(param_3),reinterpret_cast<uint *>(&PTR_LAB_005de770));',['00537caa','00537cb1','00537cb8','00537cbd','00537cbe','00537cbf','00537cc0'],'four caller-cleaned stackDWORD payloads, last is dispatch-data address')
    cpp=OUT/(VA+'.cpp');materialize(cpp,text)
    fixture=OUT/'call-boundary-fixture.cpp';materialize(fixture,'#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE)
    for path in [header,cpp,fixture]:pin(path)
    proof=dict(schema=1,original_sha256=abi.SHA,entry_va=VA,queries=['00537b40 CALL/RET, stackproducers, tableDWORD, globalWIDTH; 006bd934/954 loaderexports; 207 getstate/setstate'],
        ownership=dict(canonical_exact_or_interior=[],WIP=[]),inferred179=decl,original_instructions=original,direct_callees=callees,loader_windows=evidence,strings=string_proof,providers=providers,edits=edits,
        stack_map=dict(entry='S',after_frame_and_saved_regs='S-0x414',saved_old_table='S-0x404',buffer=['S-0x400','S-1'],incoming=['S+4','S+8','S+c']),
        callback_contracts=dict(getstate='207 raw32 stdcall4 EAX32; 537ba0/baa/bb6 push10/1/12',setstate='207 raw32,raw32 stdcall8 EAX32; state12 consumes savedtableDWORD',about='stdcall0 EAXaddress32; return points to data+30, nestedDWORD+18; voodoo PUSH ECX allocates discarded local, not semantic input',settexture='stdcall4 raw32; return unused'),
        data_views=[dict(va=v,bytes=n)for v,n in [('005de630',1),('005de64c',4),('006a6450',4),('006b4b20',1024),('005de784',4),('005de78c',4),('005de62d',1),('006bda08',4),('005de770',4)]],
        deferred=['FUN_00571630 native declaration int replaces erroneous code*: same proven original stack32 payload but native mangled-symbol binding required; no bridge supplied.',
          'Extern view/global overlaps require canonical data owners/aliases; no allocation supplied.',
          'Full callees/provider behavior, lifetime/concurrency, original volatile-register/fault and whole-game fidelity remain open.'])
    if resume:assert load(RUN/'proof-before-compile.json')==proof,'original precompile proof drift'
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects'
    if not resume:objects.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/MP6']
    command=[str(abi.COMPILER),*flags,'/Fo'+str(objects)+os.sep,str(cpp),str(fixture)]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        started=time.perf_counter();p=subprocess.run(list(map(str,command)),cwd=OUT,env=env,capture_output=True,timeout=120);elapsed=time.perf_counter()-started
        write(OUT/(name+'.execution.json'),dict(command=list(map(str,command)),exit_code=p.returncode,elapsed_seconds=elapsed))
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=OUT/(name+'.log');path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p,path,elapsed
    if resume:
        captured=load(OUT/'compile.execution.json');assert captured['command']==command and captured['exit_code']==0
        seconds=captured['elapsed_seconds'];log=OUT/'compile.log'
    else:
        p,log,seconds=run(command,'compile');assert p.returncode==0,log.read_text()
    warnings=re.findall(r'warning (C\d+).*',log.read_text())
    # Actual successful batch: original modulo32 unsignedNEG; controlledfixture char0x80.
    assert sorted(warnings)==['C4146','C4244'],warnings
    obj=objects/(VA+'.obj');symbols=coff.coff_symbols(obj)
    p,dis,_=run([abi.DUMPBIN,'/disasm',obj],'consumer-disassembly');assert p.returncode==0
    asm=dis.read_text()
    body=asm.split('?FUN_00537b40@@YAXHII@Z (',1)[1].split('\n? signed',1)[0]
    body=body.split('\n?signed_bits218@@',1)[0]
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',body,re.M)
    assert rets and all(not r.strip() for r in rets),rets
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    exe=OUT/'call-boundary-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'call-boundary-fixture.obj',kernel],'fixture-link');assert p.returncode==0,llog.read_text()
    p,nlog,nseconds=run([exe],'fixture-native');assert p.returncode==0,('fixturefailed',p.returncode)
    for path in [obj,objects/'call-boundary-fixture.obj',exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(path)
    guard()
    row=dict(va=VA,name='FUN_'+VA,compiled=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=1,
        diagnostics=[dict(severity='warning',code='C4146',classification='Original unsignedNEG modulo32 index0/255; intentional defined C++ behavior.')],
        generated_source=relative(cpp),generated_source_sha256=digest(cpp),dependency_sha256={relative(p):pins[p]for p in [cpp,header,primitive]},forced_headers=[],
        frozen184_source=relative(source),frozen184_source_sha256=digest(source),object=relative(obj),object_sha256=digest(obj),symbols=symbols,
        defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],native_ret_bytes=[0 for _ in rets],original_ret_bytes=[0,0],
        disassembly=relative(dis),disassembly_sha256=digest(dis))
    summary=dict(schema=1,kind='original-renderer-state-consumer',original_sha256=abi.SHA,objects_compiled=1,real_coff_objects=1,results=[row],actual_compiler_batches=1,
        changed_game_TUs=1,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=seconds,compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=command,
        compiler_log=relative(log),compiler_log_sha256=digest(log),input_sha256={relative(p):h for p,h in pins.items()},input_guards_before=True,input_guards_after=True,
        original_instruction_count=len(original),original_bytes=sum(len(i['bytes'])//2 for i in original),ownership_preflight=dict(canonical_exact_or_interior=0,WIP=0),
        compile_warnings=dict(game=['C4146 original modulo32 unsignedNEG'],fixture=['C4244 controlled char0x80 narrow; lowbyte fixture input']),
        captured_compile_driver=relative(OUT/'captured-compile-driver.py') if resume else relative(Path(__file__)),
        resumed_existing_successful_compile=resume,recompilations=0,
        Ghidra_decompilations=0,production_or_union_changes=False,fixture=dict(native_exit_code=0,cases=28,seconds=nseconds,executable=relative(exe),executable_sha256=digest(exe),
        scope='Actual corrected consumer; controlled call-boundary trace witnesses only, not provider/game implementations.16 fast12 fallback traces; both indices, savedtable !=10, rawhighbit arguments, signedWORD fields, bufferend, about6/7, flags and restore paths.',full_original_or_provider_fidelity_claimed=False),limits=proof['deferred'])
    write(RUN/'summary.json',summary)
    print(json.dumps(dict(objects_compiled=1,compile_seconds=seconds,original_instructions=len(original),native_rets=len(rets),fixture_cases=28)))


if __name__=='__main__':main()

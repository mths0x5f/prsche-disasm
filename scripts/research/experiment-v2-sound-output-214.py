"""Recover one original GetCurrentPosition output consumer and integer tail.

No Ghidra/provider/production/union changes; one changed game TU and fixture.
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
RUN=ROOT/'iterations/v2/001-original-recovery/runs/214-sound-output-consumer'
OUT=ROOT/'local/experiments/v2-sound-output-consumer-214'
VA='0058f5d0'
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


abi=module('abi214','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff214','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER='''#pragma once
// Exact214 original consumer RAM views; no definitions or shared-owner claim.
static_assert(sizeof(int)==4 && sizeof(uint)==4 && sizeof(void*)==4,"original32-bit ABI");
typedef int (__stdcall *GetCurrentPosition214)(int*,uint*,uint*);
static_assert(sizeof(GetCurrentPosition214)==4,"original indirect callable pointer32");
extern int DAT_006ad760; // original58f5d1 RAM4
extern int *DAT_006ad768; // original58f5de RAM4 object pointer
extern char DAT_006b48e4; // original58f5fc RAM1
extern uint _DAT_006b48dc; // original58f608 RAM4, despite179 formal byte
extern int DAT_006ad78c; // original58f618 RAM4
extern int DAT_006ad7b4; // original58f622 RAM4
extern ushort WORD_006b48da_214; // original58f62d RAM2 view at base006b48d8+2
static_assert(sizeof(_DAT_006b48dc)==4 && alignof(decltype(_DAT_006b48dc))==4,"originalDWORDload");
static_assert(sizeof(WORD_006b48da_214)==2 && alignof(decltype(WORD_006b48da_214))==2,"originalWORDload");
// Object representation, not a numeric unsigned-to-signed conversion.
static __forceinline int signed_bits214(uint bits){
 int value;unsigned char*d=reinterpret_cast<unsigned char*>(&value);
 const unsigned char*s=reinterpret_cast<const unsigned char*>(&bits);
 d[0]=s[0];d[1]=s[1];d[2]=s[2];d[3]=s[3];return value;
}
'''

FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(uint);
int FUN_0058f5d0(void);
int DAT_006ad760=1;int *DAT_006ad768=0;char DAT_006b48e4=0;
uint _DAT_006b48dc=1;int DAT_006ad78c=0,DAT_006ad7b4=0;ushort WORD_006b48da_214=1;
volatile uint failures=0,cases=0,callback_calls=0;uint configured_cursor=0;int configured_hresult=0;
int object214[1];
// Synthetic call-boundary witness only: not a DirectSound/game implementation.
int __stdcall controlled_position214(int*self,uint*play,uint*write){
 ++callback_calls;if(self!=object214 || play==0 || write!=0)++failures;
 if(configured_hresult==0)*play=configured_cursor;
 return configured_hresult;
}
GetCurrentPosition214 table214[5]={0,0,0,0,&controlled_position214};
// Original58f5f8..63e instruction sequence on the same raw input bits.
__declspec(noinline) int original_integer_tail214(uint cursor,uint mode,uint field32,uint start_bits,uint wrap_bits,ushort divisor_word){
 int result;__asm{
  mov eax,cursor
  shr eax,1
  cmp mode,0
  jne normalized214
  mov ecx,field32
  xor edx,edx
  and ecx,0xff
  div ecx
 normalized214:
  mov ecx,start_bits
  sub ecx,eax
  jns nonnegative214
  add ecx,wrap_bits
 nonnegative214:
  lea eax,[ecx+ecx*4]
  xor ecx,ecx
  mov cx,divisor_word
  lea eax,[eax+eax*4]
  lea eax,[eax+eax*4]
  shl eax,3
  cdq
  idiv ecx
  mov result,eax
 }return result;
}
extern "C" void __cdecl entry(){
 object214[0]=reinterpret_cast<int>(table214);DAT_006ad768=object214;
 const uint cursors[12]={0,1,2,3,1024,65535,0x7fffffffu,0x80000000u,0xffffffffu,0x00402000u,0x13579bdfu,0xfffffffeu};
 const uint starts[8]={0,1,1024,0x7fffffffu,0x80000000u,0xffffffffu,0x7ffff000u,0xfffff000u};
 const uint wraps[4]={0,1,0x7fffffffu,0xffffffffu};
 const uint fields[4]={1,0xa5a50002u,0xffffffffu,0x123400ffu};
 const ushort divisors[8]={1,2,3,255,256,11025,44100,65535};
 for(uint c=0;c<12;++c)for(uint m=0;m<3;++m)for(uint f=0;f<4;++f)
 for(uint s=0;s<8;++s)for(uint w=0;w<4;++w)for(uint d=0;d<8;++d){
  uint mode=m==2?0x80u:m;configured_cursor=cursors[c];DAT_006b48e4=static_cast<char>(mode);
  _DAT_006b48dc=fields[f];DAT_006ad78c=signed_bits214(starts[s]);DAT_006ad7b4=signed_bits214(wraps[w]);WORD_006b48da_214=divisors[d];
  uint before=callback_calls;int actual=FUN_0058f5d0();
  int expected=original_integer_tail214(cursors[c],mode,fields[f],starts[s],wraps[w],divisors[d]);
  if(actual!=expected || callback_calls!=before+1)++failures;++cases;
 }
 for(uint error=0;error<2;++error){configured_hresult=error?1:signed_bits214(0x80004005u);uint before=callback_calls;
  if(FUN_0058f5d0()!=0 || callback_calls!=before+1)++failures;++cases;}
 DAT_006ad760=0;uint before=callback_calls;if(FUN_0058f5d0()!=0 || callback_calls!=before)++failures;++cases;
 if(cases!=36867)++failures;ExitProcess(failures?1:0);
}
'''


def main():
    assert not OUT.exists() and not (RUN/'summary.json').exists(), 'fresh214 required'
    OUT.mkdir();RUN.mkdir(parents=True,exist_ok=True)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();actual=digest(path);assert expected is None or actual==expected,(path,expected,actual)
        pins[path]=actual;return path
    def guard():
        for path,expected in pins.items():assert digest(path)==expected,('input drift',path)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(path)
    source=pin(ROOT/'local/experiments/v2-declaration-compat-184/full/0058f5d0.cpp','0c1f5ac5e5aa406a3087dca64b8e873fd99c3b05ebd429fc407f00e55c41c26f')
    oldheader=pin(ROOT/'local/experiments/v2-declaration-compat-184/full/0058f5d0-globals.h')
    primitive=pin(ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    original=abi.function_instructions(catalog[VA],ix);by_pc={i['va']:i for i in ix[1]}
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    target_ranges=[(int(a,16),int(b,16))for a,b in catalog[VA]['ranges']]
    overlaps=[]
    for r in registry['functions']:
        if r['module']!='Porsche.exe':continue
        entry=r['entry_va'];ranges=catalog.get(entry,{}).get('ranges',[])
        if entry==VA or any(int(a,16)<=end and start<=int(b,16)for a,b in ranges for start,end in target_ranges):overlaps.append(r)
    assert not overlaps,('canonical/interior owner',overlaps)
    owners=[];recovered=ROOT/'iterations/v2/001-original-recovery/source/recovered'
    for path in recovered.rglob('*.cpp'):
        if re.search(r'(?i)(?:0058f5d0|0x58f5d0)',path.read_text(encoding='utf8')):owners.append(relative(path))
    assert not owners,('WIP/address owner',owners)
    decl=next(r for r in abi.rows(pin(abi.DECL))if r['entry_va']==VA)
    raw=pin(ROOT/'local/game/Porsche.exe',abi.SHA).read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:] for i in range(count)]
    def exact(ins):
        rva=int(ins['va'],16)-base;length=len(ins['bytes'])//2
        start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1])
        assert raw[offset+rva-start:offset+rva-start+length].hex()==ins['bytes'],ins
    origin=[i for i in ix[1]if int('0058f15c',16)<=int(i['va'],16)<=int('0058f174',16)]
    for ins in original+origin:exact(ins)
    expected={'0058f5e3':'8d542400','0058f5e7':'6a00','0058f5e9':'52','0058f5ec':'50','0058f5ed':'ff5110','0058f5f8':'8b442400',
              '0058f602':'d1e8','0058f608':'8b0ddc486b00','0058f610':'81e1ff000000','0058f616':'f7f1','0058f61e':'2bc8','0058f620':'7906',
              '0058f622':'030db4d76a00','0058f628':'8d0489','0058f62d':'668b0dda486b00','0058f634':'8d0480','0058f637':'8d0480',
              '0058f63a':'c1e003','0058f63d':'99','0058f63e':'f7f9','0058f166':'6868d76a00','0058f16f':'ff510c'}
    for pc,code in expected.items():assert by_pc[pc]['bytes']==code,(pc,code)
    sdk=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0')
    dsound=pin(sdk/'um/dsound.h');basetyps=pin(sdk/'shared/basetyps.h')
    sdktext=dsound.read_text(encoding='utf-8-sig');interface=sdktext.split('DECLARE_INTERFACE_(IDirectSoundBuffer, IUnknown)',1)[1].split('};',1)[0]
    assert interface.index('GetCaps')<interface.index('GetCurrentPosition')<interface.index('GetFormat')
    assert 'STDMETHOD(GetCurrentPosition)   (THIS_ _Out_opt_ LPDWORD pdwCurrentPlayCursor, _Out_opt_ LPDWORD pdwCurrentWriteCursor) PURE;' in interface
    assert 'STDMETHOD(CreateSoundBuffer)' in sdktext and '#define STDMETHODCALLTYPE       __stdcall' in basetyps.read_text()
    header=OUT/'consumer214.h';header.write_text(HEADER,encoding='utf8',newline='\n')
    before=source.read_text(encoding='utf8');text=before
    edits=[]
    def change(old,new,pcs,reason):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new)
        edits.append(dict(original=old,replacement=new,pcs=pcs,reason=reason,instructions=[by_pc[pc]for pc in pcs]))
    oldinclude='#include "'+oldheader.as_posix()+'"';assert text.count(oldinclude)==1
    text=text.replace(oldinclude,'#include "'+header.as_posix()+'"')
    change('undefined1 local_4 [4];','uint local_4;',['0058f5d0','0058f5e3','0058f5f8'],'original4-byte stack output cell; no extra initialization')
    change('iVar1 = (**(code **)(*DAT_006ad768 + 0x10))(DAT_006ad768,local_4,0);',
           'iVar1 = (**(GetCurrentPosition214 *)(*piVar3 + 0x10))(piVar3,&local_4,0);',
           ['0058f5de','0058f5e3','0058f5e7','0058f5e9','0058f5ea','0058f5ec','0058f5ed'],'one object snapshot; SDKstdcall self/DWORD*/nullwrite; callee cleanup12')
    change('uVar2 = (uint)piVar3 >> 1;','uVar2 = local_4 >> 1;',['0058f5f8','0058f602'],'read actual DWORD output then logicalSHR; never object-address arithmetic')
    oldtail='''  iVar1 = DAT_006ad78c - uVar2;
  if (iVar1 < 0) {
    iVar1 = iVar1 + DAT_006ad7b4;
  }
  return (iVar1 * 1000) / (int)(uint)DAT_006b48d8._2_2_;'''
    newtail='''  uint distance_bits = static_cast<uint>(DAT_006ad78c) - uVar2;
  if ((distance_bits & 0x80000000u) != 0) {
    distance_bits = distance_bits + static_cast<uint>(DAT_006ad7b4);
  }
  uint scaled_bits = distance_bits * 1000u;
  return signed_bits214(scaled_bits) / static_cast<int>(WORD_006b48da_214);'''
    change(oldtail,newtail,['0058f618','0058f61e','0058f620','0058f622','0058f628','0058f62b','0058f62d','0058f634','0058f637','0058f63a','0058f63d','0058f63e'],
           'modulo32 SUB/optionalADD/*5*5*5*8; JNS observes signbit; bitview numerator and zeroextendedWORD denominator use signedIDIV')
    cpp=OUT/'0058f5d0.cpp';cpp.write_text(text,encoding='utf8',newline='\n')
    fixture=OUT/'call-boundary-fixture.cpp';fixture.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE,encoding='utf8',newline='\n')
    for path in (header,cpp,fixture):pin(path)
    proof=dict(schema=1,original_sha256=abi.SHA,entry_va=VA,original_instructions=original,DSBuffer_origin_window=origin,
               scope='one original integer-only consumer; no provider implementation',ownership=dict(canonical_exact_or_interior=[],WIP=[]),
               source_frozen184_sha256=digest(source),inferred179=decl,edits=edits,
               SDK=dict(dsound_path=relative(dsound),dsound_sha256=digest(dsound),basetyps_path=relative(basetyps),basetyps_sha256=digest(basetyps),
                        contract='HRESULT32 __stdcall GetCurrentPosition(self,DWORD*play,DWORD*write),vtable+16,callee cleanup12'),
               original_memory_views=[dict(va='006ad760',bytes=4),dict(va='006ad768',bytes=4),dict(va='006b48e4',bytes=1),dict(va='006b48dc',bytes=4),
                                      dict(va='006ad78c',bytes=4),dict(va='006ad7b4',bytes=4),dict(va='006b48da',bytes=2)],
               confirmed='OutputDWORD dataflow, memory widths, unsignedDIV/signbit/modulo32 operations and signedIDIV; no format-field meaning assumed',
               deferred='Provider success/output initialization, object lifetime/concurrency/volatile registers and divide-by-zero fault fidelity')
    write(RUN/'proof-before-compile.json',proof);pin(RUN/'proof-before-compile.json');guard()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/MP6']
    objects=OUT/'objects';objects.mkdir()
    command=[str(abi.COMPILER),*flags,'/Fo'+str(objects)+os.sep,str(cpp),str(fixture)]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        started=time.perf_counter();p=subprocess.run(list(map(str,command)),cwd=OUT,env=env,capture_output=True,timeout=120);elapsed=time.perf_counter()-started
        write(OUT/(name+'.execution.json'),dict(command=list(map(str,command)),exit_code=p.returncode,elapsed_seconds=elapsed))
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=OUT/(name+'.log');path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p,path,elapsed
    p,log,compile_seconds=run(command,'compile');assert p.returncode==0,log.read_text()
    assert not re.search(r'\b(?:error|warning) C\d+',log.read_text()),log.read_text()
    obj=objects/'0058f5d0.obj';symbols=coff.coff_symbols(obj)
    dis,dispath,_=run([abi.DUMPBIN,'/disasm',obj],'consumer-disassembly');assert dis.returncode==0
    asm=dispath.read_text();assert re.search(r'\bdiv\s',asm) and re.search(r'\bidiv\s',asm)
    assert 'WORD_006b48da_214' in asm and '_DAT_006b48dc' in asm
    assert re.search(r'mov\s+\w+,dword ptr \[\?_DAT_006b48dc',asm)
    assert re.search(r'movzx\s+\w+,word ptr \[\?WORD_006b48da_214',asm)
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    exe=OUT/'call-boundary-fixture.exe'
    lp,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'call-boundary-fixture.obj',kernel],'fixture-link');assert lp.returncode==0,llog.read_text()
    native,nlog,native_seconds=run([exe],'fixture-native');assert native.returncode==0,('native integer/callback fixture failed',native.returncode)
    fp,fdis,_=run([abi.DUMPBIN,'/disasm',objects/'call-boundary-fixture.obj'],'fixture-disassembly');assert fp.returncode==0
    assert re.search(r'\bret\s+0?Ch',fdis.read_text())
    for path in [obj,objects/'call-boundary-fixture.obj',exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(path)
    guard()
    include_closure={cpp.resolve(),header.resolve(),primitive.resolve()}
    row=dict(va=VA,name='FUN_'+VA,compiled=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
             generated_source=relative(cpp),generated_source_sha256=digest(cpp),dependency_sha256={relative(path):pins[path]for path in sorted(include_closure)},forced_headers=[],
             frozen184_source=relative(source),frozen184_source_sha256=digest(source),object=relative(obj),object_sha256=digest(obj),symbols=symbols,
             defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],native_ret_bytes=[0,0,0],
             disassembly=relative(dispath),disassembly_sha256=digest(dispath))
    report=dict(schema=1,kind='original-sound-output-consumer',original_sha256=abi.SHA,objects_compiled=1,real_coff_objects=1,results=[row],
                actual_compiler_batches=1,changed_game_TUs=1,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=compile_seconds,
                compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=command,compiler_log=relative(log),compiler_log_sha256=digest(log),
                input_sha256={relative(path):h for path,h in pins.items()},input_guards_before=True,input_guards_after=True,
                original_instruction_count=len(original),origin_window_instruction_count=len(origin),ownership_preflight=dict(canonical_exact_or_interior=0,WIP=0),
                fixture=dict(native_exit_code=0,integer_reference_cases=36864,error_or_null_guard_cases=3,seconds=native_seconds,
                             reference='Original integer tail executed as inline assembly; actual corrected consumer called through controlled stdcall output callback',
                             callback_cleanup_bytes=12,callback_writes_DWORD_output=True,provider_fidelity_claimed=False,
                             executable=relative(exe),executable_sha256=digest(exe)),
                Ghidra_decompilations=0,production_or_union_changes=False,
                limits=['Integer-only original algorithm/ABI/output-cell recovery; no semantic meaning assigned to raw format fields.',
                        'Fixture controls only the call boundary; not a fake DirectSound implementation or game/provider acceptance.',
                        'Nonzero divisors only; provider behavior/lifetime/concurrency, outgoingvolatile registers and fault behavior remain open.'])
    write(RUN/'summary.json',report)
    print(json.dumps({k:report[k]for k in ('objects_compiled','compiler_batch_exit_code','compile_seconds','original_instruction_count','fixture')}))


if __name__=='__main__':main()

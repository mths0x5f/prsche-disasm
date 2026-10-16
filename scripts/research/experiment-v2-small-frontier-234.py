"""Four original small wrappers; preserve four lost-ECX native-contract queues."""
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
RUN=RUNS/'234-small-frontier-bodies'
OUT=ROOT/'local/experiments/v2-small-frontier-bodies-234'
SELECTED=['00468100','004d8230','004d8240','0058e2f0','0058e300','0050cbf0','00538d80','0050d310']
COMPILED=['0058e2f0','0058e300','0050cbf0','0050d310']
DEFERRED=[va for va in SELECTED if va not in COMPILED]
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


abi=module('abi234','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff234','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER='''#pragma once
static_assert(sizeof(void*)==4 && sizeof(int)==4 && sizeof(uint)==4,"original32-bit ABI");
// Opaque minimum span from x86 SDK RTL_CRITICAL_SECTION, not a game allocation.
extern byte DAT_006b1800[24];
extern int DAT_0065b928; // original DWORD receiver-address bits
extern char s_options_005cc804[8];
extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(void*);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(void*);
// Calling-convention carrier ONLY. No fields/object layout/source-class claim;
// no instance is allocated in candidate code. Original ECX and stack slots proved.
struct OriginalECX234 {
 void __thiscall FUN_004d23f0(undefined4);
 void __thiscall FUN_004d2100(void*,undefined4,undefined4);
};
'''
BODIES={
    '0058e2f0':'void __cdecl FUN_0058e2f0(void){EnterCriticalSection(DAT_006b1800);}\n',
    '0058e300':'void __cdecl FUN_0058e300(void){LeaveCriticalSection(DAT_006b1800);}\n',
    '0050cbf0':'void __cdecl FUN_0050cbf0(void){reinterpret_cast<OriginalECX234 *>(DAT_0065b928)->FUN_004d23f0(0u);}\n',
    '0050d310':'void __cdecl FUN_0050d310(void){reinterpret_cast<OriginalECX234 *>(DAT_0065b928)->FUN_004d2100(s_options_005cc804,0u,1u);}\n',
}
FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(uint);
extern "C" __declspec(dllimport) void __stdcall InitializeCriticalSection(void*);
extern "C" __declspec(dllimport) void __stdcall DeleteCriticalSection(void*);
extern "C" void *__cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
void FUN_0058e2f0(void);void FUN_0058e300(void);void FUN_0050cbf0(void);void FUN_0050d310(void);
alignas(4) byte DAT_006b1800[24]={};int DAT_0065b928=0;char s_options_005cc804[8]="options";
typedef void (__stdcall *CriticalCall234)(void*);
CriticalCall234 enter_slot234=0,leave_slot234=0;
OriginalECX234 objects234[8];uint failures234=0,critical_pairs234=0,method_calls234=0;
uint observed_receiver234=0,observed_arg234=0,observed_name234=0,observed_zero234=0,observed_one234=0;
// Controlled method boundaries, not implementations of the two game callees.
void OriginalECX234::FUN_004d23f0(uint arg){++method_calls234;observed_receiver234=reinterpret_cast<uint>(this);observed_arg234=arg;}
void OriginalECX234::FUN_004d2100(void*name,uint zero,uint one){++method_calls234;observed_receiver234=reinterpret_cast<uint>(this);observed_name234=reinterpret_cast<uint>(name);observed_zero234=zero;observed_one234=one;}
// Original12B wrappers, synthetic IAT slots point to the actual native SDK provider.
__declspec(naked) void original_enter234(){__asm{
 push offset DAT_006b1800
 call dword ptr[enter_slot234]
 ret
}}
__declspec(naked) void original_leave234(){__asm{
 push offset DAT_006b1800
 call dword ptr[leave_slot234]
 ret
}}
uint recursion234(){uint value;memcpy(&value,DAT_006b1800+8,4);return value;}
extern "C" void __cdecl entry(){
 enter_slot234=&EnterCriticalSection;leave_slot234=&LeaveCriticalSection;
 InitializeCriticalSection(DAT_006b1800);
 for(uint round=0;round<128;++round){
  for(uint depth=0;depth<8;++depth){uint before=recursion234();FUN_0058e2f0();uint middle=recursion234();original_enter234();uint after=recursion234();
   if(middle-before!=1u||after-middle!=1u)++failures234;++critical_pairs234;}
  for(uint depth=0;depth<8;++depth){uint before=recursion234();FUN_0058e300();uint middle=recursion234();original_leave234();uint after=recursion234();
   if(before-middle!=1u||middle-after!=1u)++failures234;++critical_pairs234;}
  if(recursion234()!=0)++failures234;
  for(uint object=0;object<8;++object){uint receiver=reinterpret_cast<uint>(objects234+object);DAT_0065b928=reinterpret_cast<int>(objects234+object);
   uint calls=method_calls234;observed_arg234=0xffffffffu;FUN_0050cbf0();
   if(method_calls234!=calls+1||observed_receiver234!=receiver||observed_arg234!=0)++failures234;
   calls=method_calls234;observed_name234=observed_zero234=observed_one234=0xffffffffu;FUN_0050d310();
   if(method_calls234!=calls+1||observed_receiver234!=receiver||observed_name234!=reinterpret_cast<uint>(s_options_005cc804)||observed_zero234!=0||observed_one234!=1)++failures234;
  }
 }
 DeleteCriticalSection(DAT_006b1800);
 if(critical_pairs234!=2048u||method_calls234!=2048u)++failures234;
 ExitProcess(failures234?1:0);
}
'''


def main():
    assert not OUT.exists() and not (RUN/'summary.json').exists(),'fresh234 required'
    OUT.mkdir();RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input SHA',path)
        assert path not in pins or pins[path]==h;pins[path]=h;return path
    def guard():
        for path,h in pins.items():assert digest(path)==h,('input mutation',path)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(path)
    current=load(pin(RUNS/'233-initialized-and-nested-union/summary.json'))
    assert not any(r['va']in SELECTED for r in current['results'])
    frozen={va:pin(ROOT/'local/experiments/v2-pcode-compat-180/prototypes-cpp-0000'/(va+'.cpp'))for va in SELECTED}
    primitive=pin(ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    for r in abi.rows(pin(ROOT/'research/binary-index/manual-functions.jsonl')):
        if r['module']=='Porsche.exe':catalog[r['entry_va']]=r
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'));ownership={}
    for va in SELECTED:
        overlaps=[];wip=[]
        for r in registry['functions']:
            if r['module']!='Porsche.exe':continue
            assert r['entry_va']in catalog
            if r['entry_va']==va or any(int(a,16)<=int(d,16)and int(c,16)<=int(b,16)for a,b in catalog[r['entry_va']]['ranges']for c,d in catalog[va]['ranges']):overlaps.append(r)
        for path in (ROOT/'iterations/v2/001-original-recovery/source/recovered').rglob('*.cpp'):
            if re.search(r'\b\w*'+va+r'\s*\([^;{}]*\)\s*\{',path.read_text(encoding='utf8')):wip.append(relative(path))
        assert not overlaps and not wip,('ownership',va,overlaps,wip)
        ownership[va]=dict(canonical_exact_or_interior=overlaps,WIP=wip,already_compiled=False)
    decl={r['entry_va']:r for r in abi.rows(pin(abi.DECL))if r['entry_va']in SELECTED}
    imports=[r for r in abi.rows(pin(ROOT/'research/binary-index/static/imports.jsonl'))if r['path']=='Porsche.exe'and r['symbol']in ['EnterCriticalSection','LeaveCriticalSection','InitializeCriticalSection','DeleteCriticalSection']]
    assert {r['symbol']:r['iat_rva']for r in imports}==dict(EnterCriticalSection='0x1b2078',LeaveCriticalSection='0x1b206c',InitializeCriticalSection='0x1b207c',DeleteCriticalSection='0x1b2068')
    sdk=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0')
    winnt=pin(sdk/'um/winnt.h');synch=pin(sdk/'um/synchapi.h');minwindef=pin(sdk/'shared/minwindef.h');basetsd=pin(sdk/'shared/basetsd.h')
    layout=winnt.read_text(encoding='utf8').split('typedef struct _RTL_CRITICAL_SECTION {',1)[1].split('} RTL_CRITICAL_SECTION',1)[0]
    assert all(s in layout for s in ['PRTL_CRITICAL_SECTION_DEBUG DebugInfo;','LONG LockCount;','LONG RecursionCount;','HANDLE OwningThread;','HANDLE LockSemaphore;','ULONG_PTR SpinCount;'])
    assert '#define WINAPI      __stdcall'in minwindef.read_text(encoding='utf8')
    api_text=synch.read_text(encoding='utf8')
    assert re.search(r'VOID\s+WINAPI\s+EnterCriticalSection\(\s+_Inout_ LPCRITICAL_SECTION lpCriticalSection',api_text)
    assert re.search(r'VOID\s+WINAPI\s+LeaveCriticalSection\(\s+_Inout_ LPCRITICAL_SECTION lpCriticalSection',api_text)
    raw=pin(ROOT/'local/game/Porsche.exe',abi.SHA).read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0];sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(count)]
    def payload(va,length):
        rva=int(va,16)-base;start,size,offset=next(s for s in sections if s[0]<=rva and rva+length<=s[0]+s[1]);return raw[offset+rva-start:offset+rva-start+length]
    instructions={}
    for va in SELECTED+['004d23f0','004d2100','0058e2d0','0058e2e0','00536050','004c7e10','004c7df0','00539eb0']:
        ins=abi.function_instructions(catalog[va],ix)
        for i in ins:assert payload(i['va'],len(i['bytes'])//2).hex()==i['bytes'],i
        instructions[va]=ins
    assert payload('005cc804',8)==b'options\0'
    pc={i['va']:i for ins in instructions.values()for i in ins}
    for address,bits in {'0050cbf0':'8b0d28b96500','0050cbf6':'6a00','0050d310':'8b0d28b96500','0050d316':'6a01','0050d318':'6a00','0050d31a':'6804c85c00','004d23fb':'8bd9','004d210e':'8be9'}.items():assert pc[address]['bytes']==bits
    assert [i['bytes']for i in instructions['004d23f0']if i['instruction'].startswith('RET')]==['c20400']
    assert [i['bytes']for i in instructions['004d2100']if i['instruction'].startswith('RET')]==['c20c00']
    queue=[]
    for va in DEFERRED:
        queue.append(dict(va=va,original_instructions=instructions[va],frozen_source=relative(frozen[va]),frozen_source_sha256=digest(frozen[va]),
            actual_contract='IncomingECX data pointer; original receiver is consumed before any definition.',
            mismatched_frontier_symbol='?FUN_'+va+'@@YAXXZ',reason='Frozen getC void(void) has lost receiver; preserving that name would hide wrongABI.',
            next_step='Recover original caller ECX producer/storage and bound native entry carrier+caller contracts together. Tail wrappers additionally preserve complete target RET chain; no alias supplied.'))
    write(RUN/'lost-receiver-queue.json',queue);pin(RUN/'lost-receiver-queue.json')
    header=OUT/'consumer234.h';header.write_text(HEADER,encoding='utf8',newline='\n');pin(header)
    sources={}
    for va in COMPILED:
        path=OUT/(va+'.cpp');path.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n// Original'+va+'; unchanged wrapper noincomingregister/noargument boundary.\n'+BODIES[va],encoding='utf8',newline='\n');pin(path);sources[va]=path
    fixture=OUT/'call-boundary-fixture.cpp';fixture.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE,encoding='utf8',newline='\n');pin(fixture)
    proof=dict(schema=1,original_sha256=abi.SHA,selected=SELECTED,compiled_scope=COMPILED,deferred=DEFERRED,ownership=ownership,inferred179=decl,original_instructions=instructions,
        frozen_sources={va:dict(path=relative(path),sha256=digest(path))for va,path in frozen.items()},imports=imports,
        options_string=dict(va='005cc804',bytes='6f7074696f6e7300'),
        SDK=dict(paths={relative(p):digest(p)for p in [winnt,synch,minwindef,basetsd]},critical_section_x86_size=24,alignment=4,recursion_count_offset=8,layout_fields=layout,
            API='VOID WINAPI Enter/LeaveCriticalSection(LPCRITICAL_SECTION), one pointer32, stdcall4; original init/delete producers use sameRAM address.'),
        contracts=dict(api_wrappers='void cdecl(void), constant RAM6b1800 to actual imported SDK provider; originalCALLindirect IAT stdcall4, wrapperRET0.',
            global_receiver_wrappers='void cdecl(void), ECX=DWORD[65b928], push0 / push1,push0,pushoptions; native opaque thiscall carrier preserves ECX+stack4/12 with targetRET4/12.',
            opaque_carrier='No fields/layout/sourceclass/instance allocation claim; newdistinctcallee symbols are explicit missing implementations, not aliases.'),
        limits=['Four lostreceiver wrappers deferred; their native void(void) frontier contracts are not accepted.',
            '004d23f0/004d2100 native implementations and their new explicit thiscall symbols remain missing.',
            'DAT6b1800 raw24B minimum span/65b928 and options canonical owners/initializers remain open; no allocation in game object.',
            'Fixtures prove SDK call effects and controlled method boundaries only; full callees/providers/concurrency/fault/register/game fidelity deferred.'])
    write(RUN/'proof-before-compile.json',proof);pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir();flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/MP6']
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        command=list(map(str,command));started=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);seconds=time.perf_counter()-started
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=OUT/(name+'.log');path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p,path,seconds
    command=[abi.COMPILER,*flags,'/Fo'+str(objects)+os.sep,*sources.values(),fixture]
    p,log,seconds=run(command,'compile');assert p.returncode==0,log.read_text();assert not re.search(r'(?:warning|error) C\d+',log.read_text()),log.read_text()
    results=[]
    for va,cpp in sources.items():
        obj=objects/(va+'.obj');symbols=coff.coff_symbols(obj);assert symbols['defined']==['?FUN_'+va+'@@YAXXZ']
        p,dis,_=run([abi.DUMPBIN,'/disasm',obj],va+'-disassembly');assert p.returncode==0
        body=dis.read_text().split('?FUN_'+va+'@@YAXXZ (',1)[1].split('\n?',1)[0]
        rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',body,re.M);assert rets and all(not r for r in rets)
        results.append(dict(va=va,name='FUN_'+va,compiled=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
            generated_source=relative(cpp),generated_source_sha256=digest(cpp),dependency_sha256={relative(p):pins[p]for p in [cpp,header,primitive]},forced_headers=[],object=relative(obj),object_sha256=digest(obj),symbols=symbols,
            defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],native_ret_bytes=[0 for _ in rets],original_ret_bytes=[0],disassembly=relative(dis),disassembly_sha256=digest(dis)))
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'));exe=OUT/'call-boundary-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),*[objects/(va+'.obj')for va in COMPILED],objects/'call-boundary-fixture.obj',kernel],'fixture-link');assert p.returncode==0,llog.read_text()
    p,nlog,nseconds=run([exe],'fixture-native');assert p.returncode==0,('fixture failed',p.returncode)
    p,fdis,_=run([abi.DUMPBIN,'/disasm',objects/'call-boundary-fixture.obj'],'fixture-disassembly');assert p.returncode==0
    for path in [*[objects/(va+'.obj')for va in COMPILED],objects/'call-boundary-fixture.obj',exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(path)
    guard()
    summary=dict(schema=1,kind='original-small-frontier-bodies',original_sha256=abi.SHA,selected_scope_vas=SELECTED,compiled_vas=COMPILED,uncompiled_vas=DEFERRED,objects_compiled=4,real_coff_objects=4,results=results,
        actual_compiler_batches=1,changed_game_TUs=4,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=seconds,compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),
        compiler_log=relative(log),compiler_log_sha256=digest(log),input_sha256={relative(path):h for path,h in pins.items()},input_guards_before=True,input_guards_after=True,ownership_preflight=ownership,
        original_instruction_count=sum(len(instructions[va])for va in COMPILED),original_bytes=sum(len(i['bytes'])//2 for va in COMPILED for i in instructions[va]),Ghidra_decompilations=0,production_or_union_changes=False,
        fixture=dict(native_exit_code=0,critical_section_original_native_pairs=2048,controlled_thiscall_boundary_calls=2048,seconds=nseconds,executable=relative(exe),executable_sha256=digest(exe),
            scope='Actual4bodies: recursion effect deltas match original12B wrappers through native SDK provider; methodseams capture ECX and rawstack0/options,0,1; no gamecallee replacement.',full_game_fidelity_claimed=False),
        new_explicit_thiscall_dependencies=[s for r in results for s in r['undefined_external_symbols']if 'OriginalECX234'in s],uncompiled_proof_queue=relative(RUN/'lost-receiver-queue.json'),limits=proof['limits'])
    write(RUN/'summary.json',summary);print(json.dumps(dict(compiled=COMPILED,deferred=DEFERRED,compile_seconds=seconds,fixture_seconds=nseconds)))


if __name__=='__main__':main()

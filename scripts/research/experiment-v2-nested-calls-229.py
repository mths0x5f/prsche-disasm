"""Bounded590070 recovery; preserve exact5907b0 unresolved callback/stack proof."""
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
RUN=RUNS/'229-nested-call-recovery'
OUT=ROOT/'local/experiments/v2-nested-call-recovery-229'
VA='00590070'
SELECTED=[VA,'005907b0']
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


abi=module('abi229','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff229','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER='''#pragma once
static_assert(sizeof(int)==4 && sizeof(uint)==4 && sizeof(void*)==4,"original32-bit ABI");
extern uint DAT_006b48d8; // original590078 DWORD, followed by low16 mask
extern int DAT_006b4a04; // original59008b DWORD raw table address
extern "C" void *__cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
static __forceinline uint load32_229(const void*p){uint v;memcpy(&v,p,4);return v;}
static __forceinline int signed_bits229(uint v){int s;memcpy(&s,&v,4);return s;}
'''
BODY='''// Original590070..5900a9, uint cdecl(int), no CALL, two RET0 paths.
uint __cdecl FUN_00590070(int param_1)
{
  if (param_1 >= 0 && param_1 < static_cast<int>(DAT_006b48d8 & 0xffffu)) {
    uint entry_bits = static_cast<uint>(DAT_006b4a04) + static_cast<uint>(param_1)*12u;
    if (load32_229(reinterpret_cast<const void *>(entry_bits)) != 0) {
      byte status_bits = *reinterpret_cast<const byte *>(entry_bits + 8u);
      // NEG AL sets CF iff the raw BYTE is nonzero; SBB EAX,EAX then AND AL,ee.
      return status_bits == 0 ? 0u : 0xffffffeeu;
    }
  }
  return 0xfffffff8u;
}
'''
FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(uint);
uint __cdecl FUN_00590070(int);
uint DAT_006b48d8=0;int DAT_006b4a04=0;
alignas(4) byte table229[65536*12+4]={};uint cases229=0,failures229=0;
// Original58B; only the two absolute global operands relocate.
__declspec(naked) uint __cdecl original229(int){__asm{
 mov eax,dword ptr[esp+4]
 test eax,eax
 jl rejected229
 mov ecx,DAT_006b48d8
 and ecx,0xffff
 cmp eax,ecx
 jge rejected229
 lea edx,[eax+eax*2]
 mov eax,DAT_006b4a04
 mov ecx,dword ptr[eax+edx*4]
 lea eax,[eax+edx*4]
 test ecx,ecx
 jz rejected229
 mov al,byte ptr[eax+8]
 neg al
 sbb eax,eax
 and al,0xee
 ret
rejected229:
 mov eax,0xfffffff8
 ret
}}
extern "C" void __cdecl entry(){
 const uint indexes[10]={0xffffffffu,0,1,2,255,32767,65534,65535,0x7fffffffu,0x80000000u};
 const uint counts[6]={0,1,2,256,32768,65535};
 const uint highwords[3]={0,0x12340000u,0xffff0000u};
 for(uint ix=0;ix<10;++ix)for(uint co=0;co<6;++co)for(uint hi=0;hi<3;++hi)
 for(uint present=0;present<2;++present)for(uint status=0;status<256;++status)for(uint align=0;align<4;++align){
  byte*base=table229+align;DAT_006b4a04=reinterpret_cast<int>(base);DAT_006b48d8=highwords[hi]|counts[co];
  if(indexes[ix]<65535u){byte*cell=base+indexes[ix]*12u;uint pointer_bits=present?0x87654321u:0;
   memcpy(cell,&pointer_bits,4);cell[8]=static_cast<byte>(status);cell[9]=0x5a;cell[10]=0xa5;cell[11]=0xff;}
  int index=signed_bits229(indexes[ix]);uint actual=FUN_00590070(index),expected=original229(index);
  if(actual!=expected)++failures229;++cases229;
 }
 if(cases229!=368640u)++failures229;ExitProcess(failures229?1:0);
}
'''


def main():
    assert not OUT.exists() and not (RUN/'summary.json').exists(),'fresh229 required'
    OUT.mkdir();RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input SHA',path)
        assert path not in pins or pins[path]==h;pins[path]=h;return path
    def guard():
        for path,h in pins.items():assert digest(path)==h,('input mutation',path)
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(path)
    pin(RUNS/'223-direct-callee-recovery/summary.json');pin(RUNS/'223-direct-callee-recovery/validation.json')
    current=load(pin(RUNS/'228-writable-and-callee-union/summary.json'))
    assert not any(r['va']in SELECTED for r in current['results'])
    oldsources={va:pin(ROOT/'local/experiments/v2-pcode-compat-180/prototypes-cpp-0000'/(va+'.cpp'))for va in SELECTED}
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
    raw=pin(ROOT/'local/game/Porsche.exe',abi.SHA).read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(count)]
    def exact(ins):
        for i in ins:
            rva=int(i['va'],16)-base;n=len(i['bytes'])//2;start,size,offset=next(s for s in sections if s[0]<=rva and rva+n<=s[0]+s[1])
            assert raw[offset+rva-start:offset+rva-start+n].hex()==i['bytes'],i
    instructions={}
    for va in SELECTED+['00565ea0','00599100']:
        ins=abi.function_instructions(catalog[va],ix);exact(ins);instructions[va]=ins
    by_pc={i['va']:i for ins in instructions.values()for i in ins}
    small=instructions[VA];large=instructions['005907b0']
    assert len(small)==20 and sum(len(i['bytes'])//2 for i in small)==58
    assert [i['bytes']for i in small if i['instruction'].startswith('RET')]==['c3','c3']
    assert not any(i['instruction'].startswith('CALL')for i in small)
    windows=[]
    for start,end in [('005657d1','005657ea'),('00566f27','00566f42')]:
        ins=[i for i in ix[1]if int(start,16)<=int(i['va'],16)<=int(end,16)];exact(ins);windows.append(dict(window=[start,end],instructions=ins))
    assert by_pc['0059911e']['bytes']=='8986a0000000'
    for address,bits in {'0059094d':'8b442448','00590955':'89442440','00590960':'8d4c2434','00590964':'51','00590965':'ff17','0059096d':'83c404'}.items():assert by_pc[address]['bytes']==bits
    queue=dict(va='005907b0',status='uncompiled_proof_queue',body_bytes=708,original_instructions=large,
        stack_frame='entryS; frame E=S-0x11c after SUB10c and four saves; argsE+120/E+124/E+128',
        parser_output=dict(call='0059084e',pointer_producer='00590841 LEA ECX,[ESP+78]',output_minimum_span='0xa4 bytes;59911e writes DWORD atout+0xa0',
            erroneous_getC='local_a4[4] is only8B; surrounding char/array locals are aliases of the same contiguous output region'),
        callback_packet=dict(call='00590965 CALL[EDI]',stack_argument='E+34; callerADD ESP,4',fields=[dict(offset=0,width=4,producer='00590922 constant1'),
            dict(offset=4,width=4,producer='00590937/45 output[E+ac+index*4]'),dict(offset=8,width=4,producer='0059093e/49 output[E+bc+index*4]'),
            dict(offset=12,width=4,producer='0059094d/55 first handle from[E+48]')],
            erroneous_getC='Three local_e8/e4/e0 values omit fourth produced DWORD; code* cast has no proven provider-target contract',
            slots_base='006b49e0',count_signed_byte='006b49a2',return_contract='unused in consumer; callee consumed registers/storage not yet established'),
        next_step='Trace original callback registration/indirect writes to006b49a2 and006b49e0 slots; record actual targets at00590965, then exact callee input reads/RET. Model raw contiguous parser output+fourDWORD packet before native lowering; no semantic struct guess.',
        source=relative(oldsources['005907b0']),source_sha256=digest(oldsources['005907b0']),static_witnesses=windows,
        no_native_body_or_guessed_callback=True)
    write(RUN/'005907b0-proof-queue.json',queue);pin(RUN/'005907b0-proof-queue.json')
    header=OUT/'consumer229.h';header.write_text(HEADER,encoding='utf8',newline='\n')
    cpp=OUT/(VA+'.cpp');cpp.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+BODY,encoding='utf8',newline='\n')
    fixture=OUT/'original-comparison-fixture.cpp';fixture.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE,encoding='utf8',newline='\n')
    for path in [header,cpp,fixture]:pin(path)
    proof=dict(schema=1,original_sha256=abi.SHA,selected=SELECTED,compiled_scope=[VA],ownership=ownership,inferred179=decl,original_instructions=instructions,
        frozen180_sources={va:dict(path=relative(p),sha256=digest(p))for va,p in oldsources.items()},
        contract='uint __cdecl FUN_00590070(int): stack+4 signed32, EAX32, twoRET0, noCALL; exact223 native ?FUN_00590070@@YAIH@Z',
        operations=['Signed index>=0 then signed index < zeroextended low16 of actualDWORD DAT006b48d8.',
            'Entry address=rawDAT006b4a04 + index*12 modulo32; loadDWORD must be nonzero before BYTE+8 read.',
            'NEG AL/SBB EAX,EAX/AND AL,ee maps rawBYTE0 to0 and all nonzero bytes toFFFFFFEE; invalid returnsFFFFFFF8.'],
        uncompiled_queue=relative(RUN/'005907b0-proof-queue.json'),limits=['No table owner/initializer/allocation provided; DAT006b48d8 DWORD overlaps WORD006b48da consumer.',
            '5907b0 excluded: callbacktarget contract and raw output/packet alias recovery required.',
            'Native fixture compares valid mapped storage; concurrency/volatile registers/fault and game acceptance remain open.'])
    write(RUN/'proof-before-compile.json',proof);pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir();flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/MP6']
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        command=list(map(str,command));started=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);seconds=time.perf_counter()-started
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=OUT/(name+'.log');path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p,path,seconds
    command=[abi.COMPILER,*flags,'/Fo'+str(objects)+os.sep,cpp,fixture]
    p,log,seconds=run(command,'compile');assert p.returncode==0,log.read_text();assert not re.search(r'(?:warning|error) C\d+',log.read_text()),log.read_text()
    obj=objects/(VA+'.obj');symbols=coff.coff_symbols(obj)
    assert symbols['defined']==['?FUN_00590070@@YAIH@Z'] and set(symbols['undefined'])=={'?DAT_006b48d8@@3IA','?DAT_006b4a04@@3HA'}
    p,dis,_=run([abi.DUMPBIN,'/disasm',obj],'consumer-disassembly');assert p.returncode==0
    body=dis.read_text().split('?FUN_00590070@@YAIH@Z (',1)[1].split('\n?',1)[0]
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',body,re.M);assert rets and all(not r for r in rets)
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    exe=OUT/'original-comparison-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'original-comparison-fixture.obj',kernel],'fixture-link');assert p.returncode==0,llog.read_text()
    p,nlog,nseconds=run([exe],'fixture-native');assert p.returncode==0,('fixture failed',p.returncode)
    p,fdis,_=run([abi.DUMPBIN,'/disasm',objects/'original-comparison-fixture.obj'],'fixture-disassembly');assert p.returncode==0
    for path in [obj,objects/'original-comparison-fixture.obj',exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(path)
    guard()
    row=dict(va=VA,name='FUN_'+VA,compiled=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
        generated_source=relative(cpp),generated_source_sha256=digest(cpp),dependency_sha256={relative(path):pins[path]for path in [cpp,header,primitive]},forced_headers=[],
        object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
        native_ret_bytes=[0 for _ in rets],original_ret_bytes=[0,0],disassembly=relative(dis),disassembly_sha256=digest(dis))
    summary=dict(schema=1,kind='original-nested-callee-partial-recovery',original_sha256=abi.SHA,selected_scope_vas=SELECTED,compiled_vas=[VA],uncompiled_vas=['005907b0'],
        objects_compiled=1,real_coff_objects=1,results=[row],actual_compiler_batches=1,changed_game_TUs=1,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=seconds,
        compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_log=relative(log),compiler_log_sha256=digest(log),
        input_sha256={relative(path):h for path,h in pins.items()},input_guards_before=True,input_guards_after=True,original_instruction_count=20,original_bytes=58,
        ownership_preflight=ownership,Ghidra_decompilations=0,production_or_union_changes=False,uncompiled_proof_queue=relative(RUN/'005907b0-proof-queue.json'),
        fixture=dict(native_exit_code=0,comparisons=368640,seconds=nseconds,executable=relative(exe),executable_sha256=digest(exe),
            scope='Actual candidate vs original58B:10 signed index patterns,6 low16 counts,3 highword patterns,2 NULL/nonzero entry cases,all256 statusbytes,4 table alignments.',full_game_fidelity_claimed=False),
        remaining_implementation_dependencies=['005907b0'],remaining_data_dependencies=['006b48d8','006b4a04'],limits=proof['limits'])
    write(RUN/'summary.json',summary);print(json.dumps(dict(compiled=[VA],uncompiled=['005907b0'],compile_seconds=seconds,fixture_comparisons=368640,fixture_seconds=nseconds)))


if __name__=='__main__':main()

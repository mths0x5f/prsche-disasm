"""Recover original93B callee565ea0 with211's proved raw caller-clean ABI."""
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
RUN=RUNS/'223-direct-callee-recovery'
OUT=ROOT/'local/experiments/v2-direct-callee-recovery-223'
VA='00565ea0'
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


abi=module('abi223','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff223','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER='''#pragma once
static_assert(sizeof(void*)==4 && sizeof(uint)==4 && sizeof(int)==4 && sizeof(ushort)==2,"original32-bit ABI");
extern int DAT_006b4a04; // original565eb7/ee1 DWORD, raw address32
uint __cdecl FUN_00590070(int);
int __cdecl FUN_00590170(int,int); // exact already compiled181 symbol, two slots only
int __cdecl FUN_005907b0(int,int,int);
extern "C" void *__cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
// Fixed-size representation copies; unaligned/raw-byte storage is permitted.
static __forceinline uint load32_223(const void*p){uint v;memcpy(&v,p,4);return v;}
static __forceinline ushort load16_223(const void*p){ushort v;memcpy(&v,p,2);return v;}
static __forceinline int signed_bits223(uint v){int s;memcpy(&s,&v,4);return s;}
'''

BODY='''// Original565ea0..565efc. void* is an opaque data boundary, no invented class.
// Entry stack+8 is caller-supplied but locally unused (211).
undefined4 __cdecl FUN_00565ea0(void *param_1,undefined4 /*unused_slot8*/)
{
  uint byte_bits = static_cast<const byte *>(param_1)[4];
  int signed_byte = byte_bits < 128u ? static_cast<int>(byte_bits) : static_cast<int>(byte_bits)-256;
  uint guard_bits = FUN_00590070(signed_byte);
  if ((guard_bits & 0x80000000u) == 0) {
    uint offset_bits = static_cast<uint>(signed_byte) * 12u;
    uint record_bits = load32_223(reinterpret_cast<const void *>(static_cast<uint>(DAT_006b4a04) + offset_bits));
    int item = signed_bits223(load32_223(param_1));
    if (item >= 0 && item < static_cast<int>(load16_223(reinterpret_cast<const void *>(record_bits + 6u)))) {
      int location_bits = FUN_00590170(signed_bits223(record_bits),item);
      uint refreshed_record_bits = load32_223(reinterpret_cast<const void *>(static_cast<uint>(DAT_006b4a04) + offset_bits));
      return static_cast<uint>(FUN_005907b0(signed_bits223(refreshed_record_bits),location_bits,reinterpret_cast<int>(param_1)));
    }
  }
  return 0xfffffff8u;
}
'''

FIXTURE='''extern "C" __declspec(dllimport) void __stdcall ExitProcess(uint);
uint __cdecl FUN_00565ea0(void*,uint);
int DAT_006b4a04=0;
uint tableA223[256*3]={},tableB223[256*3]={},recordA223[3]={},recordB223[3]={};
byte input223[16]={};uint trace223[12]={},trace_count223=0;
uint guard223=0,reload223=0,location223=0x87654321u,result223=0xfedcba98u;
uint failures223=0,cases223=0;
void event223(uint id,uint a,uint b,uint c){
 if(trace_count223>=3){++failures223;return;}
 uint at=trace_count223++*4;trace223[at]=id;trace223[at+1]=a;trace223[at+2]=b;trace223[at+3]=c;
}
uint __cdecl FUN_00590070(int id){event223(1,static_cast<uint>(id),0,0);return guard223;}
int __cdecl FUN_00590170(int table,int item){event223(2,static_cast<uint>(table),static_cast<uint>(item),0);
 if(reload223)DAT_006b4a04=reinterpret_cast<int>(tableB223+128*3);return signed_bits223(location223);
}
int __cdecl FUN_005907b0(int table,int location,int input){event223(3,static_cast<uint>(table),static_cast<uint>(location),static_cast<uint>(input));return signed_bits223(result223);}
// Same original instruction sequence93B, labels/relocations bound to controlled seams.
// Not a provider implementation; compares the actual native candidate body with x86.
__declspec(naked) uint __cdecl original223(void*,uint){__asm{
 push esi
 push edi
 mov edi,dword ptr[esp+0xc]
 movsx esi,byte ptr[edi+4]
 push esi
 call FUN_00590070
 add esp,4
 test eax,eax
 jl rejected223
 mov eax,DAT_006b4a04
 lea esi,[esi+esi*2]
 shl esi,2
 mov ecx,dword ptr[esi+eax]
 mov eax,dword ptr[edi]
 test eax,eax
 jl rejected223
 xor edx,edx
 mov dx,word ptr[ecx+6]
 cmp eax,edx
 jge rejected223
 push edi
 push eax
 push ecx
 call FUN_00590170
 add esp,8
 push eax
 mov eax,DAT_006b4a04
 mov ecx,dword ptr[esi+eax]
 push ecx
 call FUN_005907b0
 add esp,0xc
 pop edi
 pop esi
 ret
rejected223:
 pop edi
 mov eax,0xfffffff8
 pop esi
 ret
}}
void reset223(){DAT_006b4a04=reinterpret_cast<int>(tableA223+128*3);trace_count223=0;for(uint i=0;i<12;++i)trace223[i]=0;}
extern "C" void __cdecl entry(){
 const uint indexes[7]={0xffffffffu,0,1,65534,65535,0x7fffffffu,0x80000000u};
 const uint counts[4]={0,1,32768,65535};
 const uint guards[4]={0,0x7fffffffu,0xffffffffu,0x80000000u};
 for(uint i=0;i<256*3;++i){tableA223[i]=reinterpret_cast<uint>(recordA223);tableB223[i]=reinterpret_cast<uint>(recordB223);}
 for(uint id=0;id<256;++id)for(uint ix=0;ix<7;++ix)for(uint co=0;co<4;++co)
 for(uint g=0;g<4;++g)for(uint reload=0;reload<2;++reload)for(uint align=0;align<4;++align){
  byte*p=input223+align;uint value=indexes[ix];for(uint b=0;b<4;++b)p[b]=static_cast<byte>(value>>(b*8));
  p[4]=static_cast<byte>(id);p[5]=0xa5;p[6]=0x5a;p[7]=0xff;
  recordA223[1]=(counts[co]<<16)|0xa55au;recordB223[1]=0xffff1234u;
  guard223=guards[g];reload223=reload;reset223();
  uint actual=FUN_00565ea0(p,0xdeadbeefu),saved_count=trace_count223,saved_table=static_cast<uint>(DAT_006b4a04),saved[12];
  for(uint t=0;t<12;++t)saved[t]=trace223[t];reset223();
  uint expected=original223(p,0x01234567u);
  if(actual!=expected||saved_count!=trace_count223||saved_table!=static_cast<uint>(DAT_006b4a04))++failures223;
  for(uint t=0;t<12;++t)if(saved[t]!=trace223[t])++failures223;++cases223;
 }
 if(cases223!=229376u)++failures223;ExitProcess(failures223?1:0);
}
'''


def main():
    assert (not OUT.exists() or not any(OUT.iterdir())) and not (RUN/'summary.json').exists(),'fresh223 required'
    OUT.mkdir(exist_ok=True);RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input SHA',path)
        assert path not in pins or pins[path]==h;pins[path]=h;return path
    def guard():
        for p,h in pins.items():assert digest(p)==h,('input mutation',p)
    for p in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN]:pin(p)
    prior=load(pin(RUNS/'211-direct-call-contracts/summary.json'))
    pin(RUNS/'211-direct-call-contracts/validation.json')
    pin(ROOT/prior['evidence'],prior['evidence_sha256'])
    previous_union=load(pin(RUNS/'222-native-support-union/summary.json'))
    assert not any(r['va']==VA for r in previous_union['results'])
    nested=next(r for r in previous_union['results']if r['va']=='00590170')
    pin(ROOT/nested['object'],nested['object_sha256']);pin(ROOT/nested['generated_source'],nested['generated_source_sha256'])
    assert nested['symbols']['defined']==['?FUN_00590170@@YAHHH@Z']
    source=pin(ROOT/'local/experiments/v2-pcode-compat-180/prototypes-cpp-0000/00565ea0.cpp')
    primitive=pin(ROOT/'local/experiments/v2-compile-corpus-178/ghidra-scalars-syntax-only.h')
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    for r in abi.rows(pin(ROOT/'research/binary-index/manual-functions.jsonl')):
        if r['module']=='Porsche.exe':catalog[r['entry_va']]=r
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'));overlaps=[];wip=[]
    for r in registry['functions']:
        if r['module']!='Porsche.exe':continue
        assert r['entry_va'] in catalog
        if r['entry_va']==VA or any(int(a,16)<=int(d,16) and int(c,16)<=int(b,16)for a,b in catalog[r['entry_va']]['ranges']for c,d in catalog[VA]['ranges']):overlaps.append(r)
    for p in (ROOT/'iterations/v2/001-original-recovery/source/recovered').rglob('*.cpp'):
        if re.search(r'\b\w*00565ea0\s*\([^;{}]*\)\s*\{',p.read_text(encoding='utf8')):wip.append(relative(p))
    assert not overlaps and not wip,('ownership',overlaps,wip)
    declarations={r['entry_va']:r for r in abi.rows(pin(abi.DECL))if r['entry_va']in[VA,'00590070','00590170','005907b0']}
    raw=pin(ROOT/'local/game/Porsche.exe',abi.SHA).read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    machine,count,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',raw,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+optional+i*40+8)[1:]for i in range(count)]
    instructions={}
    for va in [VA,'00565e70','00590070','00590170','005907b0']:
        ins=abi.function_instructions(catalog[va],ix)
        for i in ins:
            rva=int(i['va'],16)-base;n=len(i['bytes'])//2
            start,size,offset=next(s for s in sections if s[0]<=rva and rva+n<=s[0]+s[1])
            assert raw[offset+rva-start:offset+rva-start+n].hex()==i['bytes'],i
        instructions[va]=ins
    original=instructions[VA];pc={i['va']:i for v in instructions.values()for i in v}
    assert len(original)==38 and sum(len(i['bytes'])//2 for i in original)==93
    assert [i['va']for i in original if '[ESP' in i['instruction']]==['00565ea2']
    assert [i['bytes']for i in original if i['instruction'].startswith('RET')]==['c3','c3']
    assert not any(i['instruction'].startswith('CALL') and not i['instruction'].startswith('CALL 0x')for i in original)
    for address,bits in {'00565ed5':'57','00565ed6':'50','00565ed7':'51','00565edd':'83c408','00565ee0':'50','00565ee9':'51','00565eef':'83c40c','005907fd':'8b8c2428010000'}.items():assert pc[address]['bytes']==bits
    header=OUT/'consumer223.h';header.write_text(HEADER,encoding='utf8',newline='\n')
    cpp=OUT/(VA+'.cpp');cpp.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+BODY,encoding='utf8',newline='\n')
    fixture=OUT/'original-comparison-fixture.cpp';fixture.write_text('#include "'+primitive.as_posix()+'"\n#include "'+header.as_posix()+'"\n'+FIXTURE,encoding='utf8',newline='\n')
    for p in [header,cpp,fixture]:pin(p)
    proof=dict(schema=1,original_sha256=abi.SHA,entry_va=VA,frozen180_source=relative(source),frozen180_source_sha256=digest(source),inferred179=declarations,
        original_instructions=instructions,ownership=dict(canonical_exact_or_interior=overlaps,WIP=wip,already_compiled=False),
        contract='uint __cdecl FUN_00565ea0(void*,uint): stack+4 raw data pointer32, stack+8 locally unused, EAX32, two RET0 exits. Exact211 native symbol ?FUN_00565ea0@@YAIPAXI@Z.',
        lost_dataflow=[dict(pcs=['00565ea6'],before='getC DWORD param_1[1] then char truncation',after='one signed BYTE read input+4; no +5..+7 read'),
            dict(pcs=['00565ed5','00565ed6','00565ed7','00565ed8','00565edd','00565ee0','00565ee9','00565eea','00565eef'],before='getC passes3 to590170 and2 to5907b0',
                after='EDI remains on stack across590170(two consumed slots); is third argument of5907b0; first argument reloaded via DAT006b4a04 after590170'),
            dict(pcs=['00565ebc','00565ebf','00565ec2','00565ec5','00565ecd','00565ed1','00565ed3'],after='modulo32 table offset signedbyte*12, DWORD tablepointer/input index, unsignedWORD limit, signed index comparisons')],
        calls=[dict(va='00590070',args=['signedbyte+4 signextended32'],cleanup=4,result='EAX32 signbit guard'),dict(va='00590170',args=['recordaddress32','signed index32'],cleanup=8,result='EAX32 raw location'),
            dict(va='005907b0',args=['refreshed recordaddress32','previous EAX32','original inputaddress32'],cleanup=12,result='EAX32 returned unchanged')],
        indirect_calls_in_target=0,fixture='Actual corrected body vs original93B instruction sequence with controlled direct-call boundaries; no provider replacement.',
        limits=['Original nested provider bodies are not reconstructed here; alreadycompiled590170 symbol retained exactly.',
            'Opaque pointee layout/ownership/lifetime unknown; only BYTE+4, DWORD+0 and recordWORD+6 consumers proven.',
            'Raw-load representation helpers preserve bytes/unaligned inputs; volatile-register/concurrency/atomicity/fault/game acceptance remains deferred.'])
    write(RUN/'proof-before-compile.json',proof);pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/diagnostics:column','/MP6']
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
    assert symbols['defined']==['?FUN_00565ea0@@YAIPAXI@Z']
    assert set(symbols['undefined'])=={'?DAT_006b4a04@@3HA','?FUN_00590070@@YAIH@Z','?FUN_00590170@@YAHHH@Z','?FUN_005907b0@@YAHHHH@Z'},symbols
    p,dis,_=run([abi.DUMPBIN,'/disasm',obj],'consumer-disassembly');assert p.returncode==0
    body=dis.read_text().split('?FUN_00565ea0@@YAIPAXI@Z (',1)[1].split('\n?',1)[0]
    rets=re.findall(r'^[ \t]*[0-9A-F]+:[ \t]+(?:[0-9A-F]{2} )+[ \t]+ret[ \t]*([^\n]*)',body,re.M);assert rets and all(not r for r in rets)
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    exe=OUT/'original-comparison-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),obj,objects/'original-comparison-fixture.obj',kernel],'fixture-link');assert p.returncode==0,llog.read_text()
    p,nlog,nseconds=run([exe],'fixture-native');assert p.returncode==0,('fixture failed',p.returncode)
    p,fdis,_=run([abi.DUMPBIN,'/disasm',objects/'original-comparison-fixture.obj'],'fixture-disassembly');assert p.returncode==0
    for p in [obj,objects/'original-comparison-fixture.obj',exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    row=dict(va=VA,name='FUN_'+VA,compiled=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
        generated_source=relative(cpp),generated_source_sha256=digest(cpp),dependency_sha256={relative(p):pins[p]for p in [cpp,header,primitive]},forced_headers=[],
        object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
        native_ret_bytes=[0 for _ in rets],original_ret_bytes=[0,0],disassembly=relative(dis),disassembly_sha256=digest(dis))
    summary=dict(schema=1,kind='original-direct-callee-recovery',original_sha256=abi.SHA,objects_compiled=1,real_coff_objects=1,results=[row],actual_compiler_batches=1,
        changed_game_TUs=1,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=seconds,compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),
        compiler_log=relative(log),compiler_log_sha256=digest(log),input_sha256={relative(p):h for p,h in pins.items()},input_guards_before=True,input_guards_after=True,
        original_instruction_count=38,original_bytes=93,ownership_preflight=dict(canonical_exact_or_interior=0,WIP=0,already_compiled=0),Ghidra_decompilations=0,production_or_union_changes=False,
        fixture=dict(native_exit_code=0,comparisons=229376,seconds=nseconds,executable=relative(exe),executable_sha256=digest(exe),
            scope='Actual candidate vs original instruction sequence, controlled direct boundaries: all256 signedbyte inputs,7 signed index patterns,4 unsignedWORD limits,4 guard bitpatterns,2 table-reload paths,4 unaligned inputs; rawEAX and complete call traces match.',full_provider_fidelity_claimed=False),
        direct_dependencies=['00590070','00590170','005907b0'],already_compiled_dependency=['00590170'],remaining_implementation_dependencies=['00590070','005907b0'],limits=proof['limits'])
    write(RUN/'summary.json',summary);print(json.dumps(dict(compiled=[VA],compile_seconds=seconds,fixture_comparisons=229376,fixture_seconds=nseconds)))


if __name__=='__main__':main()

"""Three closed original CALL chains, translated by the reusable Run257 backend.

No union packet, game implementation/provider, original-code fallback or native
FUN alias. Native original instructions occur only in the comparison fixture.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/258-x86-call-chain'
OUT=ROOT/'local/experiments/v2-x86-call-chain-258'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BACKEND_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
CHAINS=(('00515ca0','004bc610'),('00466e60','00466e80'),('004cecc0','004e0dc0'))
VAS=tuple(v for chain in CHAINS for v in chain)
SIZES=(18,5,29,9,20,23)
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


DISPATCH='''#include "machine257.h"
extern U missing_events258,missing_pc258,bad_return_injection258,callee_events258,callee_entry_sp258,callee_entry_return258;
// Only six generated original entries. Fault injection belongs only to negative tests.
void dispatch257(Machine257&s,U target){
 s.pc=target;
 if(target==0x004bc610u || target==0x00466e80u || target==0x004e0dc0u){
  ++callee_events258;callee_entry_sp258=s.r[4];callee_entry_return258=read257(s.r[4],4u);
 }
 switch(target){
 case 0x00515ca0u:translated_00515ca0(s);return;
 case 0x00466e60u:translated_00466e60(s);return;
 case 0x004cecc0u:translated_004cecc0(s);return;
 case 0x004bc610u:translated_004bc610(s);break;
 case 0x00466e80u:translated_00466e80(s);break;
 case 0x004e0dc0u:translated_004e0dc0(s);break;
 default:++missing_events258;missing_pc258=target;s.stop=Stop257::MissingEntry;return;
 }
 if(bad_return_injection258 && s.stop==Stop257::Returned)s.pc^=1u;
}
'''


FIXTURE=r'''#include "machine257.h"
extern "C" __declspec(dllimport) void __stdcall ExitProcess(U);
extern "C" __declspec(dllimport) void* __stdcall CreateFileA(const char*,U,U,void*,U,U,void*);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,U,U*,void*);
extern "C" __declspec(dllimport) int __stdcall CloseHandle(void*);
extern "C" void* __cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
U saved_sp258,saved_bp258,saved_bx258,saved_si258,saved_di258;
U seen258[8],seen_flags258,seed258[8],seed_flags258,target258,continuation258,guest_sp258;
U failures258,cases258,missing_events258,missing_pc258,bad_return_injection258;
U callee_events258,callee_entry_sp258,callee_entry_return258;
B arena258[1024],before258[1024],native_memory258[1024];
B stack258[256],stack_before258[256],native_stack258[256];
const U halt258=0x0badf00du;
void require258(bool value){if(!value)++failures258;}
bool valid258(U a,U n){
 U m=reinterpret_cast<U>(arena258),s=reinterpret_cast<U>(stack258);
 return n<=4u && ((a>=m && a-m<=1024u-n)||(a>=s && a-s<=256u-n));
}
U read257(U a,U n){U v=0;require258(valid258(a,n));if(valid258(a,n))memcpy(&v,reinterpret_cast<const B*>(a),n);return v;}
void write257(U a,U n,U v){require258(valid258(a,n));if(valid258(a,n))memcpy(reinterpret_cast<B*>(a),&v,n);}
// All original oracle bytes below are independently checked against the PE.
// Only direct CALL REL32 operands are rebound to the matching original oracle.
__declspec(naked) void original_004bc610_258(){__asm{
 mov byte ptr[ecx+0x1d],1
 ret
}}
__declspec(naked) void original_00515ca0_258(){__asm{
 push esi
 mov esi,ecx
 call original_004bc610_258
 xor al,al
 mov byte ptr[esi+0x2c],al
 mov byte ptr[esi+0x2d],al
 pop esi
 ret
}}
__declspec(naked) void original_00466e80_258(){__asm{
 mov eax,dword ptr[esp+4]
 mov dword ptr[ecx],eax
 ret 4
}}
__declspec(naked) void original_00466e60_258(){__asm{
 mov eax,dword ptr[esp+4]
 push ecx
 mov edx,esp
 mov dword ptr[ecx+0x28],eax
 mov dword ptr[edx],eax
 mov ecx,dword ptr[ecx+0xc]
 add ecx,0xb8
 call original_00466e80_258
 ret 4
}}
__declspec(naked) void original_004e0dc0_258(){__asm{
 mov eax,dword ptr[esp+4]
 mov edx,dword ptr[esp+8]
 mov dword ptr[ecx+0x130],eax
 mov dword ptr[ecx+0x12c],edx
 ret 8
}}
__declspec(naked) void original_004cecc0_258(){__asm{
 mov ecx,dword ptr[ecx+0x14c]
 test ecx,ecx
 je done258
 push 0
 push 0
 call original_004e0dc0_258
done258:
 ret
}}
// RET from an original chain reaches this test-only hook. Save all registers,
// then restore the HOST ESP before PUSHFD, preserving every guest stack byte.
__declspec(naked) void capture258(){__asm{
 mov seen258[0],eax
 mov seen258[4],ecx
 mov seen258[8],edx
 mov seen258[12],ebx
 mov seen258[16],esp
 mov seen258[20],ebp
 mov seen258[24],esi
 mov seen258[28],edi
 mov esp,saved_sp258
 pushfd
 pop seen_flags258
 mov ebx,saved_bx258
 mov esi,saved_si258
 mov edi,saved_di258
 mov ebp,saved_bp258
 jmp dword ptr continuation258
}}
__declspec(naked) void original_edge258(){__asm{
 mov saved_sp258,esp
 mov saved_bp258,ebp
 mov saved_bx258,ebx
 mov saved_si258,esi
 mov saved_di258,edi
 mov eax,offset resume258
 mov continuation258,eax
 push seed_flags258
 popfd
 mov eax,seed258[0]
 mov ecx,seed258[4]
 mov edx,seed258[8]
 mov ebx,seed258[12]
 mov ebp,seed258[20]
 mov esi,seed258[24]
 mov edi,seed258[28]
 mov esp,guest_sp258
 jmp dword ptr target258
resume258:
 ret
}}
void negative_tests258(){
 for(U i=0;i<1024;++i)arena258[i]=0xa5u;
 for(U i=0;i<256;++i)stack258[i]=0x69u;
 U sp=reinterpret_cast<U>(stack258+128);write257(sp,4,halt258);
 Machine257 missing={};missing.r[4]=sp;missing.flags=0x843u;missing.stop=Stop257::Running;missing.budget=64;
 dispatch257(missing,0x00ff1234u);
 require258(missing.stop==Stop257::MissingEntry && missing.pc==0x00ff1234u && missing.r[4]==sp);
 require258(missing_events258==1u && missing_pc258==0x00ff1234u);
 Machine257 missing_call={};missing_call.r[4]=sp;missing_call.stop=Stop257::Running;missing_call.budget=64;
 bool resumed=call257(missing_call,0x00ff1234u,0x00515ca8u);
 require258(!resumed && missing_call.stop==Stop257::MissingEntry && missing_call.pc==0x00ff1234u);
 require258(missing_call.r[4]==sp-4u && read257(sp-4u,4u)==0x00515ca8u && missing_events258==2u);
 // Actual generated callee executes, then the fixture corrupts only its returned
 // PC. CALL must reject the edge, preventing XOR/stores/POP/RET in the caller.
 Machine257 bad={};bad.r[1]=reinterpret_cast<U>(arena258+3);bad.r[4]=sp;bad.r[6]=0x87654321u;
 bad.flags=0x843u;bad.stop=Stop257::Running;bad.budget=64;
 bad_return_injection258=1;dispatch257(bad,0x00515ca0u);bad_return_injection258=0;
 require258(bad.stop==Stop257::BadReturn && bad.pc==(0x00515ca8u^1u));
 require258(bad.r[4]==sp-4u && bad.r[6]==reinterpret_cast<U>(arena258+3));
 require258(arena258[3+0x1d]==1u && arena258[3+0x2c]==0xa5u && arena258[3+0x2d]==0xa5u);
 require258(read257(sp-8u,4u)==0x00515ca8u && read257(sp,4u)==halt258);
 Machine257 exhausted={};exhausted.r[4]=sp;exhausted.stop=Stop257::Running;exhausted.budget=0;
 dispatch257(exhausted,0x00515ca0u);require258(exhausted.stop==Stop257::BudgetExhausted && exhausted.r[4]==sp);
}
void text258(char*&p,const char*s){while(*s)*p++=*s++;}
void decimal258(char*&p,U value){char digits[10];U n=0;do{digits[n++]=static_cast<char>('0'+value%10u);value/=10u;}while(value);while(n)*p++=digits[--n];}
void fixture_report258(){
 char text[1024];char*p=text;
 text258(p,"{\n  \"original_sha256\": \"ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39\",\n  \"module\": \"Porsche.exe\",\n  \"provenance\": \"isolatedVMpilot\",\n  \"native_game_execution\": false,\n  \"scope\": \"closed-call-chain-and-synthetic-negative-tests\",\n  \"cases\": ");
 decimal258(p,cases258);text258(p,",\n  \"failures\": ");decimal258(p,failures258);
 text258(p,",\n  \"synthetic_missing_entry_events\": ");decimal258(p,missing_events258);
 text258(p,",\n  \"synthetic_missing_entry_pc\": \"");const char*digits="0123456789abcdef";
 for(U n=8;n;--n)*p++=digits[(missing_pc258>>((n-1u)*4u))&15u];text258(p,"\"\n}\n");
 void*h=CreateFileA("fixture-result.json",0x40000000u,0,0,2,0x80u,0);U written=0;
 require258(h!=reinterpret_cast<void*>(0xffffffffu));
 if(h!=reinterpret_cast<void*>(0xffffffffu)){require258(WriteFile(h,text,static_cast<U>(p-text),&written,0)!=0);require258(written==static_cast<U>(p-text));require258(CloseHandle(h)!=0);}
}
extern "C" void __cdecl entry(){
 void*originals[3]={reinterpret_cast<void*>(&original_00515ca0_258),reinterpret_cast<void*>(&original_00466e60_258),reinterpret_cast<void*>(&original_004cecc0_258)};
 U entries[3]={0x00515ca0u,0x00466e60u,0x004cecc0u};
 U return_pcs[3]={0x00515ca8u,0x00466e7au,0x004cecd3u};U return_offsets[3]={8u,26u,19u};
 U values[6]={0,1,0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu};
 U sp=reinterpret_cast<U>(stack258+128);
 for(U chain=0;chain<3;++chain)for(U align=0;align<8;++align)for(U value=0;value<6;++value)
 for(U flags=0;flags<16;++flags)for(U seed=0;seed<8;++seed)for(U present=0;present<2;++present){
  for(U i=0;i<1024;++i)arena258[i]=static_cast<B>(i*37u+seed*59u+value*17u);
  for(U i=0;i<256;++i)stack258[i]=static_cast<B>(i*31u+seed*47u+value*23u);
  U receiver=reinterpret_cast<U>(arena258+align),destination=reinterpret_cast<U>(arena258+512+align);
  if(chain==1)write257(receiver+0xcu,4,destination-0xb8u);
  if(chain==2)write257(receiver+0x14cu,4,present?destination:0u);
  write257(sp,4,reinterpret_cast<U>(&capture258));write257(sp+4u,4,values[value]);
  for(U i=0;i<1024;++i)before258[i]=arena258[i];
  for(U i=0;i<256;++i)stack_before258[i]=stack258[i];
  for(U i=0;i<8;++i)seed258[i]=(0x13579bdfu*(i+1u))^(0x80000001u*seed)^values[value];
  seed258[1]=receiver;seed258[4]=sp;
  seed_flags258=0x202u|(flags&1u)|((flags&2u)<<5u)|((flags&4u)<<5u)|((flags&8u)<<8u);
  target258=reinterpret_cast<U>(originals[chain]);guest_sp258=sp;original_edge258();
  for(U i=0;i<1024;++i)native_memory258[i]=arena258[i];
  for(U i=0;i<256;++i)native_stack258[i]=stack258[i];
  require258(read257(sp,4)==reinterpret_cast<U>(&capture258));
  U call_slot=chain==2?sp-12u:sp-8u;
  if(chain!=2 || present){
   require258(read257(call_slot,4)==reinterpret_cast<U>(originals[chain])+return_offsets[chain]);
   U offset=call_slot-reinterpret_cast<U>(stack258);U original_pc=return_pcs[chain];
   memcpy(native_stack258+offset,&original_pc,4u);
  }
  memcpy(native_stack258+128,&halt258,4u);
  for(U i=0;i<1024;++i)arena258[i]=before258[i];
  for(U i=0;i<256;++i)stack258[i]=stack_before258[i];write257(sp,4,halt258);
  Machine257 state={};for(U i=0;i<8;++i)state.r[i]=seed258[i];
  state.flags=seed_flags258;state.pc=entries[chain];state.stop=Stop257::Running;state.budget=128;
  callee_events258=0;dispatch257(state,entries[chain]);
  for(U i=0;i<8;++i)require258(state.r[i]==seen258[i]);
  require258(((state.flags^seen_flags258)&0x8c1u)==0);
  require258(state.pc==halt258 && state.stop==Stop257::Returned);
  require258(state.r[4]==sp+(chain==1?8u:4u));
  require258(callee_events258==(chain==2 && !present?0u:1u));
  if(callee_events258)require258(callee_entry_sp258==call_slot && callee_entry_return258==return_pcs[chain]);
  for(U i=0;i<1024;++i)require258(arena258[i]==native_memory258[i]);
  for(U i=0;i<256;++i)require258(stack258[i]==native_stack258[i]);
  ++cases258;
 }
 require258(cases258==36864u && missing_events258==0u);
 negative_tests258();fixture_report258();ExitProcess(failures258?1u:0u);
}
'''


def main():
    resume='--finalize-existing' in sys.argv
    assert not (RUN/'summary.json').exists(),'completed258 immutable'
    assert (RUN/'selection.json').exists(),'original indexed selection required'
    if resume:assert (OUT/'compile.execution.json').exists()
    else:assert not OUT.exists() or not any(OUT.iterdir()),'fresh258 output required'
    OUT.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input pin',path)
        pins[relative(path)]=h;return path
    def guard():
        for name,h in pins.items():assert digest(ROOT/name)==h,('input drift',name)
    def materialize(path,text):
        data=text.encode('utf8')
        if resume:assert path.read_bytes()==data,('compiled source drift',path)
        else:path.write_bytes(data)
        pin(path)
    abi=module('abi258','scripts/research/experiment-v2-thiscall-186.py')
    pe=module('pe258','scripts/research/audit-v2-x86-tail-dispatch-253.py')
    oracle=module('oracle258','scripts/research/audit-v2-nested-calls-229.py')
    backend=module('backend257_for258','scripts/research/x86-cpp-backend-257.py')
    assert digest(ROOT/'scripts/research/x86-cpp-backend-257.py')==BACKEND_SHA,'frozen257 identity'
    planner=module('defs245_for258','scripts/research/plan-v2-link-frontier-245.py')
    for p in [__file__,ROOT/'scripts/research/select-v2-x86-call-chain-258.py',RUN/'selection.json',
              ROOT/'scripts/research/x86-cpp-backend-257.py',ROOT/'scripts/research/audit-v2-x86-tail-dispatch-253.py',
              ROOT/'scripts/research/plan-v2-link-frontier-245.py',ROOT/'scripts/research/experiment-v2-thiscall-186.py',
              ROOT/'scripts/research/audit-v2-nested-calls-229.py',ROOT/'research/binary-index/README.md',ROOT/'research/binary-index/manual-functions.jsonl',
              abi.CORPUS/'functions.jsonl',abi.CORPUS/'disassembly.asm',abi.COMPILER,abi.DUMPBIN,
              ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json']:
        pin(p)
    import capstone
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    catalog={r['entry_va']:r for r in abi.rows(abi.CORPUS/'functions.jsonl')};index=abi.instruction_index()
    registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
    accepted={va:[r for r in registry if r.get('module')=='Porsche.exe' and r['entry_va']==va] for va in VAS}
    wip={va:[] for va in VAS};interior={va:[] for va in VAS};references={va:[] for va in VAS}
    source_root=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'
    for path in sorted(source_root.iterdir()):
        if path.suffix not in ['.cpp','.hpp','.inc']:continue
        text=path.read_text(encoding='utf8')
        hits=[va for va in VAS if va in text]
        if not hits:continue
        pin(path)
        definitions=planner.definitions(text)
        for va in hits:
            references[va].append(relative(path))
            for row in definitions:
                if row['name'].endswith('_'+va):wip[va].append(dict(source=relative(path),definition=row))
    for va in VAS:
        for r in registry:
            if r.get('module')!='Porsche.exe':continue
            row=catalog.get(r['entry_va'])
            if row and any(int(a,16)<int(va,16)<=int(b,16) for a,b in row.get('ranges',[])):
                interior[va].append(r['entry_va'])
    assert not any(accepted.values()) and not any(wip.values()) and not any(interior.values()),('ownership preflight',accepted,wip,interior)
    baseline=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/249-canonical-and-storage-union/summary.json'))
    compiled={r['va']:r for r in baseline['results'] if r['va'] in VAS}
    for r in compiled.values():
        pin(ROOT/r['object'],r['object_sha256']);pin(ROOT/r['generated_source'],r['generated_source_sha256'])
    originals={};witnesses={};sources=[]
    header=backend.HEADER+'\n'+''.join('void translated_'+va+'(Machine257&);\n' for va in VAS)
    materialize(OUT/'machine257.h',header);materialize(OUT/'dispatch258.cpp',DISPATCH);materialize(OUT/'state-fixture.cpp',FIXTURE)
    for va,size in zip(VAS,SIZES):
        raw=pe.original_bytes(image,va,size);ins=abi.function_instructions(catalog[va],index)
        assert raw==bytes.fromhex(''.join(i['bytes'] for i in ins)) and catalog[va]['body_bytes']==size
        generated,witness=backend.translate(raw,int(va,16))
        path=OUT/(va+'.cpp');materialize(path,generated);sources.append(path);originals[va]=raw.hex();witnesses[va]=witness
    rejected=[]
    for raw,why in [(b'\xf7\xf1\xc3','DIV'),(b'\xe8\x00','truncated CALL'),(b'\xd9\xe8\xc3','x87'),(b'\xcc','INT3')]:
        try:backend.translate(raw,0x1000)
        except ValueError:rejected.append(why)
        else:raise AssertionError(('unsupported accepted',why))
    proof=dict(original_sha256=SHA,backend_sha256=BACKEND_SHA,chains=CHAINS,original_hex=originals,instruction_lowering=witnesses,
               accepted_exact_owners=accepted,wip_exact_definitions=wip,accepted_interior_owners=interior,source_references=references,
               existing_compiled_regressions=compiled,unsupported_rejected=rejected,
               state_scope='All8GPRs,CF/ZF/SF/OF,1024object bytes and256gueststack bytes; top/native CALL returnPC mappings are exact per-slot only.',
               return_pc_mapping=[dict(caller=a,callee=b,original_return_pc=f'{int(a,16)+offset:08x}',native_oracle_offset=offset,
                                       guest_call_slot_delta=delta,caller_cleanup=cleanup) for (a,b),offset,delta,cleanup in zip(CHAINS,[8,26,19],[-8,-8,-12],[0,4,0])],
               limits=['Isolated VM backend/native32 fixture only; no game EXE,full CPU or guest memory loader.',
                       'No native FUN alias or typed receiver ABI repair; zero newacceptedfunctions and no union packet.',
                       'Only3direct CALLREL32 relocations normalized; original branch/RET/argument bytes exact.',
                       'BadReturn uses explicit test-only postcallee returnedPC fault injection; not an original behavior claim.',
                       'Native hook restores hostESP beforePUSHFD; gueststack bytes untouched after originalRET.',
                       'Flags proof covers definedCF/ZF/SF/OF for actual valid fixture operands,not all possible arithmetic inputs.'])
    if resume:assert load(RUN/'proof-before-compile.json')==json.loads(json.dumps(proof))
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir(exist_ok=resume)
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120)
        seconds=time.perf_counter()-start
        write(OUT/(name+'.execution.json'),dict(command=command,cwd=str(OUT),exit_code=p.returncode,elapsed_seconds=seconds))
        log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'));return p,log,seconds
    command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/MP6','/Fo'+str(objects)+os.sep,
             *sources,OUT/'dispatch258.cpp',OUT/'state-fixture.cpp']
    if resume:
        execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['command']==list(map(str,command))
        seconds=execution['elapsed_seconds'];clog=OUT/'compile.log'
    else:
        (OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes())
        p,clog,seconds=run(command,'compile');assert p.returncode==0,clog.read_bytes()
    pin(OUT/'captured-compile-driver.py')
    assert not re.search(rb'(?:warning|error) [CD]\d+',clog.read_bytes()),clog.read_bytes()
    oracles=[]
    for va in VAS:
        body,relocs=oracle.coff_function(objects/'state-fixture.obj','?original_'+va+'_258@@YAXXZ')
        raw=bytearray.fromhex(originals[va]);expected=[]
        if va in dict(CHAINS):
            call=next(w for w in witnesses[va] if w['mnemonic']=='call');off=int(call['va'],16)-int(va,16)+1
            expected=[dict(offset=off,symbol='?original_'+dict(CHAINS)[va]+'_258@@YAXXZ',type=20)]
            raw[off:off+4]=bytes(4)
        assert relocs==expected and body==raw,(va,body.hex(),raw.hex(),relocs)
        oracles.append(dict(va=va,bytes=len(body),relocations=relocs,normalized_only_call_rel32=True))
    link=pin(abi.COMPILER.with_name('link.exe'));sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
    libraries=[pin(abi.COMPILER.parents[3]/'lib/x86'/n) for n in ['libcmt.lib','libvcruntime.lib']]+[pin(sdk/'ucrt/x86/libucrt.lib'),pin(sdk/'um/x86/kernel32.lib')]
    exe=OUT/'state-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),
                  *[objects/(va+'.obj') for va in VAS],objects/'dispatch258.obj',objects/'state-fixture.obj',*libraries],'fixture-link')
    assert p.returncode==0,llog.read_bytes()
    p,_,native_seconds=run([exe],'fixture-native');assert p.returncode==0,('original closed-chain comparisons',p.returncode)
    result=load(pin(OUT/'fixture-result.json'))
    assert result==dict(original_sha256=SHA,module='Porsche.exe',provenance='isolatedVMpilot',native_game_execution=False,
                        scope='closed-call-chain-and-synthetic-negative-tests',cases=36864,failures=0,
                        synthetic_missing_entry_events=2,synthetic_missing_entry_pc='00ff1234')
    for p in [*objects.glob('*.obj'),exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    summary=dict(schema=1,kind='isolated-x86-call-chain-pilot',original_sha256=SHA,chains=CHAINS,experimental_vas=VAS,
                 translated_original_bytes=sum(SIZES),translated_original_instructions=sum(len(w) for w in witnesses.values()),
                 new_accepted_functions=0,production_or_union_changed=False,native_game_execution_commands=0,actual_compiler_batches=1,
                 compiler_exit_code=0,compile_seconds=seconds,compiler_warnings=0,native_fixture_exit_code=0,native_seconds=native_seconds,
                 state_comparisons=36864,negative_tests=['MissingEntry dispatcher','MissingEntry CALL preservesstop','BadReturn after actual generatedcalleeRET','BudgetExhausted'],
                 fixture_result=relative(OUT/'fixture-result.json'),missing_entry_provenance='isolatedVMpilot',planner_queue_feed=False,
                 oracle=oracles,input_sha256=pins,before_after_guards=True,command=list(map(str,command)),resumed_existing_compile=resume,
                 existing_compiled_regression_vas=sorted(compiled),limits=proof['limits'])
    write(RUN/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['translated_original_bytes','translated_original_instructions','state_comparisons','compile_seconds','native_seconds','new_accepted_functions']}))


if __name__=='__main__':main()

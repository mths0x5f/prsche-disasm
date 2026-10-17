"""Synthetic CPU infrastructure tests for frozen257. No original game bodies."""
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
RUN=ROOT/'iterations/v2/001-original-recovery/runs/262-x86-cpu-primitives'
OUT=ROOT/'local/experiments/v2-x86-cpu-primitives-262'
BACKEND_SHA='fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc'
FRAGMENTS=[
 ('add-ah-cl','02e1c3','add ah,cl\n ret','binary',8),
 ('sub-ah-cl','2ae1c3','sub ah,cl\n ret','binary',8),
 ('sbb-ah-cl','1ae1c3','sbb ah,cl\n ret','binary',8),
 ('add-ax-cx','6603c1c3','add ax,cx\n ret','binary',16),
 ('sub-ax-cx','662bc1c3','sub ax,cx\n ret','binary',16),
 ('sbb-ax-cx','661bc1c3','sbb ax,cx\n ret','binary',16),
 ('add-eax-ecx','03c1c3','add eax,ecx\n ret','binary',32),
 ('sub-eax-ecx','2bc1c3','sub eax,ecx\n ret','binary',32),
 ('sbb-eax-ecx','1bc1c3','sbb eax,ecx\n ret','binary',32),
 ('neg-ah','f6dcc3','neg ah\n ret','unary',8),
 ('neg-ax','66f7d8c3','neg ax\n ret','unary',16),
 ('neg-eax','f7d8c3','neg eax\n ret','unary',32),
 ('high8-word-views','8ae1668bd0c3','mov ah,cl\n mov dx,ax\n ret','views',0),
 ('push-esp','5458c3','push esp\n pop eax\n ret','stack',0),
 ('pop-esp','5cc3','pop esp\n ret','stack',0),
 ('pop-memory-esp','8f0424c3','pop dword ptr[esp]\n ret','stack',0),
 ('indirect-call-esp','ff14248d642404c3','call dword ptr[esp]\n lea esp,[esp+4]\n ret','indirect',0),
 ('indirect-tail-jmp','ff642404','jmp dword ptr[esp+4]','indirect',0),
 ('indirect-leaf-neg-eax','f7d8c3','neg eax\n ret','callee',32),
]
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def entries():
    return [dict(id=i,name=name,synthetic_entry=f'{0x10001000+i*0x100:08x}',hex=raw,asm=assembly,kind=kind,bits=bits)
            for i,(name,raw,assembly,kind,bits) in enumerate(FRAGMENTS)]


def dispatcher(rows):
    return '#include "machine257.h"\nvoid dispatch257(Machine257&s,U target){\ns.pc=target;switch(target){\n'+''.join(
        'case 0x'+r['synthetic_entry']+'u:translated_'+r['synthetic_entry']+'(s);return;\n' for r in rows)+\
        'default:s.stop=Stop257::MissingEntry;return;\n}}\n'


FIXTURE=r'''#include "machine257.h"
static_assert(sizeof(void*)==4,"synthetic native32 fixture");
extern "C" __declspec(dllimport) void __stdcall ExitProcess(U);
extern "C" __declspec(dllimport) void* __stdcall CreateFileA(const char*,U,U,void*,U,U,void*);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,U,U*,void*);
extern "C" __declspec(dllimport) int __stdcall CloseHandle(void*);
extern "C" void* __cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
U saved_sp262,saved_bp262,saved_bx262,saved_si262,saved_di262;
U seed262[8],seen262[8],seed_flags262,seen_flags262,target262,continuation262,guest_sp262;
U failures262,cases262,arithmetic262,views262,stack_cases262,indirect262,mapped_slots262;
B stack262[256],before262[256],native_stack262[256];
const U halt262=0x0badf00du,leaf_pc262=0x10002200u;
void require262(bool value){if(!value)++failures262;}
bool valid262(U a,U n){U base=reinterpret_cast<U>(stack262);return (n==1u||n==2u||n==4u)&&a>=base&&a-base<=256u-n;}
U read257(U a,U n){U v=0;require262(valid262(a,n));if(valid262(a,n))memcpy(&v,reinterpret_cast<const B*>(a),n);return v;}
void write257(U a,U n,U v){require262(valid262(a,n));if(valid262(a,n))memcpy(reinterpret_cast<B*>(a),&v,n);}
// All register stores precede capture; host ESP is restored before PUSHFD.
__declspec(naked) void capture262(){__asm{
 mov seen262[0],eax
 mov seen262[4],ecx
 mov seen262[8],edx
 mov seen262[12],ebx
 mov seen262[16],esp
 mov seen262[20],ebp
 mov seen262[24],esi
 mov seen262[28],edi
 mov esp,saved_sp262
 pushfd
 pop seen_flags262
 mov ebx,saved_bx262
 mov esi,saved_si262
 mov edi,saved_di262
 mov ebp,saved_bp262
 jmp dword ptr continuation262
}}
__declspec(naked) void native_edge262(){__asm{
 mov saved_sp262,esp
 mov saved_bp262,ebp
 mov saved_bx262,ebx
 mov saved_si262,esi
 mov saved_di262,edi
 mov eax,offset resume262
 mov continuation262,eax
 push seed_flags262
 popfd
 mov eax,seed262[0]
 mov ecx,seed262[4]
 mov edx,seed262[8]
 mov ebx,seed262[12]
 mov ebp,seed262[20]
 mov esi,seed262[24]
 mov edi,seed262[28]
 mov esp,guest_sp262
 jmp dword ptr target262
resume262:
 ret
}}
// SYNTHETIC_ORACLES
void*targets262[19]={SYNTHETIC_TARGETS};
void normalize_slot262(U offset,U native_pc,U guest_pc){
 U value=0;memcpy(&value,native_stack262+offset,4u);require262(value==native_pc);
 memcpy(native_stack262+offset,&guest_pc,4u);++mapped_slots262;
}
U edge262(U n,U bits){U mask=bits==8?0xffu:bits==16?0xffffu:0xffffffffu;U sign=(mask>>1)+1u;
 switch(n){case 0:return 0;case 1:return 1;case 2:return mask;case 3:return sign-1u;case 4:return sign;case 5:return sign+1u;case 6:return mask-1u;default:return 2;}}
void compare262(U id,U align,U flags,U seed){
 U entry=0x10001000u+id*0x100u,sp=reinterpret_cast<U>(stack262+128+align),alternate=reinterpret_cast<U>(stack262+192+align);
 U capture=reinterpret_cast<U>(&capture262),leaf=reinterpret_cast<U>(targets262[18]);
 for(U i=0;i<256;++i)stack262[i]=static_cast<B>(i*31u+seed*47u+flags*17u);
 write257(sp,4u,capture);
 if(id==14u){write257(sp,4u,alternate);write257(alternate,4u,capture);}
 if(id==16u){write257(sp,4u,leaf);write257(sp+4u,4u,capture);}
 if(id==17u)write257(sp+4u,4u,leaf);
 for(U i=0;i<256;++i)before262[i]=stack262[i];
 seed262[4]=sp;seed_flags262=0x202u|(flags&1u)|((flags&2u)<<5u)|((flags&4u)<<5u)|((flags&8u)<<8u);
 target262=reinterpret_cast<U>(targets262[id]);guest_sp262=sp;native_edge262();
 for(U i=0;i<256;++i)native_stack262[i]=stack262[i];
 U top=id==14u?192u+align:(id==16u?132u+align:128u+align);
 normalize_slot262(top,capture,halt262);
 if(id==15u)normalize_slot262(132u+align,capture,halt262);
 if(id==16u){
  normalize_slot262(128u+align,leaf,leaf_pc262);
  normalize_slot262(124u+align,reinterpret_cast<U>(targets262[16])+3u,entry+3u);
 }
 if(id==17u)normalize_slot262(132u+align,leaf,leaf_pc262);
 for(U i=0;i<256;++i)stack262[i]=before262[i];
 write257(reinterpret_cast<U>(stack262)+top,4u,halt262);
 if(id==16u)write257(sp,4u,leaf_pc262);
 if(id==17u)write257(sp+4u,4u,leaf_pc262);
 Machine257 state={};for(U i=0;i<8;++i)state.r[i]=seed262[i];
 state.flags=seed_flags262;state.pc=entry;state.stop=Stop257::Running;state.budget=64u;
 dispatch257(state,entry);
 for(U i=0;i<8;++i)require262(state.r[i]==seen262[i]);
 require262(((state.flags^seen_flags262)&0x8c1u)==0);
 require262(state.stop==Stop257::Returned && state.pc==halt262);
 U expected_sp=id==14u?alternate+4u:sp+((id==15u||id==16u)?8u:4u);
 require262(state.r[4]==expected_sp);
 if(id==13u)require262(state.r[0]==sp);
 for(U i=0;i<256;++i)require262(stack262[i]==native_stack262[i]);
 ++cases262;
}
void seed_registers262(U seed){for(U i=0;i<8;++i)seed262[i]=(0x13579bdfu*(i+1u))^(0x80000001u*seed);}
void text262(char*&p,const char*s){while(*s)*p++=*s++;}
void decimal262(char*&p,U v){char digits[10];U n=0;do{digits[n++]=static_cast<char>('0'+v%10u);v/=10u;}while(v);while(n)*p++=digits[--n];}
void result262(){
 char text[1024];char*p=text;text262(p,"{\n  \"provenance\": \"syntheticCPUfixture\",\n  \"native_game_execution\": false,\n  \"cases\": ");decimal262(p,cases262);
 text262(p,",\n  \"failures\": ");decimal262(p,failures262);text262(p,",\n  \"arithmetic_cases\": ");decimal262(p,arithmetic262);
 text262(p,",\n  \"view_cases\": ");decimal262(p,views262);text262(p,",\n  \"stack_alias_cases\": ");decimal262(p,stack_cases262);
 text262(p,",\n  \"indirect_cases\": ");decimal262(p,indirect262);text262(p,",\n  \"normalized_exact_slots\": ");decimal262(p,mapped_slots262);text262(p,"\n}\n");
 void*h=CreateFileA("fixture-result.json",0x40000000u,0,0,2,0x80u,0);U written=0;
 require262(h!=reinterpret_cast<void*>(0xffffffffu));
 if(h!=reinterpret_cast<void*>(0xffffffffu)){require262(WriteFile(h,text,static_cast<U>(p-text),&written,0)!=0);require262(written==static_cast<U>(p-text));require262(CloseHandle(h)!=0);}
}
extern "C" void __cdecl entry(){
 U widths[12]={8,8,8,16,16,16,32,32,32,8,16,32};
 for(U id=0;id<12;++id)for(U a=0;a<8;++a)for(U b=0;b<(id<9u?8u:1u);++b)for(U flags=0;flags<16;++flags){
  seed_registers262(a^b);U bits=widths[id],shift=bits==8u?8u:0u,mask=bits==8u?0xffu:bits==16u?0xffffu:0xffffffffu;
  seed262[0]=(seed262[0]&~(mask<<shift))|(edge262(a,bits)<<shift);
  seed262[1]=(seed262[1]&~mask)|edge262(b,bits);
  compare262(id,0u,flags,a^b);++arithmetic262;
 }
 for(U a=0;a<8;++a)for(U b=0;b<8;++b)for(U flags=0;flags<16;++flags){
  seed_registers262(a^b);seed262[0]=(seed262[0]&0xffff0000u)|edge262(a,16u);
  seed262[1]=(seed262[1]&0xffffff00u)|edge262(b,8u);compare262(12u,0u,flags,a^b);++views262;
 }
 for(U id=13;id<18;++id)for(U align=0;align<8;++align)for(U flags=0;flags<16;++flags)for(U seed=0;seed<8;++seed){
  seed_registers262(seed);compare262(id,align,flags,seed);if(id<16u)++stack_cases262;else ++indirect262;
 }
 require262(cases262==15744u && arithmetic262==9600u && views262==1024u && stack_cases262==3072u && indirect262==2048u && mapped_slots262==19840u);
 result262();ExitProcess(failures262?1u:0u);
}
'''


def fixture(rows):
    oracles='\n'.join('__declspec(naked) void oracle262_'+str(r['id'])+'(){__asm{\n '+r['asm']+'\n}}' for r in rows)
    targets=','.join('reinterpret_cast<void*>(&oracle262_'+str(r['id'])+')' for r in rows)
    return FIXTURE.replace('// SYNTHETIC_ORACLES',oracles).replace('SYNTHETIC_TARGETS',targets)


def main():
    finalize='--finalize-existing' in sys.argv
    assert not (RUN/'summary.json').exists(),'completed262 immutable'
    if finalize:assert (OUT/'native-001.execution.json').exists(),'finalize only all existing successful receipts'
    else:assert not OUT.exists() or not any(OUT.iterdir()),'fresh262 output required'
    RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('pin drift',path);pins[relative(path)]=h;return path
    def guard():
        for name,h in pins.items():assert digest(ROOT/name)==h,('input drift',name)
    def materialize(path,text):
        if finalize:assert path.read_bytes()==text.encode('utf8'),('compiled source drift',path)
        else:path.write_text(text,encoding='utf8',newline='\n')
        pin(path)
    abi=module('abi262','scripts/research/experiment-v2-thiscall-186.py')
    backend=module('backend257_for262','scripts/research/x86-cpp-backend-257.py')
    oracle=module('oracle262_parser','scripts/research/audit-v2-nested-calls-229.py')
    for p in [__file__,ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/audit-v2-nested-calls-229.py',abi.COMPILER,abi.DUMPBIN]:pin(p)
    pin(ROOT/'scripts/research/x86-cpp-backend-257.py',BACKEND_SHA)
    import capstone
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    rows=entries();witnesses={};sources=[]
    header=backend.HEADER+'\n'+''.join('void translated_'+r['synthetic_entry']+'(Machine257&);\n' for r in rows)
    for row in rows:
        source,witness=backend.translate(bytes.fromhex(row['hex']),int(row['synthetic_entry'],16))
        sources.append(source);witnesses[row['name']]=witness
    # CALL[ESP] must load the old-stack target before call257 decrements ESP.
    assert witnesses['indirect-call-esp'][0]['cpp']=='U target=read257((0x00000000u+s.r[4]*1u),4u);if(!call257(s,target,0x10002003u))return;'
    assert 's.r[4]-=4u' in backend.HEADER and backend.HEADER.index('write257(s.r[4],4u,returnPC)')>backend.HEADER.index('s.r[4]-=4u')
    materialize(OUT/'machine257.h',header)
    materialize(OUT/'primitives262.cpp','\n'.join(sources)+'\n'+dispatcher(rows))
    materialize(OUT/'state-fixture.cpp',fixture(rows))
    proof=dict(kind='synthetic-CPU-primitives-preflight',backend_sha256=BACKEND_SHA,fragments=rows,instruction_lowering=witnesses,
               entries_are_original_game_functions=False,new_accepted_functions=0,planned_compiler_batches=1,planned_tus=2,planned_cases=15744,
               case_groups=dict(arithmetic=9600,views=1024,stack_aliasing=3072,indirect=2048),
               exact_slot_mapping='Only declared synthetic native code pointers/return slots are mapped to their synthetic guest PCs; every native value checked first.',
               limits=['Synthetic CPU infrastructure only; no original game body/ABI/provider claim or union packet.',
                       'Defined CF/ZF/SF/OF only; no PF/AF/undefined flags, faults,segments,concurrency or full ISA.',
                       'Valid native32 stack arena only; no guest memory loader or invalid-memory behavior.',
                       'Arithmetic AH/AX/EAX and CL/CX/ECX plus MOV AH,CL/MOV DX,AX are the tested views, not all register combinations.',
                       'Only memory indirect CALL[ESP] and tailJMP[ESP+4] into the real synthetic NEG EAX/RET leaf are tested.'])
    if finalize:assert load(RUN/'proof-before-compile.json')==proof
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir(exist_ok=finalize)
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        receipt=OUT/(name+'.execution.json');log=OUT/(name+'.log')
        assert not receipt.exists() and not log.exists(),('attempt receipt immutable',name)
        command=list(map(str,command));start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120)
        seconds=time.perf_counter()-start
        write(receipt,dict(command=command,cwd=str(OUT),exit_code=p.returncode,elapsed_seconds=seconds))
        log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'));return p,log,seconds
    command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/MP6','/Fo'+str(objects)+os.sep,OUT/'primitives262.cpp',OUT/'state-fixture.cpp']
    if finalize:
        execution=load(OUT/'compile-001.execution.json');assert execution['exit_code']==0 and execution['command']==list(map(str,command))
        seconds=execution['elapsed_seconds'];clog=OUT/'compile-001.log'
    else:
        (OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes())
        p,clog,seconds=run(command,'compile-001');assert p.returncode==0,clog.read_bytes()
    pin(OUT/'captured-compile-driver.py')
    assert not re.search(rb'(?:warning|error) [CD]\d+',clog.read_bytes()),clog.read_bytes()
    oracles=[]
    for row in rows:
        body,relocs=oracle.coff_function(objects/'state-fixture.obj','?oracle262_'+str(row['id'])+'@@YAXXZ')
        assert body.hex()==row['hex'] and relocs==[],(row['name'],body.hex(),row['hex'],relocs)
        oracles.append(dict(name=row['name'],id=row['id'],bytes=body.hex(),relocations=relocs))
    link=pin(abi.COMPILER.with_name('link.exe'));sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
    libraries=[pin(abi.COMPILER.parents[3]/'lib/x86'/n) for n in ['libcmt.lib','libvcruntime.lib']]+[pin(sdk/'ucrt/x86/libucrt.lib'),pin(sdk/'um/x86/kernel32.lib')]
    exe=OUT/'state-fixture.exe'
    if not finalize:
        p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),objects/'primitives262.obj',objects/'state-fixture.obj',*libraries],'link-001')
        assert p.returncode==0,llog.read_bytes()
        p,_,native_seconds=run([exe],'native-001');assert p.returncode==0,('synthetic CPU comparisons',p.returncode)
    else:
        assert load(OUT/'link-001.execution.json')['exit_code']==0
        native=load(OUT/'native-001.execution.json');assert native['exit_code']==0;native_seconds=native['elapsed_seconds']
    result=load(pin(OUT/'fixture-result.json'))
    assert result==dict(provenance='syntheticCPUfixture',native_game_execution=False,cases=15744,failures=0,arithmetic_cases=9600,
                        view_cases=1024,stack_alias_cases=3072,indirect_cases=2048,normalized_exact_slots=19840)
    for p in [*objects.glob('*.obj'),exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    summary=dict(schema=1,kind='synthetic-x86-cpu-primitives',backend_sha256=BACKEND_SHA,synthetic_entries=[r['synthetic_entry'] for r in rows],
                 original_game_functions=0,new_accepted_functions=0,production_or_union_changed=False,native_game_execution_commands=0,
                 synthetic_bytes=sum(len(bytes.fromhex(r['hex'])) for r in rows),synthetic_instructions=sum(len(w) for w in witnesses.values()),
                 actual_compiler_batches=1,compiled_tus=2,compiler_exit_code=0,compile_seconds=seconds,compiler_warnings=0,
                 native_fixture_exit_code=0,native_seconds=native_seconds,state_comparisons=15744,case_groups=result,
                 oracles=oracles,input_sha256=pins,before_after_guards=True,command=list(map(str,command)),resumed_existing_compile=finalize,
                 unique_execution_receipts=['compile-001','link-001','native-001'],limits=proof['limits'])
    write(RUN/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['synthetic_bytes','synthetic_instructions','state_comparisons','compile_seconds','native_seconds','new_accepted_functions']}))


if __name__=='__main__':main()

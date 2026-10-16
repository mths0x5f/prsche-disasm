"""Bounded, isolated extension of Run246: direct tail transfer and MissingEntry.

Original machine code is executed only by the independent comparison fixture.
No ordinary or support union packet is produced.
"""
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/253-x86-tail-dispatch'
OUT = ROOT/'local/experiments/v2-x86-tail-dispatch-253'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS = ('00468100','004d8230','004d8240')
CONTRACTS = {
    '00468100': dict(bytes=8, displacement=0x74, target='00536050'),
    '004d8230': dict(bytes=11, displacement=0x264, target='004c7e10'),
    '004d8240': dict(bytes=11, displacement=0x264, target='004c7df0'),
}
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_bytes())
relative = lambda p: Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


def backend():
    """Exact inherited lowering plus explicit, finite direct-JMP transformations."""
    base=module('frozen246_for253','scripts/research/experiment-v2-x86-cpp-246.py')
    text=inspect.getsource(base.translate)
    patches=[
        ("        elif m=='ret'", "        elif m=='jmp' and len(ops)==1 and ops[0].type==X86_OP_IMM:\n"
         "            target=ops[0].imm&0xffffffff\n"
         "            if entry<=target<entry+len(raw):\n"
         "                if target not in starts:raise ValueError('JMP target is not an instruction boundary')\n"
         "                code=f'goto L_{target:08x};'\n"
         "            else:code=f'dispatch246(s,0x{target:08x}u);return;'\n"
         "        elif m=='ret'"),
        ("['jl','jge','je','jz']}", "['jl','jge','je','jz','jmp'] and x.operands[0].type==X86_OP_IMM}"),
        ("instructions[-1].mnemonic!='ret'", "instructions[-1].mnemonic not in ['ret','jmp']"),
        ("s.r[4]+={4+pop}u;return;", "s.r[4]+={4+pop}u;s.stop=Stop246::Returned;return;"),
    ]
    for before,after in patches:
        assert text.count(before)==1,('frozen backend patch context drift',before)
        text=text.replace(before,after)
    text=text.replace('246','253')
    namespace={k:getattr(base,k) for k in ['capstone','REG','X86_OP_IMM','X86_OP_MEM','X86_OP_REG']}
    exec(compile(text,'derived-backend253.py','exec'),namespace)
    return namespace['translate'],text,patches


def header():
    # Keep finite-width flag helpers identical to246; replace only fixture memory map/state.
    base=module('header246_for253','scripts/research/experiment-v2-x86-cpp-246.py').HEADER
    flags=base[base.index('// Defined CF/ZF/SF/OF only.'):base.index('void translated_00590290')].replace('246','253')
    return '''#pragma once
using U=unsigned int; using U64=unsigned long long; using B=unsigned char;
static_assert(sizeof(U)==4 && sizeof(void*)==4,"x86 native fixture only");
enum class Stop253:U {Running,Returned,MissingEntry};
struct Machine253 {U r[8];U flags;U pc;Stop253 stop;};
extern "C" void* __cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
// Only controlled, valid native32 fixture memory, including unaligned DWORD reads.
static __forceinline U read253(U a,U n){U v=0;memcpy(&v,reinterpret_cast<const B*>(a),n);return v;}
static __forceinline void write253(U a,U n,U v){memcpy(reinterpret_cast<B*>(a),&v,n);}
void dispatch253(Machine253&,U);
void note_missing253(U);
''' + flags + ''.join('void translated_'+va+'(Machine253&);\n' for va in VAS)


DISPATCH = '''#include "machine253.h"
// This dispatch table contains exactly the three generated wrappers, never their callees.
void dispatch253(Machine253&s,U target){
 s.pc=target;
 switch(target){
 case 0x00468100u:translated_00468100(s);return;
 case 0x004d8230u:translated_004d8230(s);return;
 case 0x004d8240u:translated_004d8240(s);return;
 default:s.stop=Stop253::MissingEntry;note_missing253(target);return;
 }
}
'''


FIXTURE = r'''#include "machine253.h"
extern "C" __declspec(dllimport) void __stdcall ExitProcess(U);
extern "C" __declspec(dllimport) void* __stdcall CreateFileA(const char*,U,U,void*,U,U,void*);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,U,U*,void*);
extern "C" __declspec(dllimport) int __stdcall CloseHandle(void*);
U saved_sp253,saved_bp253,saved_bx253,saved_si253,saved_di253;
U seen253[8],seen_flags253,seed253[8],seed_flags253,target253,continuation253;
U failures253,cases253,missing253[3],missing_count253,missing_events253;
B arena253[768],before253[768];
void note_missing253(U pc){
 ++missing_events253;
 for(U i=0;i<missing_count253;++i)if(missing253[i]==pc)return;
 if(missing_count253==3u){++failures253;return;}
 missing253[missing_count253++]=pc;
}
// The hook observes the state at the tail-transfer cutpoint. It has no RET and
// does not implement any original callee. Its private stack traffic is fixture-only.
__declspec(naked) void capture253(){__asm{
 mov seen253[0],eax
 mov seen253[4],ecx
 mov seen253[8],edx
 mov seen253[12],ebx
 mov seen253[16],esp
 mov seen253[20],ebp
 mov seen253[24],esi
 mov seen253[28],edi
 pushfd
 pop seen_flags253
 mov ebx,saved_bx253
 mov esi,saved_si253
 mov edi,saved_di253
 mov ebp,saved_bp253
 mov esp,saved_sp253
 jmp dword ptr continuation253
}}
__declspec(naked) void original_00468100_253(){__asm{
 mov ecx,dword ptr[ecx+0x74]
 jmp capture253
}}
__declspec(naked) void original_004d8230_253(){__asm{
 mov ecx,dword ptr[ecx+0x264]
 jmp capture253
}}
__declspec(naked) void original_004d8240_253(){__asm{
 mov ecx,dword ptr[ecx+0x264]
 jmp capture253
}}
// The CALL/RET below belong only to fixture transport, not to the original
// wrapper or the capture hook. The original tail JMP itself consumes no stack.
__declspec(naked) void original_edge253(){__asm{
 mov saved_sp253,esp
 mov saved_bp253,ebp
 mov saved_bx253,ebx
 mov saved_si253,esi
 mov saved_di253,edi
 mov eax,offset resume253
 mov continuation253,eax
 push seed_flags253
 popfd
 mov eax,seed253[0]
 mov ecx,seed253[4]
 mov edx,seed253[8]
 mov ebx,seed253[12]
 mov ebp,seed253[20]
 mov esi,seed253[24]
 mov edi,seed253[28]
 jmp dword ptr target253
resume253:
 ret
}}
void require253(bool value){if(!value)++failures253;}
void hex253(char*&p,U value){const char*digits="0123456789abcdef";for(U n=8;n;--n)*p++=digits[(value>>((n-1u)*4u))&15u];}
void text253(char*&p,const char*s){while(*s)*p++=*s++;}
void runtime_report253(){
 char text[1024];char*p=text;
 text253(p,"{\n  \"original_sha256\": \"ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39\",\n  \"module\": \"Porsche.exe\",\n  \"provenance\": \"isolatedVMpilot\",\n  \"native_game_execution\": false,\n  \"scope\": \"three-tail-wrappers\",\n  \"missing_entry_vas\": [");
 for(U i=0;i<missing_count253;++i){if(i)text253(p,", ");*p++='"';hex253(p,missing253[i]);*p++='"';}
 text253(p,"]\n}\n");
 void*h=CreateFileA("runtime-misses.json",0x40000000u,0,0,2,0x80,0);U written=0;
 require253(h!=reinterpret_cast<void*>(0xffffffffu));
 if(h!=reinterpret_cast<void*>(0xffffffffu)){require253(WriteFile(h,text,static_cast<U>(p-text),&written,0)!=0);require253(written==static_cast<U>(p-text));require253(CloseHandle(h)!=0);}
}
extern "C" void __cdecl entry(){
 void*originals[3]={reinterpret_cast<void*>(&original_00468100_253),reinterpret_cast<void*>(&original_004d8230_253),reinterpret_cast<void*>(&original_004d8240_253)};
 U entries[3]={0x00468100u,0x004d8230u,0x004d8240u};
 U offsets[3]={0x74u,0x264u,0x264u};U targets[3]={0x00536050u,0x004c7e10u,0x004c7df0u};
 U values[6]={0,1,0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu};
 for(U wrapper=0;wrapper<3;++wrapper)for(U align=0;align<8;++align)
 for(U value=0;value<6;++value)for(U flags=0;flags<16;++flags)for(U seed=0;seed<8;++seed){
  for(U i=0;i<768;++i)arena253[i]=static_cast<B>(i*37u+seed*59u+value);
  U receiver=reinterpret_cast<U>(arena253+align);write253(receiver+offsets[wrapper],4,values[value]);
  for(U i=0;i<768;++i)before253[i]=arena253[i];
  for(U i=0;i<8;++i)seed253[i]=(0x13579bdfu*(i+1u))^(0x80000001u*seed);
  seed253[1]=receiver;seed_flags253=0x202u|(flags&1u)|((flags&2u)<<5u)|((flags&4u)<<5u)|((flags&8u)<<8u);
  target253=reinterpret_cast<U>(originals[wrapper]);original_edge253();
  seed253[4]=saved_sp253;
  for(U i=0;i<8;++i)require253(seen253[i]==(i==1?values[value]:seed253[i]));
  require253(((seen_flags253^seed_flags253)&0x8c1u)==0);
  for(U i=0;i<768;++i)require253(arena253[i]==before253[i]);
  Machine253 state={};for(U i=0;i<8;++i)state.r[i]=seed253[i];
  state.flags=seed_flags253;state.pc=entries[wrapper];state.stop=Stop253::Running;
  dispatch253(state,entries[wrapper]);
  for(U i=0;i<8;++i)require253(state.r[i]==seen253[i]);
  require253(state.flags==seed_flags253 && ((state.flags^seen_flags253)&0x8c1u)==0);
  require253(state.pc==targets[wrapper] && state.stop==Stop253::MissingEntry);
  for(U i=0;i<768;++i)require253(arena253[i]==before253[i]);
  ++cases253;
 }
 require253(cases253==18432u && missing_events253==cases253 && missing_count253==3u);
 for(U i=0;i<3;++i)require253(missing253[i]==targets[i]);
 runtime_report253();ExitProcess(failures253?1u:0u);
}
'''


def guard_tests(translate):
    rejected=[]
    for data,why in [(b'\xcc','unsupported INT3'),(b'\x8b','truncated instruction'),
                     (b'\xff\xe0','indirect JMP'),(b'\xeb\xff','JMP into instruction'),
                     (b'\xe8\x00\x00\x00\x00\xc3','CALL'),(b'\xd9\xe8\xc3','x87')]:
        try:translate(data,0x1000)
        except ValueError:rejected.append(why)
        else:raise AssertionError(('unsupported accepted',why))
    text,_=translate(b'\xeb\x00\xc3',0x1000)
    assert 'goto L_00001002;' in text and 'L_00001002:' in text
    text,_=translate(b'\xe9\x0b\x00\x00\x00',0x1000)
    assert 'dispatch253(s,0x00001010u);return;' in text and 'read253' not in text
    return rejected+['internal direct JMP boundary accepted','external direct JMP explicit dispatcher accepted']


def main():
    resume='--finalize-existing' in sys.argv
    assert not (RUN/'summary.json').exists(),'completed253 immutable'
    if resume:assert (OUT/'compile.execution.json').exists()
    else:assert not OUT.exists() or not any(OUT.iterdir()),'fresh253 paths required'
    RUN.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('hash',path);pins[relative(path)]=h;return path
    def guard():
        for p,h in pins.items():assert digest(ROOT/p)==h,('input drift',p)
    def materialize(path,text):
        data=text.encode('utf8')
        if resume:assert path.read_bytes()==data,('compiled source drift',path)
        else:path.write_bytes(data)
        pin(path)
    abi=module('abi253','scripts/research/experiment-v2-thiscall-186.py')
    oracle=module('oracle253','scripts/research/audit-v2-nested-calls-229.py')
    pe_reader=module('pe253','scripts/research/audit-v2-x86-cpp-246.py')
    translate,derived,patches=backend();tests=guard_tests(translate)
    for p in [__file__,ROOT/'scripts/research/experiment-v2-x86-cpp-246.py',ROOT/'scripts/research/audit-v2-x86-cpp-246.py',
              ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/audit-v2-nested-calls-229.py',
              ROOT/'research/binary-index/README.md',ROOT/'research/binary-index/manual-functions.jsonl',
              abi.CORPUS/'functions.jsonl',abi.CORPUS/'disassembly.asm',abi.COMPILER,abi.DUMPBIN,
              ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json',
              ROOT/'iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot/summary.json',
              ROOT/'iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot/validation.json',
              ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json',
              ROOT/'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/validation.json',
              ROOT/'scripts/research/plan-v2-link-frontier-245.py',
              ROOT/'iterations/v2/001-original-recovery/runs/245-automated-frontier-queue/summary.json']:
        pin(p)
    import capstone
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    catalog={r['entry_va']:r for r in abi.rows(abi.CORPUS/'functions.jsonl')}
    index=abi.instruction_index();image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes()
    registry=load(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json')['functions']
    accepted={va:[r for r in registry if r.get('module')=='Porsche.exe' and r['entry_va']==va] for va in VAS}
    assert not any(accepted.values()),'selected wrapper already accepted'
    # Exact-definition census only; occurrence-only hits are navigation, not ownership.
    source_root=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'
    ownership={va:[] for va in VAS};interior={va:[] for va in VAS}
    for path in sorted(source_root.glob('*')):
        if path.suffix not in ['.cpp','.hpp','.inc']:continue
        text=path.read_text(encoding='utf8')
        for va in VAS:
            matches=list(re.finditer(r'\b[A-Za-z_]\w*_'+va+r'\s*\([^;{}]*\)\s*(?:noexcept\s*)?\{',text))
            if matches:
                pin(path);ownership[va]+=[dict(source=relative(path),line=text.count('\n',0,m.start())+1) for m in matches]
    assert not any(ownership.values()),('WIP definition',ownership)
    for va in VAS:
        for r in registry:
            if r.get('module')!='Porsche.exe':continue
            row=catalog.get(r['entry_va'])
            if row and any(int(a,16)<int(va,16)<=int(b,16) for a,b in row.get('ranges',[])):
                interior[va].append(r['entry_va'])
    assert not any(interior.values()),('accepted interior overlap',interior)
    materialize(OUT/'derived-backend253.py',derived);materialize(OUT/'machine253.h',header())
    materialize(OUT/'dispatch253.cpp',DISPATCH);materialize(OUT/'state-fixture.cpp',FIXTURE)
    originals={};witnesses={};sources=[]
    for va in VAS:
        contract=CONTRACTS[va];raw=pe_reader.original_bytes(image,va,contract['bytes'])
        ins=abi.function_instructions(catalog[va],index)
        assert len(ins)==2 and bytes.fromhex(''.join(i['bytes'] for i in ins))==raw
        text,witness=translate(raw,int(va,16))
        assert witness[0]['mnemonic']=='mov' and witness[1]['mnemonic']=='jmp'
        assert witness[0]['operands']==f'ecx, dword ptr [ecx + 0x{contract["displacement"]:x}]'
        assert int(witness[1]['operands'],16)==int(contract['target'],16)
        assert 'read253' in witness[0]['cpp'] and 'dispatch253' in witness[1]['cpp']
        assert 'Stop253::Returned' not in text and 's.r[4]+=' not in text
        source=OUT/(va+'.cpp');materialize(source,text);sources.append(source)
        originals[va]=raw.hex();witnesses[va]=witness
    proof=dict(original_sha256=SHA,contracts=CONTRACTS,original_hex=originals,instruction_lowering=witnesses,
               backend_patches=patches,backend_derived=relative(OUT/'derived-backend253.py'),guard_tests=tests,
               accepted_exact_owners=accepted,wip_exact_definitions=ownership,accepted_interior_owners=interior,
               body_scope='Three MOV ECX,[ECX+disp32/disp8];direct JMP wrappers only. No original callee implementation.',
               state_scope='All8 GPRs including unchanged raw ESP; CF/ZF/SF/OF, unchanged VM flags,768-byte controlled arena,0..7 unaligned receivers and high-bit DWORD values.',
               limits=['Isolated native32 VM fixture; no game EXE execution, full memory loader, CALL, x87 or complete translator.',
                       'Only terminal JMP REL32 is rebound to the capture hook; MOV prefix is exact original PE bytes.',
                       'Capture hook private globals/stack writes are fixture transport after the cutpoint, not original effects.',
                       'MissingEntry targets are isolated VM dispatch misses, not missing native bodies in the main queue.',
                       'No restored typed ABI binding: original lost receiver contracts remain deferred.'])
    if resume:assert load(RUN/'proof-before-compile.json')==proof,'precompile proof drift'
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir(exist_ok=resume)
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter()
        p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120)
        seconds=time.perf_counter()-start
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
        return p,log,seconds
    command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/MP6',
             '/Fo'+str(objects)+os.sep,*sources,OUT/'dispatch253.cpp',OUT/'state-fixture.cpp']
    if resume:
        execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['command']==list(map(str,command))
        compile_seconds=execution['elapsed_seconds'];clog=OUT/'compile.log'
    else:
        (OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes())
        p,clog,compile_seconds=run(command,'compile');assert p.returncode==0,clog.read_text(encoding='utf8')
    pin(OUT/'captured-compile-driver.py')
    warnings=re.findall(r'(?m)^.*warning [CD]\d+.*$',clog.read_text(encoding='utf8'))
    assert not re.search(r'\berror [CD]\d+',clog.read_text(encoding='utf8'))
    assert warnings==[],warnings
    oracles=[]
    for va in VAS:
        body,relocs=oracle.coff_function(objects/'state-fixture.obj',f'?original_{va}_253@@YAXXZ')
        expected=bytearray.fromhex(originals[va]);offset=len(expected)-4
        assert relocs==[dict(offset=offset,symbol='?capture253@@YAXXZ',type=20)]
        expected[offset:offset+4]=bytes(4)
        assert body==expected,(va,body.hex(),expected.hex())
        oracles.append(dict(va=va,bytes=len(body),relocations=relocs,normalized_only_jmp_rel32=True))
    link=pin(abi.COMPILER.with_name('link.exe'))
    libraries=[pin(abi.COMPILER.parents[3]/'lib/x86'/n) for n in ['libcmt.lib','libvcruntime.lib']]
    sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
    libraries+=[pin(sdk/'ucrt/x86/libucrt.lib'),pin(sdk/'um/x86/kernel32.lib')]
    exe=OUT/'state-fixture.exe'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),
                  *[objects/(va+'.obj') for va in VAS],objects/'dispatch253.obj',objects/'state-fixture.obj',*libraries],'fixture-link')
    assert p.returncode==0,llog.read_bytes()
    p,_,native_seconds=run([exe],'fixture-native');assert p.returncode==0,('native cutpoint comparisons',p.returncode)
    misses=load(pin(OUT/'runtime-misses.json'))
    assert misses['provenance']=='isolatedVMpilot' and misses['native_game_execution'] is False
    assert misses['original_sha256']==SHA and misses['module']=='Porsche.exe'
    assert misses['missing_entry_vas']==[CONTRACTS[va]['target'] for va in VAS]
    planner=module('parser245_for253','scripts/research/plan-v2-link-frontier-245.py')
    parsed=planner.runtime_input(misses,catalog)
    try:planner.runtime_input({**misses,'original_sha256':'0'*64},catalog)
    except (AssertionError,ValueError):wrong_sha_rejected=True
    else:raise AssertionError('wrong runtime module SHA accepted')
    assert set(parsed['vas'])==set(misses['missing_entry_vas']) and parsed['execution_claimed'] is False
    parser_proof=dict(parser_only=True,planner_cli_executions=0,queue_unchanged=True,input_provenance=misses['provenance'],
                      native_game_execution=False,output=parsed,wrong_sha_rejected=wrong_sha_rejected)
    write(RUN/'runtime-parser-identity.json',parser_proof);pin(RUN/'runtime-parser-identity.json')
    for p in [*objects.glob('*.obj'),exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    summary=dict(schema=1,kind='isolated-x86-tail-dispatch-pilot',original_sha256=SHA,experimental_vas=list(VAS),
                 translated_original_bytes=30,translated_original_instructions=6,new_accepted_functions=0,
                 production_or_union_changed=False,native_game_execution_commands=0,planner_cli_executions=0,
                 actual_compiler_batches=1,compiler_exit_code=0,compile_seconds=compile_seconds,compile_warnings=warnings,
                 native_fixture_exit_code=0,native_seconds=native_seconds,state_comparisons=18432,
                 missing_entry_vas=misses['missing_entry_vas'],missing_entry_events=18432,runtime_misses=relative(OUT/'runtime-misses.json'),
                 runtime_misses_provenance='isolatedVMpilot',oracle=oracles,guard_tests=tests,input_sha256=pins,
                 before_after_guards=True,command=list(map(str,command)),resumed_existing_compile=resume,limits=proof['limits'])
    write(RUN/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ['translated_original_bytes','translated_original_instructions','state_comparisons','compile_seconds','native_seconds','new_accepted_functions']}))


if __name__=='__main__':main()

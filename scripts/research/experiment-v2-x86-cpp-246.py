"""Isolated static x86 -> C++ pilot; existing owners are not replaced or recounted."""
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

import capstone
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'iterations/v2/001-original-recovery/runs/246-x86-cpp-pilot'
OUT = ROOT/'local/experiments/v2-x86-cpp-pilot-246'
VAS = ['00590290', '004930f0', '00590070']
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
REG = {name:i for i,name in enumerate(['eax','ecx','edx','ebx','esp','ebp','esi','edi'])}
digest = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative = lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load = lambda p:json.loads(Path(p).read_bytes())


def module(name, path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


HEADER = '''#pragma once
using U=unsigned int; using U64=unsigned long long; using B=unsigned char;
static_assert(sizeof(U)==4 && sizeof(void*)==4,"x86 native fixture only");
struct Machine246 {U r[8];U flags;U pc;};
extern U count246,table246;
extern "C" void* __cdecl memcpy(void*,const void*,unsigned int);
#pragma intrinsic(memcpy)
// Only two original absolute global operands are mapped to controlled fixture cells.
// Other addresses are valid native32 fixture memory. This is not a game memory loader.
static __forceinline B* address246(U a){
 if(a==0x006b48d8u)return reinterpret_cast<B*>(&count246);
 if(a==0x006b4a04u)return reinterpret_cast<B*>(&table246);
 return reinterpret_cast<B*>(a);
}
static __forceinline U read246(U a,U n){U v=0;memcpy(&v,address246(a),n);return v;}
static __forceinline void write246(U a,U n,U v){memcpy(address246(a),&v,n);}
// Defined CF/ZF/SF/OF only. PF/AF and undefined flags are deliberately outside this pilot.
static __forceinline void flags246(Machine246&s,U v,U bits,U cf,U of){
 U mask=bits==8?0xffu:0xffffffffu;v&=mask;
 s.flags=(s.flags&~0x8c1u)|(cf?1u:0u)|(v==0?0x40u:0u)|
   ((v>>(bits-1))?0x80u:0u)|(of?0x800u:0u);
}
static __forceinline U logical246(Machine246&s,U v,U bits){flags246(s,v,bits,0,0);return v;}
static __forceinline U subtract246(Machine246&s,U a,U b,U carry,U bits){
 U mask=bits==8?0xffu:0xffffffffu;a&=mask;b&=mask;
 U v=static_cast<U>(static_cast<U64>(a)-static_cast<U64>(b)-carry)&mask;
 flags246(s,v,bits,static_cast<U64>(a)<static_cast<U64>(b)+carry,
   (((a^b)&(a^v))>>(bits-1))&1u);return v;
}
void translated_00590290(Machine246&);
void translated_004930f0(Machine246&);
void translated_00590070(Machine246&);
'''


def translate(raw,entry):
    decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
    instructions=list(decoder.disasm(raw,entry))
    if sum(i.size for i in instructions)!=len(raw):raise ValueError('Undecoded bytes')
    starts={i.address for i in instructions}
    def address(i,op):
        m=op.mem
        if m.segment:raise ValueError('Segment override unsupported')
        terms=[f'0x{m.disp&0xffffffff:08x}u']
        for register,scale in [(m.base,1),(m.index,m.scale)]:
            if register:
                name=i.reg_name(register)
                if name not in REG:raise ValueError('Unsupported address register '+name)
                terms.append(f's.r[{REG[name]}]*{scale}u')
        return '('+'+'.join(terms)+')'
    def expression(i,op):
        if op.type==X86_OP_IMM:return f'0x{op.imm&0xffffffff:08x}u'
        if op.type==X86_OP_REG:
            name=i.reg_name(op.reg)
            if name in REG and op.size==4:return f's.r[{REG[name]}]'
            if name=='al' and op.size==1:return '(s.r[0]&0xffu)'
            raise ValueError('Unsupported register '+name)
        if op.type==X86_OP_MEM and op.size in [1,4]:return f'read246({address(i,op)},{op.size}u)'
        raise ValueError('Unsupported operand')
    def store(i,op,value):
        if op.type==X86_OP_REG:
            name=i.reg_name(op.reg)
            if name in REG and op.size==4:return f's.r[{REG[name]}]={value};'
            if name=='al' and op.size==1:return f's.r[0]=(s.r[0]&0xffffff00u)|(({value})&0xffu);'
        if op.type==X86_OP_MEM and op.size in [1,4]:return f'write246({address(i,op)},{op.size}u,{value});'
        raise ValueError('Unsupported destination')
    lines=['#include "machine246.h"',f'void translated_{entry:08x}(Machine246&s){{']
    witnesses=[]
    for i in instructions:
        ops=i.operands;m=i.mnemonic
        if m=='mov' and len(ops)==2:code=store(i,ops[0],expression(i,ops[1]))
        elif m=='lea' and len(ops)==2 and ops[1].type==X86_OP_MEM:code=store(i,ops[0],address(i,ops[1]))
        elif m in ['xor','and','test','cmp','sbb'] and len(ops)==2:
            a,b=expression(i,ops[0]),expression(i,ops[1]);bits=ops[0].size*8
            if bits not in [8,32]:raise ValueError('Unsupported arithmetic width')
            if m in ['xor','and','test']:
                value=f'logical246(s,({a})'+('^' if m=='xor' else '&')+f'({b}),{bits}u)'
            else:value=f'subtract246(s,{a},{b},'+('(s.flags&1u)' if m=='sbb' else '0u')+f',{bits}u)'
            code=value+';' if m in ['test','cmp'] else store(i,ops[0],value)
        elif m=='neg' and len(ops)==1:
            code=store(i,ops[0],f'subtract246(s,0u,{expression(i,ops[0])},0u,{ops[0].size*8}u)')
        elif m in ['jl','jge','je','jz'] and len(ops)==1 and ops[0].type==X86_OP_IMM:
            if ops[0].imm not in starts:raise ValueError('Branch target is not an instruction boundary')
            condition='((s.flags>>7)^(s.flags>>11))&1u'
            if m=='jge':condition='!('+condition+')'
            elif m in ['je','jz']:condition='s.flags&0x40u'
            code=f'if({condition})goto L_{ops[0].imm:08x};'
        elif m=='ret' and (not ops or (len(ops)==1 and ops[0].type==X86_OP_IMM)):
            pop=ops[0].imm if ops else 0
            if pop<0 or pop>65535:raise ValueError('Invalid RET immediate')
            code=f's.pc=read246(s.r[4],4u);s.r[4]+={4+pop}u;return;'
        else:raise ValueError(f'Unsupported opcode {i.address:08x}: {m} {i.op_str}')
        # Labels are emitted only at actual direct branch destinations, avoiding unused-label warnings.
        targets={x.operands[0].imm for x in instructions if x.mnemonic in ['jl','jge','je','jz']}
        if i.address in targets:lines.append(f'L_{i.address:08x}:')
        lines.append(f' // {i.address:08x} {i.bytes.hex()} {m} {i.op_str}\n {code}')
        witnesses.append(dict(va=f'{i.address:08x}',bytes=i.bytes.hex(),mnemonic=m,operands=i.op_str,cpp=code))
    if not instructions or instructions[-1].mnemonic!='ret':raise ValueError('Open fallthrough unsupported')
    lines.append('}\n');return '\n'.join(lines),witnesses


FIXTURE = '''#include "machine246.h"
extern "C" __declspec(dllimport) void __stdcall ExitProcess(U);
U count246=0,table246=0;
U saved_sp246,saved_bp246,saved_bx246,saved_si246,saved_di246;
U entry_sp246,seen246[8],seen_flags246,failures246,cases246;
B table_memory246[65536*12+4]={};
__declspec(naked) void original_00590290_246(){__asm{xor eax,eax
 ret}}
__declspec(naked) void original_004930f0_246(){__asm{
 mov edx,dword ptr[ecx]
 mov eax,dword ptr[edx]
 mov dword ptr[ecx],eax
 mov eax,dword ptr[esp+4]
 mov dword ptr[eax],edx
 ret 8
}}
__declspec(naked) void original_00590070_246(){__asm{
 mov eax,dword ptr[esp+4]
 test eax,eax
 jl rejected246
 mov ecx,count246
 and ecx,0xffff
 cmp eax,ecx
 jge rejected246
 lea edx,[eax+eax*2]
 mov eax,table246
 mov ecx,dword ptr[eax+edx*4]
 lea eax,[eax+edx*4]
 test ecx,ecx
 jz rejected246
 mov al,byte ptr[eax+8]
 neg al
 sbb eax,eax
 and al,0xee
 ret
rejected246:
 mov eax,0xfffffff8
 ret
}}
__declspec(noinline) void original_edge246(void*target,U arg1,U arg2,U receiver,U seed_a,U seed_d,U flags){__asm{
 mov saved_sp246,esp
 mov saved_bp246,ebp
 mov saved_bx246,ebx
 mov saved_si246,esi
 mov saved_di246,edi
 push arg2
 push arg1
 lea eax,[esp-4]
 mov entry_sp246,eax
 push flags
 popfd
 mov eax,seed_a
 mov ecx,receiver
 mov edx,seed_d
 mov ebx,0x176b92d3
 mov esi,0xa53c0481
 mov edi,0x59e0b72f
 call target
 mov seen246[0],eax
 mov seen246[4],ecx
 mov seen246[8],edx
 mov seen246[12],ebx
 mov seen246[16],esp
 mov seen246[20],ebp
 mov seen246[24],esi
 mov seen246[28],edi
 pushfd
 pop seen_flags246
 mov ebx,saved_bx246
 mov esi,saved_si246
 mov edi,saved_di246
 mov esp,saved_sp246
}}
Machine246 initial246(U*stack,U receiver,U a,U d,U flags){
 Machine246 s={{a,receiver,d,0x176b92d3u,reinterpret_cast<U>(stack),saved_bp246,0xa53c0481u,0x59e0b72fu},flags,0};return s;
}
void compare246(Machine246&s,U*stack,U pop){
 for(U i=0;i<8;++i)if(i!=4&&s.r[i]!=seen246[i])++failures246;
 if((s.flags&0x8c1u)!=(seen_flags246&0x8c1u))++failures246;
 if(s.r[4]-reinterpret_cast<U>(stack)!=4u+pop||seen246[4]-entry_sp246!=4u+pop)++failures246;
 if(s.pc!=stack[0])++failures246;++cases246;
}
void no_memory246(U kind,U a1,U receiver,U a,U d,U flags){
 U stack[3]={0x13579bdfu,a1,0xc0a57f21u};
 if(kind==0)original_edge246(reinterpret_cast<void*>(&original_00590290_246),a1,stack[2],receiver,a,d,flags);
 else original_edge246(reinterpret_cast<void*>(&original_00590070_246),a1,stack[2],receiver,a,d,flags);
 Machine246 s=initial246(stack,receiver,a,d,flags);
 if(kind==0)translated_00590290(s);else translated_00590070(s);
 compare246(s,stack,0);
}
extern "C" void __cdecl entry(){
 U state=0x2463719u;
 for(U i=0;i<1024;++i){state=state*1664525u+1013904223u;no_memory246(0,state,state^0xaabbccddu,state,state^0x12345678u,0x202u|(state&0x8c1u));}
 const U nexts[6]={0,1,0x7fffffffu,0x80000000u,0x80000001u,0xffffffffu};
 for(U h=0;h<4;++h)for(U n=0;n<4;++n)for(U o=0;o<4;++o)for(U v=0;v<6;++v)for(U f=0;f<16;++f){
  B memory[64],before[64],expected[64];for(U i=0;i<64;++i)memory[i]=static_cast<B>(i^0xa5u);
  U head=reinterpret_cast<U>(memory+h),node=reinterpret_cast<U>(memory+16+n),out=reinterpret_cast<U>(memory+32+o);
  write246(head,4,node);write246(node,4,nexts[v]);memcpy(before,memory,64);
  U flags=0x202u|((f&1u)?1u:0u)|((f&2u)?0x40u:0u)|((f&4u)?0x80u:0u)|((f&8u)?0x800u:0u);
  original_edge246(reinterpret_cast<void*>(&original_004930f0_246),out,0xc0a57f21u,head,0x12345678u,0x87654321u,flags);
  memcpy(expected,memory,64);memcpy(memory,before,64);
  U stack[3]={0x13579bdfu,out,0xc0a57f21u};Machine246 s=initial246(stack,head,0x12345678u,0x87654321u,flags);
  translated_004930f0(s);compare246(s,stack,8);
  for(U i=0;i<64;++i)if(memory[i]!=expected[i])++failures246;
 }
 const U indexes[10]={0xffffffffu,0,1,2,255,32767,65534,65535,0x7fffffffu,0x80000000u};
 const U counts[6]={0,1,2,256,32768,65535};const U highs[3]={0,0x12340000u,0xffff0000u};
 for(U ix=0;ix<10;++ix)for(U co=0;co<6;++co)for(U hi=0;hi<3;++hi)for(U present=0;present<2;++present)
 for(U status=0;status<256;++status)for(U align=0;align<4;++align){
  B*base=table_memory246+align;table246=reinterpret_cast<U>(base);count246=highs[hi]|counts[co];
  if(indexes[ix]<65535u){U cell=reinterpret_cast<U>(base)+indexes[ix]*12u;write246(cell,4,present?0x87654321u:0u);write246(cell+8u,1,status);}
  no_memory246(1,indexes[ix],0x2468ace0u^status,0x13579bdfu^status,0xa5a55a5au^indexes[ix],0xa43u);
 }
 if(cases246!=375808u)++failures246;ExitProcess(failures246?1:0);
}
'''


def main():
    resume='--finalize-existing' in sys.argv
    assert not (RUN/'summary.json').exists(),'completed246 immutable'
    if resume:assert (OUT/'compile.execution.json').exists()
    else:assert not OUT.exists() or not any(OUT.iterdir()),'fresh246 paths required'
    OUT.mkdir(exist_ok=True);RUN.mkdir(parents=True,exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,path;pins[relative(path)]=h;return path
    def guard():
        for p,h in pins.items():assert digest(ROOT/p)==h,('input drift',p)
    def materialize(path,text):
        if resume:assert path.read_bytes()==text.encode('utf8'),('compiled source drift',path)
        else:path.write_text(text,encoding='utf8',newline='\n')
    abi=module('abi246','scripts/research/experiment-v2-thiscall-186.py')
    parse=module('parse246','scripts/research/audit-v2-nested-calls-229.py')
    coff=module('coff246','scripts/research/build-v2-compile-corpus.py')
    for p in [__file__,ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/audit-v2-nested-calls-229.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN,
              ROOT/'research/binary-index/README.md',ROOT/'research/binary-index/manual-functions.jsonl',ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json']:
        pin(p)
    pin(Path(capstone.__file__));pin(Path(capstone.__file__).parent/'lib/capstone.dll')
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))};pin(abi.CORPUS/'disassembly.asm');index=abi.instruction_index()
    baseline=load(pin(ROOT/'iterations/v2/001-original-recovery/runs/243-canonical-reuse-union/summary.json'))
    owners={r['va']:r for r in baseline['results']if r['va']in VAS};assert set(owners)==set(VAS)
    for row in owners.values():pin(ROOT/row['object'],row['object_sha256']);pin(ROOT/row['generated_source'],row['generated_source_sha256'])
    raw=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();pe=struct.unpack_from('<I',raw,0x3c)[0]
    _,count,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',raw,pe+4);base=struct.unpack_from('<I',raw,pe+24+28)[0]
    sections=[struct.unpack_from('<IIII',raw,pe+24+opt+i*40+8)[1:]for i in range(count)]
    originals={};witnesses={};sources=[];header=OUT/'machine246.h';materialize(header,HEADER);pin(header)
    for va in VAS:
        entry=catalog[va];assert len(entry['ranges'])==1
        ins=abi.function_instructions(entry,index);data=bytes.fromhex(''.join(i['bytes']for i in ins));rva=int(va,16)-base
        start,size,offset=next(s for s in sections if s[0]<=rva and rva+len(data)<=s[0]+s[1]);assert raw[offset+rva-start:offset+rva-start+len(data)]==data
        text,witness=translate(data,int(va,16));assert [(w['va'],w['bytes'])for w in witness]==[(i['va'],i['bytes'])for i in ins]
        source=OUT/(va+'.cpp');materialize(source,text);pin(source);sources.append(source);originals[va]=data.hex();witnesses[va]=witness
    rejected=[]
    for data,why in [(b'\xcc','unsupported INT3'),(b'\x8b','truncated instruction'),(b'\x74\x01\xc3','branch into missing instruction boundary')]:
        try:translate(data,0x1000);raise AssertionError('Unsupported input silently accepted')
        except ValueError:rejected.append(why)
    fixture=OUT/'state-fixture.cpp';materialize(fixture,FIXTURE);pin(fixture)
    proof=dict(original_sha256=SHA,existing_owners=owners,original_hex=originals,instruction_lowering=witnesses,
        index_query='00590290,004930f0,00590070 -> exact PE bodies, existing197/217/229 owners; experimental regression only',
        rejected_inputs=rejected,mode='Ahead-of-time per-instruction C++ statements/direct gotos; no runtime instruction decoder or original-game machine-code fallback.',
        state_scope='EAX/ECX/EDX/EBX/EBP/ESI/EDI, relative ESP/RET0/RET8, defined CF/ZF/SF/OF, 64-byte memory arena effects, controlled raw32 globals.',
        limits=['Call-free subset only; unsupported instructions/operands/branches reject before any native compilation.',
            'No PF/AF/undefined flags, x87/SSE, CALL/import/callback/exception/concurrency or full guest memory loader.',
            'Original x86 executes only in the comparison fixture. Existing restored owners/production/union unchanged; zero new accepted functions.',
            'A pilot pass is not full CPU equivalence, game launch or evidence of a complete x86 translator.'])
    if resume:assert load(RUN/'proof-before-compile.json')==proof,'precompile proof drift'
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects';objects.mkdir(exist_ok=resume);env={**os.environ,'VSLANG':'1033','CL':'','_CL_':''}
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);seconds=time.perf_counter()-start
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'));return p,log,seconds
    command=[abi.COMPILER,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/TP','/GS-','/GR-','/W4','/utf-8','/MP6','/Fo'+str(objects)+os.sep,*sources,fixture]
    captured=OUT/'captured-compile-driver.py'
    if resume:
        execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['command']==list(map(str,command))
        log=OUT/'compile.log';seconds=execution['elapsed_seconds']
    else:
        captured.write_bytes(Path(__file__).read_bytes())
        p,log,seconds=run(command,'compile');assert p.returncode==0,log.read_text(encoding='utf8')
    pin(captured)
    assert not re.search(rb'(?:warning|error) [CD]\d+',log.read_bytes()),log.read_bytes()
    oracle=[]
    for va in VAS:
        data,rel=parse.coff_function(objects/'state-fixture.obj','?original_'+va+'_246@@YAXXZ');expected=bytearray.fromhex(originals[va])
        if va=='00590070':
            assert rel==[dict(offset=10,symbol='?count246@@3IA',type=6),dict(offset=28,symbol='?table246@@3IA',type=6)]
        else:assert rel==[]
        for r in rel:expected[r['offset']:r['offset']+4]=b'\0'*4
        assert data==bytes(expected),(va,data.hex(),expected.hex());oracle.append(dict(va=va,bytes=len(data),relocations=rel,normalized_exact=True))
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'));exe=OUT/'state-fixture.exe'
    libraries=[pin(abi.COMPILER.parents[3]/'lib/x86'/name) for name in ['libcmt.lib','libvcruntime.lib']]
    libraries.append(pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/ucrt/x86/libucrt.lib')))
    # The variable-width memcpy boundary is a CRT dependency, not an instruction-lowering change.
    # Preserve the first diagnostic link, then relink the same four successful COFFs.
    previous=OUT/'fixture-link.execution.json'
    if previous.exists() and load(previous)['exit_code']!=0 and not (OUT/'first-fixture-link.execution.json').exists():
        (OUT/'first-fixture-link.execution.json').write_bytes(previous.read_bytes())
        (OUT/'first-fixture-link.log').write_bytes((OUT/'fixture-link.log').read_bytes())
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/OUT:'+str(exe),*[objects/(va+'.obj')for va in VAS],objects/'state-fixture.obj',*libraries,kernel],'fixture-link');assert p.returncode==0,llog.read_bytes()
    p,_,native_seconds=run([exe],'fixture-native');assert p.returncode==0,('state comparisons failed',p.returncode)
    for p in [*objects.glob('*.obj'),exe,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(p)
    guard()
    summary=dict(schema=1,kind='isolated-static-x86-to-cpp-pilot',original_sha256=SHA,experimental_vas=VAS,new_accepted_functions=0,production_or_union_changed=False,
        translated_original_bytes=sum(len(bytes.fromhex(h))for h in originals.values()),translated_original_instructions=sum(map(len,witnesses.values())),
        existing_owner_regressions=3,actual_compiler_batches=1,game_algorithm_reimplementations=0,compile_seconds=seconds,compiler_exit_code=0,
        native_fixture_exit_code=0,native_seconds=native_seconds,state_comparisons=375808,oracle=oracle,input_sha256=pins,
        before_after_guards=True,unsupported_inputs_rejected=rejected,limits=proof['limits'],command=list(map(str,command)),resumed_existing_compile=resume)
    write(RUN/'summary.json',summary)
    print(json.dumps(dict(translated_functions=3,original_bytes=summary['translated_original_bytes'],state_comparisons=375808,compile_seconds=seconds,native_seconds=native_seconds,new_accepted_functions=0)))


if __name__=='__main__':main()

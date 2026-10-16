"""Mechanically slice two canonical175 definitions and prove exact rawcdecl aliases."""
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
RUN=RUNS/'240-canonical-lock-reuse'
OUT=ROOT/'local/experiments/v2-canonical-lock-reuse-240'
VAS=['005a3719','005a376b']
NAMES=['formatter_stdio_lock_index_005a3719','formatter_stdio_unlock_index_005a376b']
TARGETS=['?'+name+'@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z'for name in NAMES]
FROMS=['?FUN_'+va+'@@YAXHH@Z'for va in VAS]
sys.dont_write_bytecode=True


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


abi=module('abi240','scripts/research/experiment-v2-thiscall-186.py')
coff=module('coff240','scripts/research/build-v2-compile-corpus.py')
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))


def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')


FIXTURE='''#include "porsche/formatter_stdio.hpp"
extern "C" __declspec(dllimport) void __stdcall ExitProcess(unsigned int);
void __cdecl FUN_005a3719(int,int);void __cdecl FUN_005a376b(int,int);
using U240=std::uint32_t;
typedef void (__stdcall *Critical240)(void*);
Critical240 enter_slot240=0,leave_slot240=0;
U240 failures240=0,cases240=0,provider_calls240=0,typed_calls240=0,raw_calls240=0;
U240 trace_id240=0,trace_value240=0;
U240 save_sp240=0,save_bp240=0,save_bx240=0,save_si240=0,save_di240=0;
U240 seen_sp240=0,clean_sp240=0,seen_bp240=0,seen_bx240=0,seen_si240=0,seen_di240=0;
namespace porsche {
// Typed controlled boundaries ONLY; no real canonical lock-table/provider use.
void __cdecl exit_registry_lock_api_005a4ba4(std::uint32_t id){++provider_calls240;trace_id240=1;trace_value240=id;}
void __cdecl exit_registry_unlock_api_005a4c05(std::uint32_t id){++provider_calls240;trace_id240=2;trace_value240=id;}
void __stdcall formatter_lowio_critical_enter(void*p){++provider_calls240;trace_id240=3;trace_value240=static_cast<U240>(reinterpret_cast<std::uintptr_t>(p));}
void __stdcall formatter_lowio_critical_leave(void*p){++provider_calls240;trace_id240=4;trace_value240=static_cast<U240>(reinterpret_cast<std::uintptr_t>(p));}
// Original35B references. Same instructions, proved native relocation bindings.
__declspec(naked) void __cdecl original_lock240(int,int){__asm{
 mov eax,dword ptr[esp+4]
 cmp eax,20
 jge dynamic_lock240
 add eax,28
 push eax
 call exit_registry_lock_api_005a4ba4
 pop ecx
 ret
dynamic_lock240:
 mov eax,dword ptr[esp+8]
 add eax,32
 push eax
 call dword ptr[enter_slot240]
 ret
}}
__declspec(naked) void __cdecl original_unlock240(int,int){__asm{
 mov eax,dword ptr[esp+4]
 cmp eax,20
 jge dynamic_unlock240
 add eax,28
 push eax
 call exit_registry_unlock_api_005a4c05
 pop ecx
 ret
dynamic_unlock240:
 mov eax,dword ptr[esp+8]
 add eax,32
 push eax
 call dword ptr[leave_slot240]
 ret
}}
}
void expect_trace240(U240 before,U240 id,U240 value){if(provider_calls240!=before+1||trace_id240!=id||trace_value240!=value)++failures240;}
__declspec(noinline) void raw_edge240(void*target,int index,U240 pointer){__asm{
 mov eax,target
 mov ecx,index
 mov edx,pointer
 mov save_sp240,esp
 mov save_bp240,ebp
 mov save_bx240,ebx
 mov save_si240,esi
 mov save_di240,edi
 push edx
 push ecx
 mov ebx,0x176b92d3
 mov esi,0xa53c0481
 mov edi,0x59e0b72f
 mov ebp,0xc7138ae5
 call eax
 mov seen_sp240,esp
 mov seen_bp240,ebp
 mov seen_bx240,ebx
 mov seen_si240,esi
 mov seen_di240,edi
 add esp,8
 mov clean_sp240,esp
 mov ebp,save_bp240
 mov ebx,save_bx240
 mov esi,save_si240
 mov edi,save_di240
 mov esp,save_sp240
 }
 ++raw_calls240;
 if(seen_sp240!=save_sp240-8||clean_sp240!=save_sp240||seen_bp240!=0xc7138ae5u||seen_bx240!=0x176b92d3u||seen_si240!=0xa53c0481u||seen_di240!=0x59e0b72fu)++failures240;
}
void one240(U240 operation,void*raw,void*canonical,void*original,int index,U240 pointer){
 U240 id=index<20?(operation?2u:1u):(operation?4u:3u),value=index<20?static_cast<U240>(index)+28u:pointer+32u;
 U240 before=provider_calls240,sp_before=0,sp_after=0;
 __asm mov sp_before,esp
 if(operation)FUN_005a376b(index,static_cast<int>(pointer));else FUN_005a3719(index,static_cast<int>(pointer));
 __asm mov sp_after,esp
 ++typed_calls240;if(sp_before!=sp_after)++failures240;expect_trace240(before,id,value);
 before=provider_calls240;raw_edge240(raw,index,pointer);expect_trace240(before,id,value);
 before=provider_calls240;raw_edge240(canonical,index,pointer);expect_trace240(before,id,value);
 before=provider_calls240;raw_edge240(original,index,pointer);expect_trace240(before,id,value);++cases240;
}
extern "C" void __cdecl entry(){
 static_assert(sizeof(void*)==4&&sizeof(int)==4&&sizeof(std::int32_t)==4,"cdecl raw32 storage");
 enter_slot240=&porsche::formatter_lowio_critical_enter;leave_slot240=&porsche::formatter_lowio_critical_leave;
 void*raw[2]={reinterpret_cast<void*>(&FUN_005a3719),reinterpret_cast<void*>(&FUN_005a376b)};
 void*canonical[2]={reinterpret_cast<void*>(&porsche::formatter_stdio_lock_index_005a3719),reinterpret_cast<void*>(&porsche::formatter_stdio_unlock_index_005a376b)};
 void*original[2]={reinterpret_cast<void*>(&porsche::original_lock240),reinterpret_cast<void*>(&porsche::original_unlock240)};
 if(raw[0]!=canonical[0]||raw[1]!=canonical[1])++failures240;
 const int indexes[10]={static_cast<int>(0x80000000u),-29,-28,-1,0,1,19,20,21,0x7fffffff};
 const U240 pointers[11]={0,1,31,32,0x005e5508u,0x7fffffffu,0x80000000u,0xffffffe0u,0xfffffff0u,0xffffffffu,0x12345678u};
 for(U240 op=0;op<2;++op){
  for(U240 i=0;i<10;++i)for(U240 p=0;p<11;++p)one240(op,raw[op],canonical[op],original[op],indexes[i],pointers[p]);
  U240 state=0x3719376bu;
  for(U240 i=0;i<1024;++i){state=state*1664525u+1013904223u;int index=static_cast<int>(state);state=state*1664525u+1013904223u;one240(op,raw[op],canonical[op],original[op],index,state);}
 }
 if(cases240!=2268u||typed_calls240!=2268u||raw_calls240!=6804u||provider_calls240!=9072u)++failures240;
 ExitProcess(failures240?1:0);
}
'''


def main():
    resume='--resume-existing-compile'in sys.argv
    assert not (RUN/'summary.json').exists(),'completed240 immutable'
    if resume:assert (OUT/'compile.execution.json').exists() and (RUN/'proof-before-compile.json').exists()
    else:
        assert not OUT.exists(),'fresh240 required'
        OUT.mkdir()
    RUN.mkdir(parents=True,exist_ok=True);(RUN/'bindings').mkdir(exist_ok=True);pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();h=digest(path);assert expected is None or h==expected,('input SHA',path,h)
        assert path not in pins or pins[path]==h;pins[path]=h;return path
    def guard():
        for path,h in pins.items():assert digest(path)==h,('input mutation',path)
    def materialize(path,text):
        if resume:assert Path(path).read_bytes()==text.encode('utf8'),('compiled source drift',path)
        else:Path(path).write_text(text,encoding='utf8',newline='\n')
    for path in [Path(__file__),ROOT/'scripts/research/experiment-v2-thiscall-186.py',ROOT/'scripts/research/build-v2-compile-corpus.py',abi.COMPILER,abi.DUMPBIN,abi.COMPILER.with_name('c1xx.dll'),abi.COMPILER.with_name('c2.dll')]:pin(path)
    if resume:pin(OUT/'captured-compile-driver.py')
    old=load(pin(RUNS/'175-formatter-stdio/verification.json'));assert old['native_cpp_equal_original_x86'] and old['cases']==4152
    project175={name:h for name,h in old['source_sha256'].items()if '/source/'in name};assert len(project175)==18
    for name,h in project175.items():pin(ROOT/name,h)
    canonical=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_stdio.cpp';raw_source=canonical.read_bytes();assert b'\r'not in raw_source
    cached=pin(ROOT/'local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatter_stdio.obj')
    cached_symbols=coff.coff_symbols(cached);assert set(TARGETS)<=set(cached_symbols['defined'])
    tlog=pin(ROOT/'local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatte.99D94A9E.tlog/CL.read.1.tlog')
    # Recorded175 compiler reads give a small known header superset before newcompile.
    for line in tlog.read_text(encoding='utf16').splitlines():
        if line.strip() and not line.startswith('^'):pin(Path(line.strip()))
    include=ROOT/'iterations/v2/001-original-recovery/source/include'
    toolroot=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207';sdk=Path('C:/Program Files (x86)/Windows Kits/10/Include/10.0.26100.0')
    roots=[include,toolroot/'include',sdk/'ucrt',sdk/'shared',sdk/'um'];assert all(p.is_dir()for p in roots)
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    for r in abi.rows(pin(ROOT/'research/binary-index/manual-functions.jsonl')):
        if r['module']=='Porsche.exe':catalog[r['entry_va']]=r
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    registry=load(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'))
    assert not any(r['module']=='Porsche.exe'and any(int(a,16)<=int(va,16)<=int(b,16)for a,b in catalog[r['entry_va']]['ranges']for va in VAS)for r in registry['functions'])
    wip={}
    for va,name in zip(VAS,NAMES):
        rows=[]
        for path in (ROOT/'iterations/v2/001-original-recovery/source/recovered').rglob('*.cpp'):
            if re.search(r'\b'+name+r'\s*\([^;{}]*\)\s*\{',path.read_text(encoding='utf8')):rows.append(relative(path))
        assert rows==[relative(canonical)],('WIP owner must be exact canonical175',va,rows);wip[va]=rows
    baseline=load(pin(RUNS/'233-initialized-and-nested-union/summary.json'))
    assert not any(r['va']in VAS or set(TARGETS)&set(r['symbols']['defined'])for r in baseline['results'])
    calls=[r for r in abi.rows(pin(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl'))if r.get('to_function')in VAS];assert len(calls)==8
    original=pin(ROOT/'local/game/Porsche.exe',abi.SHA).read_bytes();pe=struct.unpack_from('<I',original,0x3c)[0]
    machine,count,_,_,_,opt,_=struct.unpack_from('<HHIIIHH',original,pe+4);assert machine==0x14c
    base=struct.unpack_from('<I',original,pe+24+28)[0];sections=[struct.unpack_from('<IIII',original,pe+24+opt+i*40+8)[1:]for i in range(count)]
    instructions={}
    for va in VAS+sorted({r['from_function']for r in calls}):
        ins=abi.function_instructions(catalog[va],ix)
        for i in ins:
            rva=int(i['va'],16)-base;n=len(i['bytes'])//2;start,size,offset=next(s for s in sections if s[0]<=rva and rva+n<=s[0]+s[1]);assert original[offset+rva-start:offset+rva-start+n].hex()==i['bytes']
        instructions[va]=ins
    for va in VAS:
        ins=instructions[va];assert len(ins)==13 and sum(len(i['bytes'])//2 for i in ins)==35
        assert [i['bytes']for i in ins if i['instruction'].startswith('RET')]==['c3','c3']
        assert [i['instruction']for i in ins if '['in i['instruction']]==['MOV EAX,dword ptr [ESP + 0x4]','MOV EAX,dword ptr [ESP + 0x8]',
            'CALL dword ptr [0x005b2078]'if va==VAS[0]else'CALL dword ptr [0x005b206c]']
    imports=[r for r in abi.rows(pin(ROOT/'research/binary-index/static/imports.jsonl'))if r['path']=='Porsche.exe'and r['symbol']in ['EnterCriticalSection','LeaveCriticalSection']]
    assert {r['symbol']:r['iat_rva']for r in imports}==dict(EnterCriticalSection='0x1b2078',LeaveCriticalSection='0x1b206c')
    def fragment(start,end,label):
        data=raw_source[start:end];return dict(kind='canonical_bytes',label=label,offset=start,length=end-start,sha256=hashlib.sha256(data).hexdigest(),text=data.decode())
    prefix=fragment(0,raw_source.index(b'namespace porsche {'),'original_include_prefix')
    hs=raw_source.index(b'using U=');he=raw_source.index(b'\n',raw_source.index(b'U address(',hs))+1;helper=fragment(hs,he,'private_usingU_and_address_helper')
    sources={};slices={}
    for va,name in zip(VAS,NAMES):
        start=raw_source.index(('void __cdecl '+name+'(').encode());brace=raw_source.index(b'{',start);depth=1;end=brace+1
        while depth:
            depth+=(raw_source[end]==123)-(raw_source[end]==125);end+=1
        end+=1;definition=fragment(start,end,'exact_canonical_definition_'+va)
        parts=[prefix,dict(kind='wrapper',text='namespace porsche {\nnamespace {\n'),helper,dict(kind='wrapper',text='}\n'),definition,dict(kind='wrapper',text='}\n')]
        path=OUT/(va+'.cpp');materialize(path,''.join(p['text']for p in parts));pin(path);sources[va]=path;slices[va]=parts
    support_sources={};directives={}
    for va,fr,to in zip(VAS,FROMS,TARGETS):
        directive='/alternatename:'+fr+'='+to;directives[va]=directive
        path=OUT/('binding_'+va+'.cpp');materialize(path,'#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4 && sizeof(int)==4,"proven raw32 cdecl");\n#pragma comment(linker,"'+directive+'")\n');pin(path);support_sources[va]=path
    fixture=OUT/'native-fixture.cpp';materialize(fixture,FIXTURE);pin(fixture)
    owner_header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/formatter_crt_runtime.hpp';assert 'formatter_crt_locks_005e57a8[26]'in owner_header.read_text()
    proof=dict(schema=1,original_sha256=abi.SHA,logical_VAs=VAS,canonical_source=relative(canonical),canonical_source_sha256=digest(canonical),canonical175_project_pins=project175,
        canonical_registry_owners=[],WIP_reused_exactly=wip,cached_uninstrumented_object=relative(cached),cached_object_sha256=digest(cached),cached_defined_symbols=cached_symbols['defined'],
        mechanically_copied_slices=slices,original_instructions=instructions,indexed_callers=calls,imports=imports,
        contracts='Two exact voidcdecl rawFUN(int,int) -> canonical(int32,Descriptor*) edges: two4B stackslots, RET0; signed index<20 selects uint32(index)+28; otherwise rawpointerbits+32. No Descriptor dereference or hiddeninput.',
        table_prefix=dict(published=26,required=48,production_ready=False,owner=relative(owner_header)),
        limits=['Canonical175 algorithms reused byte-for-byte; no alternate manual bodies and no wholeTU/global/flush reuse.',
            'Only exact rawpointer32 cdecl aliases; no general ABI inference or arbitrary alias.',
            'Providers controlled only; published26-entry lockprefix does not support required IDs28..47. Full production/provider/register/fault/game fidelity remains open.'])
    if resume:assert load(RUN/'proof-before-compile.json')==proof,'original precompile proof drift'
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json');guard()
    objects=OUT/'objects'
    if not resume:objects.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/showIncludes']
    command=[abi.COMPILER,*flags,*[x for root in roots for x in ['/I',root]],'/Fo'+str(objects)+os.sep,*sources.values(),*support_sources.values(),fixture]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''}
    def run(command,name):
        command=list(map(str,command));started=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);seconds=time.perf_counter()-started
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        try:log=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:log=(p.stdout+p.stderr).decode('cp1251')
        path=OUT/(name+'.log');path.write_text(log.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p,path,seconds
    if resume:
        execution=load(OUT/'compile.execution.json');assert execution['exit_code']==0 and execution['command']==list(map(str,command))
        log=OUT/'compile.log';seconds=execution['elapsed_seconds']
    else:
        p,log,seconds=run(command,'compile');assert p.returncode==0,log.read_text()
    warnings=re.findall(r'warning ([CD]\d+)',log.read_text(encoding='utf8'));assert sorted(warnings)==['C4731','C4731','D9030'],warnings
    assert not re.search(r'error [CD]\d+',log.read_text(encoding='utf8'))
    receipt=pin(OUT/'compile.execution.json');actual_headers=set()
    for line in log.read_text(encoding='utf8').splitlines():
        if not re.search(r'(?:including file|включение файла):',line,re.I):continue
        m=re.search(r'([A-Za-z]:[\\/].*?)\s*$',line)
        if m:
            path=Path(m[1]).resolve()
            if not path.is_file():continue
            assert path in pins,('header not prepinned from175 closure',path);actual_headers.add(path)
    assert include/'porsche/formatter_stdio.hpp'in actual_headers
    results=[];support_rows=[];aliases=[]
    for va,target,fr in zip(VAS,TARGETS,FROMS):
        obj=objects/(va+'.obj');symbols=coff.coff_symbols(obj);assert symbols['defined']==[target]
        assert not any('005a76a1'in s or 'formatter_stdio_buffers_'in s for s in symbols['defined'])
        p,dis,_=run([abi.DUMPBIN,'/disasm',obj],va+'-disassembly');assert p.returncode==0
        results.append(dict(va=va,name=NAMES[VAS.index(va)],compiled=True,canonical_reuse=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
            generated_source=relative(sources[va]),generated_source_sha256=digest(sources[va]),dependency_sha256={relative(path):pins[path]for path in actual_headers|{sources[va]}},forced_headers=[],
            include_directories=[relative(root)for root in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=relative(receipt),
            object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined'],
            original_ret_bytes=[0,0],disassembly=relative(dis),disassembly_sha256=digest(dis)))
        sobj=objects/('binding_'+va+'.obj');ss=coff.coff_symbols(sobj);assert not any(ss.values())
        p,sections,_=run([abi.DUMPBIN,'/headers','/rawdata',sobj],va+'-binding-sections');assert p.returncode==0
        support_rows.append(dict(id='canonical-lock-binding-'+va,generated_source=relative(support_sources[va]),generated_source_sha256=digest(support_sources[va]),object=relative(sobj),object_sha256=digest(sobj),
            dependency_sha256={relative(support_sources[va]):digest(support_sources[va])},symbols=ss,directive=directives[va],function_count=0))
        aliases.append(dict(**{'from':fr,'to':target},va=va,support_object_id='canonical-lock-binding-'+va,directive=directives[va],
            proof=dict(original_sha256=abi.SHA,callee_ret_pop_bytes=0,stackslots=[dict(offset=4,bytes=4,representation='signedint32'),dict(offset=8,bytes=4,representation='opaque pointerbits32; only+32, no dereference')],
                canonical_source=relative(canonical),canonical_source_sha256=digest(canonical),exact_fragment_evidence=relative(RUN/'proof-before-compile.json'),native_fixture_cases=1134,typed_target_identity_verified=True)))
    link=pin(abi.COMPILER.with_name('link.exe'));kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'));exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
    p,llog,_=run([link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),*[objects/(va+'.obj')for va in VAS],*[objects/('binding_'+va+'.obj')for va in VAS],objects/'native-fixture.obj',kernel],'fixture-link');assert p.returncode==0,llog.read_text()
    p,nlog,nseconds=run([exe],'fixture-native');assert p.returncode==0,('fixture failed',p.returncode)
    p,fdis,_=run([abi.DUMPBIN,'/disasm',objects/'native-fixture.obj'],'fixture-disassembly');assert p.returncode==0
    for path in [*objects.glob('*.obj'),exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json')]:pin(path)
    guard();manifest={relative(path):h for path,h in pins.items()}
    summary=dict(schema=1,kind='canonical-lock-body-reuse',original_sha256=abi.SHA,objects_compiled=2,real_coff_objects=2,results=results,compiled_vas=VAS,new_distinct_function_VAs=2,
        actual_compiler_batches=1,actual_parallel_compilation=False,requested_MP6_ignored_by_showIncludes=True,changed_game_TUs=2,handwritten_game_algorithm_TUs=0,synthetic_fixture_TUs=1,directive_only_support_TUs=2,compiler_batch_exit_code=0,compile_seconds=seconds,
        compile_warnings=dict(game=0,driver=['D9030 showIncludes disables MP6; actual single serial batch'],fixture=['C4731 intentional EBP marker+restoration','C4731 intentional EBP marker+restoration']),
        resumed_existing_successful_compile=resume,recompilations=0,captured_compile_driver=relative(OUT/'captured-compile-driver.py')if resume else relative(Path(__file__)),
        compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_execution_receipt=relative(receipt),compiler_log=relative(log),compiler_log_sha256=digest(log),
        input_sha256=manifest,input_guards_before=True,input_guards_after=True,canonical175_source_pins_reused=18,observed_headers_prepinned=len(actual_headers),original_instructions_per_body=13,original_bytes_per_body=35,
        Ghidra_decompilations=0,production_or_union_changes=False,production_ready=False,fixture=dict(native_exit_code=0,cases=2268,typed_alias_calls=2268,raw_calls=6804,provider_calls=9072,seconds=nseconds,
            executable=relative(exe),executable_sha256=digest(exe),aliases_same_target_address=True,ESP_and_nonvolatile_registers=True,provider_fidelity_claimed=False),limits=proof['limits'])
    write(RUN/'summary.json',summary)
    bindings=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=abi.SHA,compiler_sha256=digest(abi.COMPILER),new_function_count=0,support_objects=support_rows,aliases=aliases,
        compiler_batch_exit_code=0,input_sha256={**manifest,relative(RUN/'summary.json'):digest(RUN/'summary.json')},compiler_command=list(map(str,command)),compiler_execution_receipt=relative(receipt),
        ordinary_summary=relative(RUN/'summary.json'),ordinary_summary_sha256=digest(RUN/'summary.json'),production_ready=False,limits=proof['limits'])
    write(RUN/'bindings/summary.json',bindings)
    print(json.dumps(dict(canonical_COFF=2,directive_only_COFF=2,compile_seconds=seconds,fixture_cases=2268,fixture_seconds=nseconds,observed_headers=len(actual_headers))))


if __name__=='__main__':main()

"""Three exact canonical fragments with narrow x86 raw-word ABI bindings."""
import argparse
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

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'247-canonical-reuse-batch'
OUT=ROOT/'local/experiments/v2-canonical-reuse-247'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=['005a669e','005a36ea','005a373c']
NAMES=['formatter_lowio_errno_005a669e','formatter_stdio_lock_pointer_005a36ea','formatter_stdio_unlock_pointer_005a373c']
TARGETS=['?'+NAMES[0]+'@porsche@@YAPAHXZ',*['?'+n+'@porsche@@YAXPAUFormatterOriginalDescriptor32@1@@Z' for n in NAMES[1:]]]
FROMS=['?FUN_005a669e@@YAHXZ','?FUN_005a36ea@@YAXI@Z','?FUN_005a373c@@YAXI@Z']
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):
    p=Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def write(p,value):Path(p).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

FIXTURE=r'''#include "porsche/formatter_stdio.hpp"
#include "porsche/formatter_crt_runtime.hpp"
extern "C" __declspec(dllimport) void __stdcall ExitProcess(unsigned int);
int __cdecl FUN_005a669e();
void __cdecl FUN_005a36ea(unsigned int);void __cdecl FUN_005a373c(unsigned int);
using U=std::uint32_t;
U fail247=0,pointer_cases247=0,errno_cases247=0,provider_calls247=0,thread_calls247=0;
U typed_calls247=0,raw_calls247=0,tag247=0,value247=0;
U save_sp247=0,save_bp247=0,save_bx247=0,save_si247=0,save_di247=0;
U seen_sp247=0,seen_bp247=0,seen_bx247=0,seen_si247=0,seen_di247=0,seen_ax247=0,clean_sp247=0,stack_bytes247=0;
alignas(16) unsigned char arena247[4096];void* thread_base247=arena247;
using Critical247=void(__stdcall*)(void*);Critical247 enter_slot247=0,leave_slot247=0;
namespace porsche {
// Private address-only FILE20 and controlled providers; no game storage/provider object.
FormatterOriginalDescriptor32 formatter_iob_entries_005e54e8[20]{};
void __cdecl exit_registry_lock_api_005a4ba4(U id){++provider_calls247;tag247=1;value247=id;}
void __cdecl exit_registry_unlock_api_005a4c05(U id){++provider_calls247;tag247=2;value247=id;}
void __stdcall formatter_lowio_critical_enter(void*p){++provider_calls247;tag247=3;value247=reinterpret_cast<U>(p);}
void __stdcall formatter_lowio_critical_leave(void*p){++provider_calls247;tag247=4;value247=reinterpret_cast<U>(p);}
void* __cdecl formatter_crt_thread_005a545c(){++thread_calls247;return thread_base247;}
__declspec(naked) void __cdecl original_lock247(U){__asm{
 mov eax,dword ptr[esp+4]
 mov ecx,offset formatter_iob_entries_005e54e8
 cmp eax,ecx
 jb dynamic_lock247
 cmp eax,offset formatter_iob_entries_005e54e8+608
 ja dynamic_lock247
 sub eax,ecx
 sar eax,5
 add eax,28
 push eax
 call exit_registry_lock_api_005a4ba4
 pop ecx
 ret
dynamic_lock247:
 add eax,32
 push eax
 call dword ptr[enter_slot247]
 ret
}}
__declspec(naked) void __cdecl original_unlock247(U){__asm{
 mov eax,dword ptr[esp+4]
 mov ecx,offset formatter_iob_entries_005e54e8
 cmp eax,ecx
 jb dynamic_unlock247
 cmp eax,offset formatter_iob_entries_005e54e8+608
 ja dynamic_unlock247
 sub eax,ecx
 sar eax,5
 add eax,28
 push eax
 call exit_registry_unlock_api_005a4c05
 pop ecx
 ret
dynamic_unlock247:
 add eax,32
 push eax
 call dword ptr[leave_slot247]
 ret
}}
__declspec(naked) void* __cdecl original_errno247(){__asm{
 call formatter_crt_thread_005a545c
 add eax,8
 ret
}}
}
__declspec(noinline) void raw247(void*target,U argument,U slots){
 stack_bytes247=slots*4;
 __asm{
 mov eax,target
 mov ecx,argument
 mov edx,slots
 mov save_sp247,esp
 mov save_bp247,ebp
 mov save_bx247,ebx
 mov save_si247,esi
 mov save_di247,edi
 test edx,edx
 jz no_push247
 push ecx
no_push247:
 mov ebx,0x176b92d3
 mov esi,0xa53c0481
 mov edi,0x59e0b72f
 mov ebp,0xc7138ae5
 call eax
 mov seen_ax247,eax
 mov seen_sp247,esp
 mov seen_bp247,ebp
 mov seen_bx247,ebx
 mov seen_si247,esi
 mov seen_di247,edi
 add esp,stack_bytes247
 mov clean_sp247,esp
 mov ebp,save_bp247
 mov ebx,save_bx247
 mov esi,save_si247
 mov edi,save_di247
 mov esp,save_sp247
 }
 ++raw_calls247;
 if(seen_sp247!=save_sp247-stack_bytes247||clean_sp247!=save_sp247||seen_bp247!=0xc7138ae5u||seen_bx247!=0x176b92d3u||seen_si247!=0xa53c0481u||seen_di247!=0x59e0b72fu)++fail247;
}
void check_pointer247(U operation,void*raw,void*canonical,void*original,U pointer){
 const U first=reinterpret_cast<U>(porsche::formatter_iob_entries_005e54e8),last=first+608;
 const bool inside=pointer>=first&&pointer<=last;
 const U wanted_tag=inside?(operation?2u:1u):(operation?4u:3u),wanted=inside?((pointer-first)>>5)+28:pointer+32;
 U before=provider_calls247,sp0=0,sp1=0;
 __asm mov sp0,esp
 if(operation)FUN_005a373c(pointer);else FUN_005a36ea(pointer);
 __asm mov sp1,esp
 ++typed_calls247;
 if(sp0!=sp1||provider_calls247!=before+1||tag247!=wanted_tag||value247!=wanted)++fail247;
 void* targets[3]={raw,canonical,original};
 for(U i=0;i<3;++i){before=provider_calls247;raw247(targets[i],pointer,1);if(provider_calls247!=before+1||tag247!=wanted_tag||value247!=wanted)++fail247;}
 ++pointer_cases247;
}
extern "C" void __cdecl entry(){
 static_assert(sizeof(void*)==4&&sizeof(int)==4&&sizeof(porsche::FormatterOriginalDescriptor32)==32,"original raw32 ABI");
 enter_slot247=&porsche::formatter_lowio_critical_enter;leave_slot247=&porsche::formatter_lowio_critical_leave;
 void* raw[3]={reinterpret_cast<void*>(&FUN_005a669e),reinterpret_cast<void*>(&FUN_005a36ea),reinterpret_cast<void*>(&FUN_005a373c)};
 void* canonical[3]={reinterpret_cast<void*>(&porsche::formatter_lowio_errno_005a669e),reinterpret_cast<void*>(&porsche::formatter_stdio_lock_pointer_005a36ea),reinterpret_cast<void*>(&porsche::formatter_stdio_unlock_pointer_005a373c)};
 void* original[3]={reinterpret_cast<void*>(&porsche::original_errno247),reinterpret_cast<void*>(&porsche::original_lock247),reinterpret_cast<void*>(&porsche::original_unlock247)};
 for(U i=0;i<3;++i)if(raw[i]!=canonical[i])++fail247;
 const U first=reinterpret_cast<U>(porsche::formatter_iob_entries_005e54e8);
 const U edges[11]={0,1,31,32,0x7fffffffu,0x80000000u,0xffffffe0u,0xfffffff0u,0xffffffffu,first-1,first+609};
 for(U op=0;op<2;++op){
  for(int delta=-64;delta<=672;++delta)check_pointer247(op,raw[op+1],canonical[op+1],original[op+1],first+static_cast<U>(delta));
  for(U i=0;i<11;++i)check_pointer247(op,raw[op+1],canonical[op+1],original[op+1],edges[i]);
  U state=0x36ea373cu;for(U i=0;i<1024;++i){state=state*1664525u+1013904223u;check_pointer247(op,raw[op+1],canonical[op+1],original[op+1],state);}
 }
 for(U i=0;i<4096;++i)arena247[i]=0xa5;
 for(U i=0;i<512;++i){
  thread_base247=arena247+(i%128)*16;
  const U expected=reinterpret_cast<U>(thread_base247)+8;
  U before=thread_calls247,sp0=0,sp1=0,got=0;
  __asm mov sp0,esp
  got=static_cast<U>(FUN_005a669e());
  __asm mov sp1,esp
  ++typed_calls247;if(got!=expected||sp0!=sp1||thread_calls247!=before+1)++fail247;
  for(U t=0;t<3;++t){before=thread_calls247;void* target=t==0?raw[0]:t==1?canonical[0]:original[0];raw247(target,0,0);if(seen_ax247!=expected||thread_calls247!=before+1)++fail247;}
  ++errno_cases247;
 }
 for(U i=0;i<4096;++i)if(arena247[i]!=0xa5)++fail247;
 if(pointer_cases247!=3544||errno_cases247!=512||typed_calls247!=4056||raw_calls247!=12168||provider_calls247!=14176||thread_calls247!=2048)++fail247;
 ExitProcess(fail247?1:0);
}
'''


def main(resume=False):
    assert not (RUN/'summary.json').exists(),'Completed247 is immutable'
    if resume:assert (OUT/'compile.execution.json').exists()
    else:
        assert not OUT.exists(),'Fresh247 output required';OUT.mkdir(parents=True)
    RUN.mkdir(parents=True,exist_ok=True);(RUN/'bindings').mkdir(exist_ok=True)
    pins={}
    def pin(p,expected=None):
        p=Path(p).resolve();sha=digest(p);assert expected is None or sha==expected,('SHA drift',p)
        assert p not in pins or pins[p]==sha;pins[p]=sha;return p
    def guard():
        for p,sha in pins.items():assert digest(p)==sha,('Input mutation',p)
    def materialize(p,text):
        if resume:assert Path(p).read_bytes()==text.encode('utf8'),('Source drift',p)
        else:Path(p).write_text(text,encoding='utf8',newline='\n')
        return pin(p)
    pin(Path(__file__))
    if not resume:(OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes())
    pin(OUT/'captured-compile-driver.py')
    h=module('h247',pin(ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'))
    abi=module('abi247',pin(ROOT/'scripts/research/experiment-v2-thiscall-186.py'))
    coff=module('coff247',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    audit=module('audit247',pin(RUNS/'226-writable-scalar-storage/audit.py'))
    old=json.loads(pin(RUNS/'240-canonical-lock-reuse/summary.json').read_bytes())
    roots=[(ROOT/x).resolve()for x in old['results'][0]['include_directories']]
    for name,sha in old['input_sha256'].items():
        p=(ROOT/name).resolve()
        if any(p.is_relative_to(r)for r in roots):pin(p,sha)
    for path in [abi.COMPILER,abi.COMPILER.with_name('c1xx.dll'),abi.COMPILER.with_name('c2.dll'),abi.COMPILER.with_name('link.exe')]:pin(path)
    assert digest(abi.COMPILER)==old['compiler_sha256']
    kernel=pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    registry=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    baseline=json.loads(pin(RUNS/'243-canonical-reuse-union/summary.json').read_bytes())
    assert not any(r.get('va')in VAS for r in baseline['results'])
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    for r in abi.rows(pin(ROOT/'research/binary-index/manual-functions.jsonl')):
        if r['module']=='Porsche.exe':catalog[r['entry_va']]=r
    for va in VAS:
        exact=[r for r in registry if r['module']=='Porsche.exe'and r['entry_va']==va]
        assert len(exact)==(1 if va=='005a669e'else 0)
        assert not any(r['entry_va']!=va and any(int(a,16)<=int(va,16)<=int(b,16)for a,b in catalog[r['entry_va']]['ranges'])for r in registry if r['module']=='Porsche.exe')
    source_root=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'
    canonical={name:pin(source_root/name).read_bytes()for name in ['formatter_stdio.cpp','formatter_crt_runtime.cpp']}
    source175=json.loads(pin(RUNS/'175-formatter-stdio/verification.json').read_bytes())
    source157=json.loads(pin(RUNS/'157-crt-runtime/verification.json').read_bytes())
    canonical_pins={};superseded_157_headers={}
    for report in [source175,source157]:
        for name,sha in report['source_sha256'].items():
            if '/source/'in name:
                if name in canonical_pins and canonical_pins[name]!=sha:
                    superseded_157_headers[name]=dict(report157_sha256=sha,accepted175_sha256=canonical_pins[name])
                    pin(ROOT/name,canonical_pins[name])
                else:
                    pin(ROOT/name,sha);canonical_pins[name]=sha
    ix=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    original=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();original_sections=h.sections(original)
    def image_offset(pc):
        s=next(s for s in original_sections if s['va']<=pc<s['va']+s['rawsize']);return s['raw']+pc-s['va']
    instructions={va:abi.function_instructions(catalog[va],ix)for va in VAS+['005a4c05']}
    for va,ins in instructions.items():
        for i in ins:
            pc=int(i['va'],16);raw=bytes.fromhex(i['bytes']);assert original[image_offset(pc):image_offset(pc)+len(raw)]==raw
        assert sum(len(i['bytes'])//2 for i in ins)=={'005a669e':9,'005a36ea':47,'005a373c':47,'005a4c05':21}[va]
    calls=[r for r in abi.rows(pin(ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl'))if r.get('to_function')in VAS]
    consumers=[]
    for va,fr in zip(VAS,FROMS):
        frontier=next(r for r in baseline['frontier']if r.get('va')==va);assert frontier['symbol']==fr
        for caller in frontier['referring_object_vas']:
            r=next(r for r in baseline['results']if r.get('va')==caller);obj=pin(ROOT/r['object'],r['object_sha256'])
            actual=coff.coff_symbols(obj);assert fr in actual['undefined']
            for name in r['include_closure']:pin(ROOT/name,baseline['input_sha256'][name])
            consumers.append(dict(va=va,caller=caller,object=r['object'],object_sha256=r['object_sha256'],required_native_symbol=fr))
    def fragment(raw,start,end,label):
        value=raw[start:end];return dict(kind='canonical_bytes',offset=start,length=end-start,sha256=hashlib.sha256(value).hexdigest(),label=label,text=value.decode())
    def definition(raw,name):
        start=raw.index(name.encode());start=raw.rfind(b'\n',0,start)+1;at=raw.index(b'{',start);depth=1;end=at+1
        while depth:depth+=(raw[end]==123)-(raw[end]==125);end+=1
        return fragment(raw,start,end+1,'exact_'+name)
    slices={};sources={}
    for va,name in zip(VAS,NAMES):
        owner='formatter_crt_runtime.cpp'if va=='005a669e'else'formatter_stdio.cpp';raw=canonical[owner]
        parts=[fragment(raw,0,raw.index(b'namespace porsche {'),'original_include_prefix'),dict(kind='wrapper',text='namespace porsche {\n')]
        if va!='005a669e':
            at=raw.index(b'using U=');end=raw.index(b'\n',raw.index(b'U address(',at))+1
            parts.extend([dict(kind='wrapper',text='namespace {\n'),fragment(raw,at,end,'usingU_and_address'),definition(raw,'lock_pointer'),dict(kind='wrapper',text='}\n')])
        parts.extend([definition(raw,name),dict(kind='wrapper',text='}\n')])
        slices[va]=dict(canonical_source=relative(source_root/owner),parts=parts)
        sources[va]=materialize(OUT/(va+'.cpp'),''.join(x['text']for x in parts))
    supports={};directives={}
    for va,fr,target in zip(VAS,FROMS,TARGETS):
        directives[va]='/alternatename:'+fr+'='+target
        supports[va]=materialize(OUT/('binding_'+va+'.cpp'),'#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4&&sizeof(int)==4,"raw32 ABI");\n#pragma comment(linker,"'+directives[va]+'")\n')
    fixture=materialize(OUT/'native-fixture.cpp',FIXTURE)
    proof=dict(schema=1,original_sha256=SHA,selected_vas=VAS,mechanically_copied_slices=slices,
        canonical_source_pins=canonical_pins,superseded157_headers_using_accepted175=superseded_157_headers,
        original_instructions=instructions,indexed_incoming_calls=calls,actual_native_consumers=consumers,
        deferred=dict(va='005a4c05',reason='Canonical array[26] cannot silently supply demanded IDs28..47; no storage expansion or source-level out-of-bounds workaround',published_prefix=26,required_stdio_prefix=48),
        fixture_scope='Controlled FILE20 address+CRT/critical/TLS providers only; pointer slots are raw32, errno return is EAX pointerbits; no real-provider composition')
    if resume:assert json.loads((RUN/'proof-before-compile.json').read_bytes())==proof
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json')
    objects=OUT/'objects';deps=OUT/'dependencies'
    if not resume:objects.mkdir();deps.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Gy','/GS-','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/sourceDependencies',str(deps)]
    command=[abi.COMPILER,*flags,*[v for root in roots for v in ['/I',root]],'/Fo'+str(objects)+os.sep,*sources.values(),*supports.values(),fixture]
    env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''}
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter();p=subprocess.run(command,cwd=OUT,env=env,capture_output=True,timeout=120);seconds=time.perf_counter()-start
        write(OUT/(name+'.execution.json'),dict(command=command,exit_code=p.returncode,elapsed_seconds=seconds))
        try:text=(p.stdout+p.stderr).decode('utf8')
        except UnicodeDecodeError:text=(p.stdout+p.stderr).decode('cp1251')
        log=OUT/(name+'.log');log.write_text(text.replace('\r\n','\n').replace('\r','\n'),encoding='utf8',newline='\n');return p.returncode,log,seconds
    guard()
    if resume:
        execution=json.loads((OUT/'compile.execution.json').read_bytes());assert execution['exit_code']==0 and execution['command']==list(map(str,command));compile_seconds=execution['elapsed_seconds']
    else:
        write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={relative(p):sha for p,sha in pins.items()}))
        exitcode,log,compile_seconds=run(command,'compile');assert exitcode==0,log.read_text()
    compile_receipt=pin(OUT/'compile.execution.json');compile_log=pin(OUT/'compile.log');text=compile_log.read_text(encoding='utf8')
    warnings=re.findall(r'warning ([CD]\d+)',text);assert warnings==['C4731','C4731']and not re.search(r'error [CD]\d+',text),warnings
    actual_headers={};dependency_reports={}
    for source in [*sources.values(),*supports.values(),fixture]:
        reportpath=pin(deps/(source.name+'.json'));report=json.loads(reportpath.read_bytes());assert report['Version']=='1.2'
        assert Path(report['Data']['Source']).resolve()==source
        includes={Path(p).resolve()for p in report['Data']['Includes']}
        assert all(p in pins for p in includes),('Unprepinned actual header',includes-set(pins))
        actual_headers[source]=includes;dependency_reports[source]=reportpath
    results=[];support_rows=[];aliases=[]
    for va,name,target,fr in zip(VAS,NAMES,TARGETS,FROMS):
        obj=objects/(va+'.obj');symbols=coff.coff_symbols(obj);assert symbols['defined']==[target]
        results.append(dict(va=va,name=name,compiled=True,canonical_reuse=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,
            generated_source=relative(sources[va]),generated_source_sha256=digest(sources[va]),dependency_sha256={relative(p):pins[p]for p in actual_headers[sources[va]]|{sources[va]}},
            forced_headers=[],include_directories=[relative(p)for p in roots],compiler_command=list(map(str,command)),compiler_execution_receipt=relative(compile_receipt),
            source_dependencies=relative(dependency_reports[sources[va]]),source_dependencies_sha256=digest(dependency_reports[sources[va]]),
            object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined']))
        obj=objects/('binding_'+va+'.obj');symbols=coff.coff_symbols(obj);assert not any(symbols.values())
        parsed=audit.coff(obj);section=next(s for s in parsed['sections']if s['name']=='.drectve');directive=parsed['bytes'][section['raw']:section['raw']+section['size']].decode().strip();assert directive==directives[va]
        support_rows.append(dict(id='canonical-reuse-binding-'+va,generated_source=relative(supports[va]),generated_source_sha256=digest(supports[va]),object=relative(obj),object_sha256=digest(obj),dependency_sha256={relative(supports[va]):digest(supports[va])},symbols=symbols,directive=directive,function_count=0))
        aliases.append(dict(**{'from':fr,'to':target},va=va,support_object_id='canonical-reuse-binding-'+va,directive=directive,proof=dict(original_sha256=SHA,ret_pop_bytes=0,
            representation='EAX pointer32→int32, noargs'if va==VAS[0]else'oneDWORD rawuint32→opaqueDescriptorpointer32; no dereference',exact_fragment_evidence=relative(RUN/'proof-before-compile.json'))))
    exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map'
    exitcode,log,_=run([abi.COMPILER.with_name('link.exe'),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),
        *[objects/(va+'.obj')for va in VAS],*[objects/('binding_'+va+'.obj')for va in VAS],objects/'native-fixture.obj',kernel],'fixture-link');assert exitcode==0,log.read_text()
    write(OUT/'fixture-before-execution.json',dict(executable=relative(exe),executable_sha256=digest(exe),fixture_object_sha256=digest(objects/'native-fixture.obj')))
    exitcode,log,native_seconds=run([exe],'fixture-native');assert exitcode==0
    for p in [*objects.glob('*.obj'),exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),OUT/'fixture-before-execution.json']:pin(p)
    guard();manifest={relative(p):sha for p,sha in pins.items()}
    limits=['Canonical algorithms/helpers byte-identical; no wholeTU/global duplication or host substitute',
        'Controlled FILE20/TLS/CRT/critical providers only; real namespace sharedstate and lockprefix26/48 composition open',
        'Opaque x86 pointer/return bits only; no class/layout/lifetime or full game/provider/fault claim']
    summary=dict(schema=1,kind='canonical-body-reuse-batch',original_sha256=SHA,objects_compiled=3,real_coff_objects=3,results=results,compiled_vas=VAS,new_distinct_function_VAs=3,
        actual_compiler_batches=1,actual_MP6_requested=True,showIncludes_disabled=False,changed_game_TUs=3,handwritten_game_algorithm_TUs=0,directive_only_support_TUs=3,synthetic_fixture_TUs=1,
        compiler_batch_exit_code=0,compile_seconds=compile_seconds,resumed_existing_successful_compile=resume,recompilations=0,captured_compile_driver=relative(OUT/'captured-compile-driver.py'),
        compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_execution_receipt=relative(compile_receipt),compiler_log=relative(compile_log),compiler_log_sha256=digest(compile_log),
        compiler_warnings=dict(game=0,driver=0,fixture=warnings),actual_header_counts={va:len(actual_headers[sources[va]])for va in VAS},source_dependencies_format='MSVC1.2',
        input_sha256=manifest,input_guards_before=True,input_guards_after=True,original_selected_bytes=103,production_ready=False,production_or_union_changes=False,
        fixture=dict(cases=4056,pointer_cases=3544,errno_cases=512,typed_alias_calls=4056,raw_calls=12168,critical_lock_provider_calls=14176,thread_provider_calls=2048,
            native_exit_code=0,seconds=native_seconds,executable=relative(exe),executable_sha256=digest(exe),alias_identity=True,EAX_pointer_return=True,ESP_nonvolatile=True,poisoned_TLS_unchanged=True),
        deferred=[proof['deferred']],limits=limits)
    write(RUN/'summary.json',summary)
    bindings=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=SHA,compiler_sha256=digest(abi.COMPILER),new_function_count=0,support_objects=support_rows,aliases=aliases,
        compiler_batch_exit_code=0,input_sha256={**manifest,relative(RUN/'summary.json'):digest(RUN/'summary.json')},compiler_command=list(map(str,command)),compiler_execution_receipt=relative(compile_receipt),
        ordinary_summary=relative(RUN/'summary.json'),ordinary_summary_sha256=digest(RUN/'summary.json'),production_ready=False,limits=limits)
    write(RUN/'bindings/summary.json',bindings)
    print(json.dumps(dict(ordinary=3,support=3,compile_seconds=compile_seconds,native_cases=4056,native_exit=0,headers=summary['actual_header_counts'],pins=len(pins))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume-existing-compile',action='store_true');main(parser.parse_args().resume_existing_compile)

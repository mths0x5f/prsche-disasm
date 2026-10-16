"""Two exact canonical fragments and narrow original-ABI aliases, without new algorithms."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'259-canonical-reuse'
OUT=ROOT/'local/experiments/v2-canonical-reuse-259'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
VAS=('0059f050','005a66a7')
NAMES=('application_release_0059f050','formatter_lowio_doserrno_005a66a7')
FROM=('?FUN_0059f050@@YAXH@Z','?FUN_005a66a7@@YAHXZ')
TO=('?application_release_0059f050@porsche@@YAIPAX@Z','?formatter_lowio_doserrno_005a66a7@porsche@@YAPAIXZ')

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):
    path=Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def definition(data,name):
    start=data.index(name.encode());start=data.rfind(b'\n',0,start)+1
    at=data.index(b'{',start);level=1;end=at+1
    while level:
        level+=(data[end]==123)-(data[end]==125);end+=1
    return start,end+1,data[start:end+1]

FIXTURE=r'''#include "porsche/application_alloc.hpp"
#include "porsche/formatter_crt_runtime.hpp"
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);
void __cdecl FUN_0059f050(int);
int __cdecl FUN_005a66a7();
using U=std::uint32_t;
U fail259=0,release_cases259=0,dos_cases259=0,free_calls259=0,thread_calls259=0;
U save_sp259,save_bp259,save_bx259,save_si259,save_di259,save_slots259;
U seen_sp259,seen_bp259,seen_bx259,seen_si259,seen_di259,seen_ax259,clean_sp259;
U last_free_arg259=0;
alignas(16) unsigned char arena259[4096];void* thread_base259=arena259;
namespace porsche {
U __cdecl free_00531f90(void*p){++free_calls259;last_free_arg259=reinterpret_cast<U>(p);return last_free_arg259^0x8000a5f0u;}
void* __cdecl formatter_crt_thread_005a545c(){++thread_calls259;return thread_base259;}
struct Manager259 {U a,b;U (__cdecl*release)(void*);};
Manager259 table259={0,0,&free_00531f90};Manager259* manager259=&table259;
__declspec(naked) U __cdecl original_release259(void*){__asm{
 mov eax,dword ptr[esp+4]
 test eax,eax
 jz done259
 push eax
 mov eax,manager259
 call dword ptr[eax+8]
 pop ecx
done259:
 ret
}}
__declspec(naked) U __cdecl original_dos259(){__asm{
 call formatter_crt_thread_005a545c
 add eax,12
 ret
}}
}
void raw259(void*target,U arg,U slots){
 __asm{
 mov eax,target
 mov ecx,arg
 mov edx,slots
 mov save_slots259,edx
 mov save_sp259,esp
 mov save_bp259,ebp
 mov save_bx259,ebx
 mov save_si259,esi
 mov save_di259,edi
 test edx,edx
 jz nopush259
 push ecx
nopush259:
 mov ebx,0x176b92d3
 mov esi,0xa53c0481
 mov edi,0x59e0b72f
 mov ebp,0xc7138ae5
 call eax
 mov seen_ax259,eax
 mov seen_sp259,esp
 mov seen_bp259,ebp
 mov seen_bx259,ebx
 mov seen_si259,esi
 mov seen_di259,edi
 mov edx,save_slots259
 shl edx,2
 add esp,edx
 mov clean_sp259,esp
 mov ebp,save_bp259
 mov ebx,save_bx259
 mov esi,save_si259
 mov edi,save_di259
 mov esp,save_sp259
 }
 if(seen_sp259!=save_sp259-slots*4||clean_sp259!=save_sp259||seen_bp259!=0xc7138ae5u||seen_bx259!=0x176b92d3u||seen_si259!=0xa53c0481u||seen_di259!=0x59e0b72fu)++fail259;
}
extern "C" void __cdecl entry(){
 static_assert(sizeof(void*)==4&&sizeof(U)==4,"raw x86 fixture");
 if(reinterpret_cast<void*>(&FUN_0059f050)!=reinterpret_cast<void*>(&porsche::application_release_0059f050))++fail259;
 if(reinterpret_cast<void*>(&FUN_005a66a7)!=reinterpret_cast<void*>(&porsche::formatter_lowio_doserrno_005a66a7))++fail259;
 const U values[9]={0,1,0x7fu,0x80u,0xffu,0x7fffffffu,0x80000000u,0xfffffffeu,0xffffffffu};
 for(U i=0;i<9;++i){
  U value=values[i],expected=value?value^0x8000a5f0u:0u;
  void*targets[3]={reinterpret_cast<void*>(&FUN_0059f050),reinterpret_cast<void*>(&porsche::application_release_0059f050),reinterpret_cast<void*>(&porsche::original_release259)};
  for(U j=0;j<3;++j){U before=free_calls259;raw259(targets[j],value,1);if(seen_ax259!=expected||free_calls259!=before+(value?1u:0u)||(value&&last_free_arg259!=value))++fail259;}
  ++release_cases259;
 }
 for(U i=0;i<4096;++i)arena259[i]=0xa5;
 for(U i=0;i<512;++i){
  thread_base259=arena259+(i%128)*16;
  U expected=reinterpret_cast<U>(thread_base259)+12;
  void*targets[3]={reinterpret_cast<void*>(&FUN_005a66a7),reinterpret_cast<void*>(&porsche::formatter_lowio_doserrno_005a66a7),reinterpret_cast<void*>(&porsche::original_dos259)};
  for(U j=0;j<3;++j){U before=thread_calls259;raw259(targets[j],0,0);if(seen_ax259!=expected||thread_calls259!=before+1)++fail259;}
  ++dos_cases259;
 }
 for(U i=0;i<4096;++i)if(arena259[i]!=0xa5)++fail259;
 if(release_cases259!=9||dos_cases259!=512||free_calls259!=24||thread_calls259!=1536)++fail259;
 ExitProcess(fail259?1:0);
}
'''

def main(finalize,retry_failed_include):
    assert not (RUN/'summary.json').exists()
    if finalize:assert (OUT/'compile.execution.json').exists()
    elif retry_failed_include:
        failed=json.loads((OUT/'compile.execution.json').read_bytes())
        assert failed['exit_code']!=0 and b'C1083' in (OUT/'compile.log').read_bytes()
        assert not (OUT/'first-compile.execution.json').exists()
        (OUT/'first-compile.execution.json').write_bytes((OUT/'compile.execution.json').read_bytes())
        (OUT/'first-compile.log').write_bytes((OUT/'compile.log').read_bytes())
        (OUT/'first-captured-compile-driver.py').write_bytes((OUT/'captured-compile-driver.py').read_bytes())
    else:
        assert not OUT.exists();OUT.mkdir(parents=True)
    RUN.mkdir(parents=True,exist_ok=True);(RUN/'bindings').mkdir(exist_ok=True)
    pins={}
    def pin(path,expected=None):
        path=Path(path).resolve();sha=digest(path)
        assert expected is None or sha==expected,(path,sha,expected)
        pins[path]=sha;return path
    def guard():
        for path,sha in pins.items():assert digest(path)==sha,('input drift',path)
    def materialize(path,text):
        if finalize or retry_failed_include:assert path.read_bytes()==text.encode('utf8'),('source drift',path)
        else:path.write_text(text,encoding='utf8',newline='\n')
        return pin(path)
    def run(command,name):
        command=list(map(str,command));start=time.perf_counter()
        p=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
        elapsed=round(time.perf_counter()-start,6)
        log=OUT/(name+'.log');log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
        receipt=dict(command=command,exit_code=p.returncode,seconds=elapsed,log=relative(log),log_sha256=digest(log))
        write(OUT/(name+'.execution.json'),receipt)
        return receipt
    pin(Path(__file__))
    if finalize:pin(OUT/'captured-compile-driver.py')
    else:
        (OUT/'captured-compile-driver.py').write_bytes(Path(__file__).read_bytes())
        pin(OUT/'captured-compile-driver.py')
    if retry_failed_include:
        pin(OUT/'first-compile.execution.json');pin(OUT/'first-compile.log');pin(OUT/'first-captured-compile-driver.py')
    h=module('h259',pin(ROOT/'scripts/research/experiment-v2-readonly-scalars-221.py'))
    abi=module('abi259',pin(ROOT/'scripts/research/experiment-v2-thiscall-186.py'))
    coff=module('coff259',pin(ROOT/'scripts/research/build-v2-compile-corpus.py'))
    audit=module('audit259',pin(RUNS/'226-writable-scalar-storage/audit.py'))
    parse=module('parse259',pin(ROOT/'scripts/research/audit-v2-nested-calls-229.py'))
    queue=json.loads(pin(RUNS/'256-automated-frontier-refresh/summary.json').read_bytes())
    baseline=json.loads(pin(RUNS/'249-canonical-and-storage-union/summary.json').read_bytes())
    registry=json.loads(pin(ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json').read_bytes())['functions']
    catalog={r['entry_va']:r for r in abi.rows(pin(abi.CORPUS/'functions.jsonl'))}
    index=abi.instruction_index();pin(abi.CORPUS/'disassembly.asm')
    image=pin(ROOT/'local/game/Porsche.exe',SHA).read_bytes();sections=h.sections(image)
    def file_offset(va):
        sec=next(s for s in sections if s['va']<=va<s['va']+s['rawsize'])
        return sec['raw']+va-sec['va']
    proof_rows={};consumer_proof=[]
    for va,fr in zip(VAS,FROM):
        task=next(t for t in queue['tasks'] if t.get('original_va')==va and t['action']=='accepted_owner_reuse_review')
        assert task['native_symbols']==[fr] and task['indexed_entry_known']
        own=[r for r in registry if r.get('module')=='Porsche.exe' and r.get('entry_va')==va]
        assert len(own)==1 and own[0]['source']==task['accepted_owners'][0]['source']
        ins=abi.function_instructions(catalog[va],index)
        assert len(catalog[va]['ranges'])==1 and catalog[va]['ranges'][0][0]==va
        assert sum(len(i['bytes'])//2 for i in ins)==task['original_body_bytes']==(19 if va==VAS[0] else 9)
        for row in ins:
            pc=int(row['va'],16);raw=bytes.fromhex(row['bytes'])
            assert image[file_offset(pc):file_offset(pc)+len(raw)]==raw
        proof_rows[va]=ins
        frontier=[r for r in baseline['frontier'] if r.get('va')==va]
        assert len(frontier)==1 and frontier[0]['symbol']==fr
        for caller in frontier[0]['referring_object_vas']:
            result=next(r for r in baseline['results'] if r['va']==caller)
            obj=pin(ROOT/result['object'],result['object_sha256'])
            actual=coff.coff_symbols(obj);assert fr in actual['undefined']
            for name in result['include_closure']:pin(ROOT/name,baseline['input_sha256'][name])
            consumer_proof.append(dict(va=va,caller=caller,object=relative(obj),sha256=digest(obj),undefined=fr))
    # Audit the misleading char view before any alias allocation.
    deferred=next(t for t in queue['tasks'] if t.get('original_va')=='005925d0' and t['action']=='accepted_owner_reuse_review')
    defer_ins=abi.function_instructions(catalog['005925d0'],index)
    assert any(i['instruction'].upper()=='XOR ECX,ECX' for i in defer_ins)
    assert any(i['instruction'].upper()=='MOV EAX,ECX' for i in defer_ins)
    assert any(i['instruction'].upper()=='XOR EAX,EAX' for i in defer_ins)
    caller=next(r for r in baseline['results'] if r['va']=='00568ae0')
    caller_obj=pin(ROOT/caller['object'],caller['object_sha256'])
    assert '?FUN_005925d0@@YADI@Z' in coff.coff_symbols(caller_obj)['undefined']
    assert b'\xe8\0\0\0\0\x83\xc4\x04\x0f\xbe\xc8' in caller_obj.read_bytes(),'Actual caller must sign-extend AL after call'
    for path in [abi.COMPILER,abi.COMPILER.with_name('c1xx.dll'),abi.COMPILER.with_name('c2.dll'),abi.COMPILER.with_name('link.exe')]:pin(path)
    pin(Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib'))
    canonical_root=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe'
    canonical={'0059f050':pin(canonical_root/'application_alloc.cpp').read_bytes(),
               '005a66a7':pin(canonical_root/'formatter_crt_runtime.cpp').read_bytes()}
    include_root=ROOT/'iterations/v2/001-original-recovery/source/include'
    # Pre-pin the project's entire current header closure; actual MSVC includes are narrowed below.
    for path in include_root.rglob('*.hpp'):pin(path)
    old=json.loads(pin(RUNS/'247-canonical-reuse-batch/summary.json').read_bytes())
    for name,sha in old['input_sha256'].items():
        path=Path(name)
        if not path.is_absolute():path=ROOT/path
        if path.suffix.lower() in ('.h','.hpp') and path.exists():pin(path,sha if digest(path)==sha else None)
    fragments={};sources={}
    for va,name in zip(VAS,NAMES):
        raw=canonical[va];prefix_end=raw.index(b'namespace porsche {')
        start,end,body=definition(raw,name)
        parts=[dict(kind='canonical_slice',offset=0,length=prefix_end,sha256=hashlib.sha256(raw[:prefix_end]).hexdigest(),text=raw[:prefix_end].decode('utf8')),
               dict(kind='wrapper',text='namespace porsche {\n'),
               dict(kind='canonical_slice',offset=start,length=end-start,sha256=hashlib.sha256(body).hexdigest(),text=body.decode('utf8')),
               dict(kind='wrapper',text='}\n')]
        fragments[va]=dict(canonical_source=relative(canonical_root/('application_alloc.cpp' if va==VAS[0] else 'formatter_crt_runtime.cpp')),parts=parts)
        sources[va]=materialize(OUT/(va+'.cpp'),''.join(p['text'] for p in parts))
    directives={va:'/alternatename:'+fr+'='+to for va,fr,to in zip(VAS,FROM,TO)}
    supports={va:materialize(OUT/('binding_'+va+'.cpp'),'#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4&&sizeof(int)==4,"raw32 ABI");\n#pragma comment(linker,"'+directives[va]+'")\n') for va in VAS}
    fixture=materialize(OUT/'native-fixture.cpp',FIXTURE)
    proof=dict(schema=1,original_sha256=SHA,selected_vas=list(VAS),original_instructions=proof_rows,canonical_fragments=fragments,actual_native_consumers=consumer_proof,
        deferred_005925d0=dict(original_va='005925d0',original_bytes=57,original_zero_extends_device_byte=True,native_symbol='?FUN_005925d0@@YADI@Z',actual_consumer_object=relative(caller_obj),actual_consumer_sha256=digest(caller_obj),actual_consumer_instruction='movsx ecx,al after call',reason='Signed char promotion in native consumer diverges for 0x80..0xff; no alias or substitute'),
        ABI=dict(release='raw void(int) caller ignores return; canonical uint32(void*) preserves full EAX/RET0 and delegates accepted free_00531f90',doserrno='raw int(void) caller casts full EAX to pointer; canonical uint32*(void) preserves pointer bits/RET0 and calls accepted CRT thread provider'),
        limits=['Exact canonical fragments only; controlled fixture providers are not real game providers','No production/union change or new accepted algorithm'])
    if finalize or retry_failed_include:assert json.loads((RUN/'proof-before-compile.json').read_bytes())==proof
    else:write(RUN/'proof-before-compile.json',proof)
    pin(RUN/'proof-before-compile.json')
    objects=OUT/'objects';deps=OUT/'dependencies'
    if not finalize and not retry_failed_include:objects.mkdir();deps.mkdir()
    flags=['/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/sourceDependencies',str(deps)]
    include_roots=[ROOT/name for name in old['results'][0]['include_directories']]
    assert include_roots[0]==include_root
    command=[abi.COMPILER,*flags,*[item for root in include_roots for item in ('/I',root)],'/Fo'+str(objects)+os.sep,*sources.values(),*supports.values(),fixture]
    if finalize:
        prepared=json.loads(pin(OUT/'prepare.json').read_bytes())
        for name,sha in prepared['input_sha256'].items():
            historic=OUT/'first-native-fixture.cpp' if name==relative(fixture) and (OUT/'first-native-fixture.cpp').exists() else ROOT/name
            pin(OUT/'captured-compile-driver.py' if name==relative(Path(__file__)) else historic,sha)
        compiled=json.loads(pin(OUT/'compile.execution.json').read_bytes())
        assert compiled['command']==list(map(str,command))
        pin(ROOT/compiled['log'],compiled['log_sha256'])
    else:
        guard()
        write(OUT/'prepare.json',dict(command=list(map(str,command)),input_sha256={relative(p):sha for p,sha in pins.items()}))
        compiled=run(command,'compile')
    assert compiled['exit_code']==0,(OUT/'compile.log').read_text(errors='replace')
    warnings=re.findall(rb'warning ([CD]\d+)',(OUT/'compile.log').read_bytes())
    assert not re.search(rb'error [CD]\d+',(OUT/'compile.log').read_bytes())
    actual_headers={};dependency_reports={};postcompile_header_pins=[]
    for source in [*sources.values(),*supports.values(),fixture]:
        path=pin(deps/(source.name+'.json'));report=json.loads(path.read_bytes())
        assert report['Version']=='1.2' and Path(report['Data']['Source']).resolve()==source
        includes={Path(s).resolve() for s in report['Data']['Includes']}
        for header in includes-set(pins):
            assert any(header.is_relative_to(root) for root in include_roots),('unexpected include root',header)
            pin(header);postcompile_header_pins.append(relative(header))
        actual_headers[source]=includes;dependency_reports[source]=path
    results=[];support_rows=[];aliases=[]
    for va,fr,to in zip(VAS,FROM,TO):
        obj=objects/(va+'.obj');symbols=coff.coff_symbols(obj)
        assert symbols['defined']==[to]
        results.append(dict(va=va,name=NAMES[VAS.index(va)],compiled=True,canonical_reuse=True,compiler_exit_code=0,code_generation_succeeded=True,actual_i386_coff_validated=True,owned_error_count=0,owned_warning_count=0,generated_source=relative(sources[va]),generated_source_sha256=digest(sources[va]),dependency_sha256={relative(p):pins[p] for p in actual_headers[sources[va]]|{sources[va]}},forced_headers=[],include_directories=[relative(root) for root in include_roots],compiler_command=list(map(str,command)),compiler_execution_receipt=relative(OUT/'compile.execution.json'),source_dependencies=relative(dependency_reports[sources[va]]),source_dependencies_sha256=digest(dependency_reports[sources[va]]),object=relative(obj),object_sha256=digest(obj),symbols=symbols,defined_external_symbols=symbols['defined'],undefined_external_symbols=symbols['undefined']))
        binding=objects/('binding_'+va+'.obj');binding_symbols=coff.coff_symbols(binding)
        assert not any(binding_symbols.values())
        parsed=audit.coff(binding);section=next(s for s in parsed['sections'] if s['name']=='.drectve')
        directive=parsed['bytes'][section['raw']:section['raw']+section['size']].decode('ascii').strip()
        assert directive==directives[va]
        support_rows.append(dict(id='canonical-reuse-binding-'+va,generated_source=relative(supports[va]),generated_source_sha256=digest(supports[va]),object=relative(binding),object_sha256=digest(binding),dependency_sha256={relative(supports[va]):digest(supports[va])},symbols=binding_symbols,directive=directive,function_count=0))
        aliases.append(dict(**{'from':fr,'to':to},va=va,support_object_id='canonical-reuse-binding-'+va,directive=directive,proof=dict(original_sha256=SHA,ret_pop_bytes=0,representation='one x86 DWORD argument, full EAX preserved' if va==VAS[0] else 'zero argument, EAX pointer bits preserved',exact_fragment_evidence=relative(RUN/'proof-before-compile.json'))))
    fixture_obj=objects/'native-fixture.obj'
    oracle=[]
    for va,fragment in zip(VAS,('original_release259','original_dos259')):
        symbols=coff.coff_symbols(fixture_obj)
        names=[s for s in symbols['defined'] if fragment in s]
        assert len(names)==1,names
        body,relocs=parse.coff_function(fixture_obj,names[0])
        expected=bytearray.fromhex(''.join(i['bytes'] for i in proof_rows[va]))
        offsets=[10] if va==VAS[0] else [1]
        assert len(relocs)==1 and relocs[0]['offset']==offsets[0] and relocs[0]['type']==(6 if va==VAS[0] else 20),relocs
        expected[offsets[0]:offsets[0]+4]=bytes(4)
        assert body==bytes(expected),(va,body.hex(),expected.hex())
        oracle.append(dict(va=va,symbol=names[0],bytes=len(body),relocations=relocs,normalized_exact=True))
    exe=OUT/'native-fixture.exe';mapfile=OUT/'native-fixture.map';kernel=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0/um/x86/kernel32.lib')
    stale_link=exe.exists() and fixture_obj.stat().st_mtime_ns>exe.stat().st_mtime_ns
    if stale_link and (OUT/'fixture-link.execution.json').exists():
        for path in [OUT/'fixture-link.execution.json',OUT/'fixture-link.log',exe,mapfile]:
            shutil.copyfile(path,OUT/('second-'+path.name))
    if finalize and not stale_link and (OUT/'fixture-link.execution.json').exists() and json.loads((OUT/'fixture-link.execution.json').read_bytes())['exit_code']==0:linked=json.loads(pin(OUT/'fixture-link.execution.json').read_bytes())
    else:linked=run([abi.COMPILER.with_name('link.exe'),'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(mapfile),*[objects/(va+'.obj') for va in VAS],*[objects/('binding_'+va+'.obj') for va in VAS],fixture_obj,kernel],'fixture-link')
    assert linked['exit_code']==0,(OUT/'fixture-link.log').read_text(errors='replace')
    if finalize and (OUT/'fixture-native.execution.json').exists() and json.loads((OUT/'fixture-native.execution.json').read_bytes())['exit_code']==0:native=json.loads(pin(OUT/'fixture-native.execution.json').read_bytes())
    else:native=run([exe],'fixture-native')
    assert native['exit_code']==0
    for p in [*objects.glob('*.obj'),exe,mapfile,*OUT.glob('*.log'),*OUT.glob('*.execution.json'),*deps.glob('*.json')]:pin(p)
    guard();manifest={relative(p):sha for p,sha in pins.items()}
    limits=['Existing canonical bodies copied byte-for-byte; controlled provider fixture only','005925d0 char view deferred due actual signed extension in native caller','No production/union change, whole provider composition or game acceptance']
    first_receipt=json.loads((OUT/'first-compile.execution.json').read_bytes()) if (OUT/'first-compile.execution.json').exists() else None
    repair=json.loads((OUT/'fixture-repair-compile.execution.json').read_bytes()) if (OUT/'fixture-repair-compile.execution.json').exists() else None
    summary=dict(schema=1,kind='canonical-body-reuse-batch',original_sha256=SHA,objects_compiled=2,real_coff_objects=2,results=results,compiled_vas=list(VAS),new_distinct_function_VAs=2,actual_compiler_batches=(2 if first_receipt else 1)+(2 if (OUT/'first-fixture-repair-compile.execution.json').exists() else 1 if repair else 0),actual_MP6_requested=True,showIncludes_disabled=False,changed_game_TUs=2,handwritten_game_algorithm_TUs=0,directive_only_support_TUs=2,synthetic_fixture_TUs=1,compiler_batch_exit_code=0,compile_seconds=compiled['seconds'],first_compile_failure=dict(receipt=relative(OUT/'first-compile.execution.json'),exit_code=first_receipt['exit_code'],reason='Missing pinned MSVC/SDK include roots caused C1083') if first_receipt else None,first_fixture_link_failure=relative(OUT/'first-fixture-link.execution.json') if repair else None,fixture_repair_compile=relative(OUT/'fixture-repair-compile.execution.json') if repair else None,fixture_repair_history=[relative(OUT/n) for n in ('first-fixture-repair-compile.execution.json','first-fixture-native.execution.json','second-fixture-link.execution.json','second-fixture-native.execution.json') if (OUT/n).exists()],resumed_existing_successful_compile=finalize,recompilations=(1 if first_receipt else 0)+(2 if (OUT/'first-fixture-repair-compile.execution.json').exists() else 1 if repair else 0),captured_compile_driver=relative(OUT/'captured-compile-driver.py'),compiler_sha256=digest(abi.COMPILER),compiler_flags=flags,compiler_command=list(map(str,command)),compiler_execution_receipt=relative(OUT/'compile.execution.json'),compiler_log=relative(OUT/'compile.log'),compiler_log_sha256=digest(OUT/'compile.log'),compiler_warnings=dict(game=0,driver=0,fixture=[w.decode() for w in warnings]),actual_header_counts={va:len(actual_headers[sources[va]]) for va in VAS},postcompile_header_pins=sorted(set(postcompile_header_pins)),source_dependencies_format='MSVC1.2',input_sha256=manifest,input_guards_before=True,input_guards_after=True,original_selected_bytes=28,production_ready=False,production_or_union_changes=False,fixture=dict(cases=521,release_cases=9,doserrno_cases=512,native_exit_code=0,seconds=native['seconds'],executable=relative(exe),executable_sha256=digest(exe),alias_identity=True,EAX_full_return=True,ESP_nonvolatile=True),oracle=oracle,deferred=[proof['deferred_005925d0']],limits=limits)
    write(RUN/'summary.json',summary)
    bindings=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=SHA,compiler_sha256=digest(abi.COMPILER),new_function_count=0,support_objects=support_rows,aliases=aliases,compiler_batch_exit_code=0,input_sha256={**manifest,relative(RUN/'summary.json'):digest(RUN/'summary.json')},compiler_command=list(map(str,command)),compiler_execution_receipt=relative(OUT/'compile.execution.json'),ordinary_summary=relative(RUN/'summary.json'),ordinary_summary_sha256=digest(RUN/'summary.json'),production_ready=False,limits=limits)
    write(RUN/'bindings/summary.json',bindings)
    print(json.dumps(dict(ordinary=2,bindings=2,compile_exit=compiled['exit_code'],compile_seconds=compiled['seconds'],native_exit=native['exit_code'],pins=len(pins))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--finalize-existing',action='store_true');p.add_argument('--retry-failed-include',action='store_true')
    args=p.parse_args();assert not (args.finalize_existing and args.retry_failed_include)
    main(args.finalize_existing,args.retry_failed_include)

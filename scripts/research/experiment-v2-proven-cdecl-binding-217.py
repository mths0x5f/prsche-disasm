"""One proven unused-argument cdecl link edge; no new game body/function."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib, importlib.util, json, os, re, struct, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; RUNS=ROOT/'iterations/v2/001-original-recovery/runs'
RUN=RUNS/'217-proven-cdecl-binding'; OUT=ROOT/'local/experiments/v2-proven-cdecl-binding-217/final'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
FROM='?FUN_00590290@@YAIII@Z'; TO='?FUN_00590290@@YAIXZ'; ID='cdecl-binding-00590290'
DIRECTIVE='/alternatename:'+FROM+'='+TO
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix()
def write(path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


FIXTURE=r'''typedef unsigned int u32;
static_assert(sizeof(void*)==4 && sizeof(u32)==4,"x86 raw32 contract");
extern "C" __declspec(dllimport) void __stdcall ExitProcess(u32);
u32 __cdecl FUN_00590290();
u32 __cdecl FUN_00590290(u32,u32);
volatile u32 failures,checks,cases,typed_calls,raw_calls;
volatile u32 save_sp,save_bp,save_bx,save_si,save_di,seen_sp,clean_sp,seen_bp,seen_bx,seen_si,seen_di,seen_eax;
void require(bool value){++checks;if(!value)++failures;}
// Exact original33c0c3, test reference only; never a production body.
__declspec(naked) void original_reference(){__asm { xor eax,eax
 ret }}
__declspec(noinline) u32 typed_edge(u32 a,u32 b){u32 before,after,answer;
 __asm mov before,esp
 answer=FUN_00590290(a,b);
 __asm mov after,esp
 ++typed_calls;require(before==after);require(answer==0);return answer;
}
__declspec(noinline) u32 raw_edge(void* target,u32 a,u32 b){
 __asm {
 mov save_sp,esp
 mov save_bp,ebp
 mov save_bx,ebx
 mov save_si,esi
 mov save_di,edi
 mov eax,target
 push b
 push a
 mov ebx,0x176b92d3
 mov esi,0xa53c0481
 mov edi,0x59e0b72f
 mov ebp,0xc7138ae5
 call eax
 mov seen_eax,eax
 mov seen_sp,esp
 mov seen_bp,ebp
 mov seen_bx,ebx
 mov seen_si,esi
 mov seen_di,edi
 add esp,8
 mov clean_sp,esp
 mov ebp,save_bp
 mov ebx,save_bx
 mov esi,save_si
 mov edi,save_di
 mov esp,save_sp
 }
 ++raw_calls;
 require(seen_eax==0);require(seen_sp==save_sp-8);require(clean_sp==save_sp);
 require(seen_bp==0xc7138ae5u);require(seen_bx==0x176b92d3u);
 require(seen_si==0xa53c0481u);require(seen_di==0x59e0b72fu);
 return seen_eax;
}
void one_case(void* actual,void* original,u32 a,u32 b){
 ++cases;typed_edge(a,b);u32 x=raw_edge(actual,a,b);u32 y=raw_edge(original,a,b);require(x==y);
}
extern "C" void __cdecl entry(){
 u32 (__cdecl *typed)(u32,u32)=&FUN_00590290;
 u32 (__cdecl *zero)()=&FUN_00590290;
 void*actual=reinterpret_cast<void*>(typed);void*cached=reinterpret_cast<void*>(zero);
 void*original=reinterpret_cast<void*>(&original_reference);
 require(actual==cached);
 const u32 values[]={0,1,0x7fffffffu,0x80000000u,0xffffffffu,0x13579bdfu,0xa55a5aa5u,0xdeadbeefu};
 for(u32 i=0;i<8;++i)for(u32 j=0;j<8;++j)one_case(actual,original,values[i],values[j]);
 u32 state=0x90290217u;
 for(u32 i=0;i<1024;++i){state=state*1664525u+1013904223u;u32 a=state;state=state*1664525u+1013904223u;one_case(actual,original,a,state);}
 if(cases!=1088 || typed_calls!=1088 || raw_calls!=2176 || checks!=18497)++failures;
 ExitProcess(failures?1:0);
}
'''


def coff_sections(path):
    data=path.read_bytes(); machine,n,_,_,_,optional,_=struct.unpack_from('<HHIIIHH',data); assert machine==0x14c and optional==0
    result=[]
    for i in range(n):
        off=20+40*i; name=data[off:off+8].rstrip(b'\0').decode(); size,raw,reloc=struct.unpack_from('<III',data,off+16); count=struct.unpack_from('<H',data,off+32)[0]
        result.append(dict(name=name,bytes=data[raw:raw+size].hex(),relocations=count))
    return result


def main():
    begun=time.perf_counter(); assert not OUT.exists() or not any(OUT.iterdir()); assert not (RUN/'summary.json').exists()
    for p in (RUN,OUT,OUT/'sources',OUT/'objects',OUT/'logs'): p.mkdir(parents=True,exist_ok=True)
    pins={}
    def read(path,expected=None):
        path=Path(path).resolve(); raw=path.read_bytes(); actual=hashlib.sha256(raw).hexdigest()
        if expected: assert actual==expected,('stale input',path)
        assert path not in pins or pins[path]==actual; pins[path]=actual; return raw
    read(Path(__file__))
    baseline_path=RUNS/'216-sound-consumer-union/summary.json'; baseline=json.loads(read(baseline_path)); assert baseline['original_sha256']==SHA
    target=next(r for r in baseline['results'] if r['va']=='00590290'); cached=ROOT/target['object']; read(cached,target['object_sha256'])
    read(ROOT/target['generated_source'],target['generated_source_sha256'])
    for name in target['include_closure']:
        expected=baseline['input_sha256'][name]; read(ROOT/name,expected)
    parserpath=ROOT/'scripts/research/build-v2-compile-corpus.py'; parser=module('coff217',parserpath); read(parserpath)
    assert parser.coff_symbols(cached)==target['symbols'] and target['symbols']['defined']==[TO] and not target['symbols']['undefined']
    cached_sections=coff_sections(cached); text_sections=[s for s in cached_sections if s['name'].startswith('.text') and s['bytes']]
    assert len(text_sections)==1 and text_sections[0]['bytes']=='558bec33c05dc3' and text_sections[0]['relocations']==0
    # Actual cached body: PUSH EBP;MOV EBP,ESP;XOR EAX,EAX;POP EBP;RET0.
    # No argument read; only EBP is touched and restored, other nonvolatiles untouched.
    contract_path=RUNS/'211-direct-call-contracts/summary.json'; contract=json.loads(read(contract_path)); assert contract['original_sha256']==SHA
    evidence_path=ROOT/contract['evidence']; evidence=json.loads(read(evidence_path,contract['evidence_sha256']))
    edge=next(c for c in evidence['contracts'] if c['callee']=='00590290')
    assert edge['pushed_stack_bytes']==8 and edge['callee_local_inputs']==[] and edge['callee_unused_stack_offsets']==[4,8]
    assert edge['caller_cleanup']['bytes']=='83c408' and ''.join(r['bytes'] for r in evidence['instructions']['00590290'])=='33c0c3'
    catalog_path=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'; catalog={r['entry_va']:r for r in map(json.loads,read(catalog_path).decode().splitlines())}
    manual_path=ROOT/'research/binary-index/manual-functions.jsonl'
    for r in map(json.loads,read(manual_path).decode().splitlines()):
        if r['module']=='Porsche.exe': catalog[r['entry_va']]=r
    registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json'; registry=json.loads(read(registry_path))['functions']; owners=[]
    for owner in registry:
        if owner['module']!='Porsche.exe':continue
        assert owner['entry_va'] in catalog
        if any(int(a,16)<=0x590290<=int(b,16) for a,b in catalog[owner['entry_va']]['ranges']):owners.append(owner)
    assert not owners,'Existing compiled candidate is not a recovered implementation owner'
    wip=[]
    for path in sorted((ROOT/'iterations/v2/001-original-recovery/source/recovered').rglob('*.cpp')):
        text=path.read_text(encoding='utf8')
        if '00590290' not in text:continue
        read(path)
        for m in re.finditer(r'\b([A-Za-z_]\w*_00590290)\s*\([^;{}]*\)\s*\{',text):wip.append(dict(source=relative(path),name=m[1]))
    assert not wip
    tools=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'; compiler=tools/'bin/Hostx64/x86/cl.exe'; linker=compiler.with_name('link.exe')
    for name in ('cl.exe','c1xx.dll','c2.dll','link.exe'):read(compiler.parent/name)
    assert sha(compiler)==contract['compiler_sha256']
    sdk=ROOT/'local/tools/Windows Kits/10/Lib'
    if not sdk.exists():sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib')
    kernel=sorted(sdk.glob('*/um/x86/kernel32.lib'))[-1];read(kernel)
    assert not any(os.environ.get(k) for k in ('CL','_CL_','LINK','_LINK_'))
    support_source=OUT/'sources/cdecl_binding_00590290.cpp'
    support_source.write_text('#ifndef _M_IX86\n#error x86 only\n#endif\nstatic_assert(sizeof(void*)==4,"raw32 pointer width");\n#pragma comment(linker,"'+DIRECTIVE+'")\n',encoding='utf8',newline='\n')
    fixture_source=OUT/'sources/native_fixture.cpp'; fixture_source.write_text(FIXTURE,encoding='utf8',newline='\n')
    read(support_source);read(fixture_source)
    flags=['/nologo','/c','/Od','/Oy-','/Gy','/GS-','/GR-','/EHs-c-','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl']
    rsp=OUT/'logs/native.rsp';rsp.write_text('\n'.join('"'+s+'"' for s in flags+['/Fo'+(OUT/'objects').as_posix()+'/',str(support_source),str(fixture_source)])+'\n',encoding='utf-8-sig',newline='\n')
    def guard():
        def check(item):p,h=item;assert sha(p)==h,('input mutation',p)
        with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(check,pins.items()))
    guard();prepare=OUT/'prepare.json';write(prepare,dict(before_guard_pass=True,input_sha256={relative(p) if p.is_relative_to(ROOT) else str(p):h for p,h in pins.items()},response_sha256=sha(rsp)))
    env={**os.environ,'VSLANG':'1033'}
    def run(command,label):
        before=time.perf_counter();p=subprocess.run([str(s) for s in command],cwd=OUT,capture_output=True,env=env,timeout=120);seconds=time.perf_counter()-before
        raw=p.stdout+p.stderr
        try:text=raw.decode('utf8')
        except UnicodeDecodeError:text=raw.decode('cp1251')
        log=OUT/'logs'/(label+'.log');log.write_text(text.replace('\r\n','\n'),encoding='utf8',newline='\n')
        result=dict(command=[str(s) for s in command],observed_exit_code=p.returncode,seconds=round(seconds,6),log=relative(log),log_sha256=sha(log))
        write(OUT/(label+'-capture.json'),result) # Persist result before parsing/assertion.
        return result,text
    compilation,compile_log=run([compiler,'@'+str(rsp)],'compile');assert compilation['observed_exit_code']==0,compile_log
    support=OUT/'objects/cdecl_binding_00590290.obj';fixture=OUT/'objects/native_fixture.obj'
    support_symbols=parser.coff_symbols(support);assert all(not v for v in support_symbols.values()),support_symbols
    support_sections=coff_sections(support);directive_sections=[bytes.fromhex(s['bytes']).decode() for s in support_sections if s['name']=='.drectve']
    assert len(directive_sections)==1 and directive_sections[0].strip()==DIRECTIVE
    assert not any(s['bytes'] for s in support_sections if s['name'].startswith('.text'))
    fixture_symbols=parser.coff_symbols(fixture);assert FROM in fixture_symbols['undefined'] and TO in fixture_symbols['undefined']
    assert any(s['bytes']=='33c0c3' for s in coff_sections(fixture) if s['name'].startswith('.text'))
    exe=OUT/'native_fixture.exe';map_path=OUT/'native_fixture.map'
    link_result,link_log=run([linker,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/ENTRY:entry','/NODEFAULTLIB','/INCREMENTAL:NO','/OPT:NOREF','/OUT:'+str(exe),'/MAP:'+str(map_path),fixture,support,cached,kernel],'link')
    assert link_result['observed_exit_code']==0 and exe.exists(),link_log
    native_result,native_log=run([exe],'native');assert native_result['observed_exit_code']==0,native_log
    guard()
    alias=dict(**{'from':FROM,'to':TO},va='00590290',support_object_id=ID,directive=DIRECTIVE,
        proof=dict(original_sha256=SHA,original_body_hex='33c0c3',cached_body_hex='558bec33c05dc3',cached_object=relative(cached),cached_object_sha256=sha(cached),
            caller='00565cd0',callsite='00565d07',caller_passed_bytes=8,caller_cleanup_bytes=8,callee_ret_pop_bytes=0,unused_stack_offsets=[4,8],
            cached_inputs=[],original_call_evidence=relative(evidence_path),original_call_evidence_sha256=sha(evidence_path),native_fixture_cases=1088,
            native_checks=18497,typed_calls=1088,cached_raw_calls=1088,original_asm_reference_calls=1088,native_exit=0,
            boundary='One exact raw32 cdecl edge only; no generic alias, implementation owner replacement, or full caller fidelity claim'))
    support_row=dict(id=ID,generated_source=relative(support_source),generated_source_sha256=sha(support_source),object=relative(support),object_sha256=sha(support),
        dependency_sha256={relative(support_source):sha(support_source)},symbols=support_symbols,compiler_flags=flags,directive=DIRECTIVE,function_count=0)
    report=dict(schema=1,kind='proven-link-contract',module='Porsche.exe',original_sha256=SHA,compiler_sha256=sha(compiler),new_function_count=0,
        support_objects=[support_row],aliases=[alias],input_sha256={relative(p) if p.is_relative_to(ROOT) else str(p):h for p,h in pins.items()},
        ownership=dict(canonical_exact_or_interior=owners,wip_implementations=wip,cached_candidate_reused_without_replacement=True),
        cached_target=target,cached_body_sections=cached_sections,actual_support_directive=directive_sections[0],
        compiler_response=relative(rsp),compiler_response_sha256=sha(rsp),native_commands=dict(compile=compilation,link=link_result,native=native_result),
        fixture=dict(source=relative(fixture_source),source_sha256=sha(fixture_source),object=relative(fixture),object_sha256=sha(fixture),symbols=fixture_symbols,
            exe=relative(exe),exe_sha256=sha(exe),map=relative(map_path),map_sha256=sha(map_path),cases=1088,checks=18497),
        elapsed_seconds=round(time.perf_counter()-begun,3),limits=['Single weak-link directive, no game body or added function.',
            'Native private fixture uses actual cached COFF plus original assembly only as a test reference. No production/wholeunion link.',
            'Full caller algorithm/flags/provider/nativegame fidelity remains backlog. Alias cannot be generalized to other addresses/signatures.'])
    write(RUN/'summary.json',report)
    write(RUN/'validation.json',dict(schema=1,summary_sha256=sha(RUN/'summary.json'),source_script_sha256=sha(Path(__file__)),input_guards_before_after=True,
        actual_cached_coff_body_and_symbols_pass=True,exact_one_directive_no_text_pass=True,new_function_count=0,native_fixture_exit=0,
        typed_actual_target_address_identity_pass=True,eax_esp_nonvolatile_preservation_pass=True,fixture_cases=1088,fixture_checks=18497,whole_union_link_commands=0))
    print(json.dumps(dict(support_objects=1,new_functions=0,fixture_cases=1088,fixture_checks=18497,exit_codes={k:v['observed_exit_code'] for k,v in report['native_commands'].items()},elapsed_seconds=report['elapsed_seconds']),indent=2))


if __name__=='__main__':main()

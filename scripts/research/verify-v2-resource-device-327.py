"""Run327: native original-chain/ABI checks for resource device routing.

The original 35B route calls the original 27B prefix. Only the AL-returning
005916a0 boundary and a recording wrapper around the accepted character search
are controlled. The search TU is compiled from its canonical source with a
fixture-only symbol rename; its algorithm is unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/327-resource-open-callback-evidence'
BASE=ROOT/'local/experiments/v2-resource-open-327'
PE=ROOT/'local/game/Porsche.exe'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE=RUN/'resource_device_327.cpp'
HEADER=RUN/'resource_device_327.hpp'
CANONICAL=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/formatter_search.cpp'

FIXTURE=r'''
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include "resource_device_327.hpp"
using U=std::uint32_t;
static_assert(sizeof(void*)==4,"x86 fixture");
static const unsigned char route_bytes[35]={@ROUTE@};
static const unsigned char prefix_bytes[27]={@PREFIX@};
struct Event { U kind,arg,character; };
static Event events[8]; static U count,raw_letter;
static void record(U kind,const char* path,U character) {
    if(count>=8) { std::puts("trace overflow"); ExitProcess(97); }
    events[count++]={kind,reinterpret_cast<U>(path),character};
}
extern "C" U __cdecl helper_raw(const char* path) {
    record(2,path,raw_letter); return raw_letter;
}
namespace porsche {
// The canonical TU also contains an unrelated locale-aware comparison. The
// linker requires these symbols even with /Gy /OPT:REF; no such function is
// exercised or claimed by this fixture. Any call fails instead of simulating it.
std::uint32_t formatter_text_locale_006afd80=0;
std::uint32_t formatter_text_locale_writer_006c02e4=0;
std::int32_t formatter_text_locale_readers_006c02e8=0;
void __cdecl exit_registry_lock_api_005a4ba4(std::uint32_t) {ExitProcess(96);}
void __cdecl exit_registry_unlock_api_005a4c05(std::uint32_t) {ExitProcess(96);}
std::int32_t __cdecl formatter_text_lower_inner_005a22b7(std::int32_t) {ExitProcess(96);}
const char* __cdecl fixture_canonical_search_005a2780(const char*,int);
const char* __cdecl formatter_search_character_005a2780(const char* path,int character) {
    record(1,path,static_cast<U>(character));
    return fixture_canonical_search_005a2780(path,character);
}
__declspec(naked) std::uint8_t __cdecl resource_drive_letter_005916a0(const char*) {
    __asm { jmp helper_raw }
}
}
struct Result {
    U esp0,esp1,ebp0,ebp1,ebx0,ebx1,esi0,esi1,edi0,edi1,eax,n;
    Event events[8];
};
static Result invoke(const void* fn,const char* path) {
    Result r{}; count=0;
    __asm {
        lea eax,r
        mov [eax+0],esp
        mov [eax+8],ebp
        mov ebx,13579bdfh
        mov esi,2468ace0h
        mov edi,6a31c5e7h
        mov [eax+16],ebx
        mov [eax+24],esi
        mov [eax+32],edi
        mov eax,path
        push eax
        mov ecx,fn
        call ecx
        add esp,4
        lea edx,r
        mov [edx+40],eax
        mov [edx+4],esp
        mov [edx+12],ebp
        mov [edx+20],ebx
        mov [edx+28],esi
        mov [edx+36],edi
    }
    r.n=count; for(U i=0;i<count;++i)r.events[i]=events[i];
    return r;
}
static bool abi(const Result& r) {
    return r.esp0==r.esp1 && r.ebp0==r.ebp1 && r.ebx0==r.ebx1 &&
           r.esi0==r.esi1 && r.edi0==r.edi1;
}
static bool same(const Result&a,const Result&b,U mask=0xffffffffu) {
    if(!abi(a)||!abi(b)||(a.eax&mask)!=(b.eax&mask)||a.n!=b.n)return false;
    for(U i=0;i<a.n;++i)
        if(a.events[i].kind!=b.events[i].kind || a.events[i].arg!=b.events[i].arg ||
           a.events[i].character!=b.events[i].character)return false;
    return true;
}
static bool patch(unsigned char* body,U original_va,U off,U target_va,const void* target) {
    if(body[off]!=0xe8)return false;
    if(original_va+off+5+*reinterpret_cast<U*>(body+off+1)!=target_va)return false;
    *reinterpret_cast<U*>(body+off+1)=reinterpret_cast<U>(target)-reinterpret_cast<U>(body+off+5);
    return true;
}
static U expected_prefix(U raw) {U low=raw&255;return low?low-0x40u:0;}
int main() {
    auto* slab=static_cast<unsigned char*>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
    if(!slab)return 90;
    for(U i=0;i<35;++i)slab[i]=route_bytes[i];
    for(U i=0;i<27;++i)slab[0x80+i]=prefix_bytes[i];
    if(!patch(slab,0x568e90,8,0x5a2780,reinterpret_cast<const void*>(&porsche::formatter_search_character_005a2780)) ||
       !patch(slab,0x568e90,21,0x591760,slab+0x80) ||
       !patch(slab+0x80,0x591760,5,0x5916a0,reinterpret_cast<const void*>(&porsche::resource_drive_letter_005916a0)))return 91;
    DWORD old=0;
    if(!VirtualProtect(slab,4096,PAGE_EXECUTE_READ,&old)||!FlushInstructionCache(GetCurrentProcess(),slab,4096))return 92;
    U passed=0;
    __declspec(align(16)) static char arena[128];
    const char* samples[]={"","plain.bin","|plain","a|b","a|","||","a\\b","x\0|"};
    for(U hi=0;hi<4;++hi)for(U low=0;low<256;++low) {
        const U highs[]={0,0xa5a50000u,0xffffff00u,0x80000000u};
        raw_letter=highs[hi]|low;
        const char* path="drive-prefix";
        Result a=invoke(slab+0x80,path);
        Result b=invoke(reinterpret_cast<const void*>(&porsche::resource_device_prefix_full_00591760),path);
        if(!same(a,b)||a.eax!=expected_prefix(raw_letter)||a.n!=1||a.events[0].arg!=reinterpret_cast<U>(path)) {
            std::printf("prefix divergence raw=%08x original=%08x cpp=%08x\n",raw_letter,a.eax,b.eax);return 10;
        }
        ++passed;
        Result c=invoke(reinterpret_cast<const void*>(&porsche::disk_path_device_00591760),path);
        if(!same(a,c,255u)) {std::puts("legacy AL adapter divergence");return 11;}
        ++passed;
    }
    for(U sample=0;sample<8;++sample)for(U alignment=0;alignment<4;++alignment)for(U low=0;low<256;++low) {
        for(U i=0;i<128;++i)arena[i]=static_cast<char>(0xa7);
        char* path=arena+16+alignment;
        const char* input=samples[sample];
        U j=0;do{path[j]=input[j];}while(input[j++]);
        if(sample==7) {path[2]='|';path[3]=0;}
        raw_letter=0xa5a50000u|low;
        bool separator=false;for(U i=0;path[i];++i)if(path[i]=='|')separator=true;
        Result a=invoke(slab,path);
        Result b=invoke(reinterpret_cast<const void*>(&porsche::file_device_name_00568e90),path);
        if(!same(a,b)||a.eax!=(separator?0u:expected_prefix(raw_letter))||a.n!=(separator?1u:2u)||
           a.events[0].kind!=1||a.events[0].arg!=reinterpret_cast<U>(path)||a.events[0].character!=0x7c) {
            std::printf("route divergence sample=%u align=%u low=%u original=%08x cpp=%08x events=%u/%u\n",sample,alignment,low,a.eax,b.eax,a.n,b.n);return 12;
        }
        ++passed;
    }
    std::printf("cases=%u failures=0 full_EAX_ESP_nonvolatile=PASS canonical_search=PASS\n",passed);
    return passed==10240?0:93;
}
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def relative(path):
    path=Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--attempt',type=int,required=True)
    parser.add_argument('--negative-controls',action='store_true')
    args=parser.parse_args()
    out=BASE/f'{args.attempt:03d}'
    assert not out.exists(),f'Immutable attempt already exists: {out}'
    out.mkdir(parents=True)
    (out/'dependencies').mkdir()
    utility=module('pe313',ROOT/'scripts/research/verify-v2-pr9-resource-313.py')
    utility.RUN=RUN
    coff=module('coff327',ROOT/'scripts/research/build-v2-compile-corpus.py')
    provenance=module('provenance327',ROOT/'scripts/research/audio_recovery_provenance.py')
    assert sha(PE)==SHA
    image=PE.read_bytes()
    route=utility.pe_at(image,0x568e90,35);prefix=utility.pe_at(image,0x591760,27)
    assert hashlib.sha256(route).hexdigest()=='39a3707f51099fd1ae5546253fe56fe0e6093bca1924cbd53d624f09bdfe6c0b'
    assert hashlib.sha256(prefix).hexdigest()=='acc20270b66ebca0881f491c3365e644e9f3a7f429fc621c9fa698bab4cc6dc9'
    for body,va,off,target in [(route,0x568e90,8,0x5a2780),(route,0x568e90,21,0x591760),(prefix,0x591760,5,0x5916a0)]:
        assert body[off]==0xe8 and va+off+5+struct.unpack_from('<i',body,off+1)[0]==target
    fixture=out/'native_fixture.cpp'
    fixture.write_text(FIXTURE.replace('@ROUTE@',','.join(map(str,route))).replace('@PREFIX@',','.join(map(str,prefix))),encoding='utf8',newline='\n')
    vc=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
    sdk=Path('C:/Program Files (x86)/Windows Kits/10');kit='10.0.26100.0'
    cl=vc/'bin/Hostx64/x86/cl.exe';link=cl.parent/'link.exe'
    includes=[RUN,ROOT/'iterations/v2/001-original-recovery/source/include',vc/'include',*[sdk/'Include'/kit/x for x in ('ucrt','shared','um')]]
    libs=[vc/'lib/x86/libcmt.lib',vc/'lib/x86/libvcruntime.lib',vc/'lib/x86/oldnames.lib',sdk/'Lib'/kit/'ucrt/x86/libucrt.lib',sdk/'Lib'/kit/'um/x86/kernel32.lib']
    pins={}
    def pin(path):
        path=Path(path).resolve();value=sha(path)
        if path in pins:assert pins[path]==value,f'input changed: {path}'
        pins[path]=value
    def guard():
        for path,value in pins.items():assert sha(path)==value,f'input changed: {path}'
    for path in [PE,Path(__file__),SOURCE,HEADER,CANONICAL,fixture,cl,link,cl.parent/'c1xx.dll',cl.parent/'c2.dll',*libs,ROOT/'scripts/research/verify-v2-pr9-resource-313.py',ROOT/'scripts/research/build-v2-compile-corpus.py',ROOT/'scripts/research/audio_recovery_provenance.py']:
        pin(path)
    for source in (SOURCE,CANONICAL,fixture):
        for path in utility.local_includes(source):pin(path)
    receipts={}
    def run(name,command):
        guard();start=time.perf_counter()
        process=subprocess.run(list(map(str,command)),cwd=out,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
        log=out/(name+'.log');log.write_bytes(process.stdout+process.stderr)
        record=dict(command=list(map(str,command)),exit_code=process.returncode,seconds=round(time.perf_counter()-start,6),log=relative(log),log_sha256=sha(log))
        write(out/(name+'.execution.json'),record);receipts[name]=record
        guard();return record
    common=[cl,'/nologo','/c','/TP','/std:c++17','/Od','/Oy-','/Gy','/GS-','/GR-','/EHsc','/W4','/utf-8',*[p for inc in includes for p in ('/I',inc)]]
    objects={}
    def compile_all(tag):
        for name,source,extra in [('game',SOURCE,[]),('canonical-search',CANONICAL,['/Dformatter_search_character_005a2780=fixture_canonical_search_005a2780']),('fixture',fixture,[])]:
            obj=out/(name+'.obj');objects[name]=obj
            record=run(tag+'-'+name,[*common,*extra,'/sourceDependencies',out/'dependencies',f'/Fo{obj}',source])
            assert record['exit_code']==0,(out/(tag+'-'+name+'.log')).read_text(errors='replace')
    compile_all('dependency-probe')
    dependencies=provenance.dependency_paths(out)
    for path in dependencies:pin(path)
    compile_all('compile')
    assert provenance.dependency_paths(out)==dependencies
    for path in objects.values():pin(path)
    symbols=coff.coff_symbols(objects['game'])
    expected={'?file_device_name_00568e90@porsche@@YAIPBD@Z','?resource_device_prefix_full_00591760@porsche@@YAIPBD@Z','?disk_path_device_00591760@porsche@@YAEPBD@Z'}
    assert set(symbols['defined'])==expected,symbols
    assert set(symbols['undefined'])=={'?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z','?resource_drive_letter_005916a0@porsche@@YAEPBD@Z'},symbols
    exe=out/'native_fixture.exe'
    def link_fixture(name,game_obj,target):
        result=run(name,[link,'/nologo','/MACHINE:X86','/SUBSYSTEM:CONSOLE','/INCREMENTAL:NO','/OPT:REF','/NODEFAULTLIB',f'/OUT:{target}',game_obj,objects['canonical-search'],objects['fixture'],*libs])
        assert result['exit_code']==0,(out/(name+'.log')).read_text(errors='replace')
    link_fixture('link',objects['game'],exe);pin(exe)
    execution=run('native',[exe])
    assert execution['exit_code']==0,(out/'native.log').read_text()
    assert 'cases=10240 failures=0' in (out/'native.log').read_text()
    negatives=[]
    if args.negative_controls:
        text=SOURCE.read_text()
        mutations=[('route-ignores-separator','if (formatter_search_character_005a2780(path, 0x7c) != nullptr)','if (false)'),('prefix-truncates-EAX','return letter == 0 ? 0u : letter - 0x40u;','return static_cast<std::uint8_t>(letter == 0 ? 0u : letter - 0x40u);'),('prefix-off-by-one','letter - 0x40u','letter - 0x41u')]
        for name,old,new in mutations:
            assert text.count(old)==1
            mutated=out/(name+'.cpp');mutated.write_text(text.replace(old,new),newline='\n');pin(mutated)
            obj=out/(name+'.obj')
            compile_record=run(name+'-compile',[*common,f'/Fo{obj}',mutated]);assert compile_record['exit_code']==0
            target=out/(name+'.exe');link_fixture(name+'-link',obj,target)
            record=run(name+'-native',[target]);assert record['exit_code'] in (10,12)
            negatives.append(dict(name=name,exit_code=record['exit_code'],detected=True))
    guard()
    outputs={relative(p):sha(p) for p in out.rglob('*') if p.is_file()}
    report=dict(schema=1,run=327,attempt=args.attempt,status='PASS',native_cases_passed=10240,original_sha256=SHA,original_selected_bytes=62,original_vas=['00568e90','00591760'],source_sha256={relative(p):sha(p) for p in (SOURCE,HEADER,CANONICAL)},inputs_sha256={relative(p):h for p,h in pins.items()},outputs_sha256=outputs,receipts=receipts,coff_symbols=symbols,native=execution,negative_controls=negatives,actual_dependencies=sorted(map(relative,dependencies)),guards_before_after=True,limits=['005916a0 remains a controlled AL-returning boundary; its real OS behavior is not accepted.','Canonical search source is compiled unchanged with a fixture-only symbol rename and recording wrapper.','Unused locale-comparison link dependencies are fixture-only globals/fail-fast functions, not exercised or accepted providers.','Callback00561ce0 is evidence only; no implementation or transform-cell provider is supplied.'])
    receipt=out/'receipt.json';write(receipt,report)
    summary=dict(schema=1,run=327,status='PASS',original_sha256=SHA,original_vas=report['original_vas'],original_selected_bytes=62,native_cases_passed=10240,native_attemptdir=relative(out),native_receipt_sha256=sha(receipt),source_sha256=report['source_sha256'],inputs_sha256=report['inputs_sha256'],negative_controls=negatives,coff_symbols=symbols,callback_00561ce0='evidence-only HOLD; not included in recovered byte count')
    write(RUN/'summary.json',summary)
    print(f'Run327 PASS: 2 original bodies /62B,10240 cases,3 ABI views; negative controls={len(negatives)}; receipt={relative(receipt)}')

if __name__=='__main__':main()

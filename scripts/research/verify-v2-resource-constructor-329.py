"""Native PE constructor proof with a verified full-word allocator transport.

Canonical production callee names/types are unchanged. All four callees in
this bounded fixture are recording boundaries; no queue or filesystem provider
is installed in the game. Mutants are local source copies linked in the same
one-batch executable and are never production inputs.
"""
from __future__ import annotations

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
import traceback

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/329-resource-constructor'
OUT = ROOT / 'local/experiments/v2-resource-constructor-329'
VC = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
SDK = Path('C:/Program Files (x86)/Windows Kits/10')
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def write(path, text):
    Path(path).write_text(text, encoding='utf8', newline='\n')


def json_write(path, value):
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


FIXTURE = r'''#include "resource_constructor_329.hpp"
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
using U=std::uint32_t;
using porsche::FileOperation;
using Fn=U (__cdecl*)(const char*,U,void*);
struct Event {U tag,a,b,c,d;};
struct State {
 U count;Event events[4];U device,result,allocation_kind,mutation,effective_group;
 unsigned char path[128],context[64];
 __declspec(align(16)) unsigned char operations[2][96];
};
static State state;
static unsigned char* code=nullptr;
static int cases=0,checks=0,failures=0;
static void check(bool yes){++checks;if(!yes)++failures;}
static void event(U tag,U a,U b=0,U c=0,U d=0){
 if(state.count<4)state.events[state.count++]={tag,a,b,c,d};else ++failures;
}
static FileOperation* selected(){
 return state.allocation_kind?reinterpret_cast<FileOperation*>(state.operations[state.allocation_kind-1]+16):nullptr;
}
// This wide hook sees the actual original/candidate argument slot. The naked
// fixture shim retains the canonical allocator's byte-group symbol/declaration.
static FileOperation* __cdecl allocate_word_hook(U type_word,U group_word,void* context_arg,U device_arg){
 event(0x5682a0,type_word,group_word,U(context_arg),device_arg);
 state.effective_group=group_word&0xffu;
 if(state.mutation&1)state.context[24]^=0x19;
 if(state.mutation&2)state.path[48]^=0x27;
 return selected();
}
namespace porsche {
U __cdecl file_device_name_00568e90(const char* path){
 event(0x568e90,U(path));
 if(state.mutation&1)state.path[47]^=0x35;
 return state.device;
}
__declspec(naked) FileOperation* __cdecl operation_allocate_005682a0(U,std::uint8_t,void*,U){
 __asm {jmp allocate_word_hook}
}
void __cdecl operation_name_005684e0(FileOperation* operation,const char* path){
 event(0x5684e0,U(operation),U(path));
 if(state.mutation&1){state.allocation_kind=state.allocation_kind==1?2:1;state.context[25]^=0x43;}
 if((state.mutation&2)&&operation)operation->id^=0xcafe1234u;
}
U __cdecl operation_queue_00568200(FileOperation* operation){
 event(0x568200,U(operation));
 U result=state.result;
 if((state.mutation&1)&&operation)operation->offset+=0x80000001u;
 if(state.mutation&2){state.result^=0x87654321u;state.context[26]^=0x57;}
 return result;
}
U __cdecl request_exists_00568260_mutant_group(const char*,U,void*);
U __cdecl request_exists_00568260_mutant_result(const char*,U,void*);
U __cdecl request_exists_00568260_mutant_null(const char*,U,void*);
}
static const unsigned char original[]={ORIGINAL_BYTES};
static void call(U offset,U target,U replacement){
 check(code[offset]==0xe8);U old=0;std::memcpy(&old,code+offset+1,4);
 check(0x568260u+offset+5+old==target);
 U disp=replacement-U(code+offset+5);std::memcpy(code+offset+1,&disp,4);
}
static bool init(){
 code=(unsigned char*)VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 check(code!=nullptr);if(!code)return false;std::memcpy(code,original,sizeof(original));
 call(7,0x568e90,U(&porsche::file_device_name_00568e90));
 call(0x19,0x5682a0,U(&porsche::operation_allocate_005682a0));
 call(0x22,0x5684e0,U(&porsche::operation_name_005684e0));
 call(0x28,0x568200,U(&porsche::operation_queue_00568200));
 DWORD previous=0;check(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&previous)!=0);
 check(FlushInstructionCache(GetCurrentProcess(),code,sizeof(original))!=0);
 return failures==0;
}
struct Registers {U eax,esp_before,esp_after,ebx_before,ebx_after,esi_before,esi_after,edi_before,edi_after,ebp_before,ebp_after;};
static Registers invoke(Fn target,const char* path,U group,void* context){
 U result=0,esp_before=0,esp_after=0,ebx_before=0,ebx_after=0,esi_before=0,esi_after=0;
 U edi_before=0,edi_after=0,ebp_before=0,ebp_after=0;
 __asm {
  mov esp_before,esp
  mov ebx_before,ebx
  mov esi_before,esi
  mov edi_before,edi
  mov ebp_before,ebp
  push context
  push group
  push path
  mov eax,target
  call eax
  add esp,12
  mov result,eax
  mov esp_after,esp
  mov ebx_after,ebx
  mov esi_after,esi
  mov edi_after,edi
  mov ebp_after,ebp
 }
 return {result,esp_before,esp_after,ebx_before,ebx_after,esi_before,esi_after,edi_before,edi_after,ebp_before,ebp_after};
}
struct Result {U value;bool abi,trace,guards;State post;};
static Result once(Fn target,U group,U device,U result,U allocation,U path_kind,U context_kind,U mutation){
 std::memset(&state,0,sizeof(state));
 state.device=device;state.result=result;state.allocation_kind=allocation;state.mutation=mutation;
 std::memset(state.path,0xa5,sizeof(state.path));std::memset(state.path+32,0,64);
 std::memset(state.context,0xa5,sizeof(state.context));std::memset(state.context+16,0,32);
 std::memset(state.operations,0xa5,sizeof(state.operations));
 for(U i=0;i<2;++i)std::memset(state.operations[i]+16,0,sizeof(FileOperation));
 const char* path=nullptr;
 if(path_kind){
  const char* text=path_kind==1?"":"Data\\Cars\\\x80\xff.sim";
  std::memcpy(state.path+32,text,std::strlen(text)+1);path=reinterpret_cast<const char*>(state.path+32);
 }
 void* context=context_kind==0?nullptr:context_kind==1?state.context+16:
  context_kind==2?state.path+32:reinterpret_cast<void*>(0xffffffffu);
 FileOperation* expected_operation=selected();
 Registers r=invoke(target,path,group,context);
 Event expected[4]={{0x568e90,U(path),0,0,0},{0x5682a0,6,group,U(context),device},
                    {0x5684e0,U(expected_operation),U(path),0,0},{0x568200,U(expected_operation),0,0,0}};
 bool trace=state.count==4&&std::memcmp(state.events,expected,sizeof(expected))==0&&state.effective_group==(group&0xffu);
 bool abi=r.esp_before==r.esp_after&&r.ebx_before==r.ebx_after&&r.esi_before==r.esi_after&&r.edi_before==r.edi_after&&r.ebp_before==r.ebp_after;
 bool guards=true;
 for(U i=0;i<128;++i)if((i<32||i>=96)&&state.path[i]!=0xa5)guards=false;
 for(U i=0;i<64;++i)if((i<16||i>=48)&&state.context[i]!=0xa5)guards=false;
 for(U row=0;row<2;++row)for(U i=0;i<96;++i)if((i<16||i>=16+sizeof(FileOperation))&&state.operations[row][i]!=0xa5)guards=false;
 Result out{};out.value=r.eax;out.abi=abi;out.trace=trace;out.guards=guards;out.post=state;return out;
}
static bool equal(const Result& a,const Result& b){
 return a.value==b.value&&a.abi&&b.abi&&a.trace&&b.trace&&a.guards&&b.guards&&std::memcmp(&a.post,&b.post,sizeof(State))==0;
}
int main(){
 if(!init())return 2;
 Fn oracle=reinterpret_cast<Fn>(code);
 const U groups[]={0,0x64,0x123400ffu,0xffffffffu};
 const U devices[]={0,1,0x80000000u,0xffffffffu};
 const U results[]={0,1,0xffffffffu,0x80000000u,0x7fffffffu,0x12345678u};
 for(U group:groups)for(U device:devices)for(U result:results)for(U allocation=0;allocation<3;++allocation)
 for(U path=0;path<3;++path)for(U context=0;context<4;++context)for(U mutation=0;mutation<4;++mutation){
  Result a=once(oracle,group,device,result,allocation,path,context,mutation);
  Result b=once(&porsche::request_exists_00568260,group,device,result,allocation,path,context,mutation);
  check(a.value==result);check(b.value==result);check(a.abi);check(b.abi);
  check(a.trace);check(b.trace);check(a.guards);check(b.guards);check(equal(a,b));++cases;
 }
 Fn mutants[]={&porsche::request_exists_00568260_mutant_group,&porsche::request_exists_00568260_mutant_result,&porsche::request_exists_00568260_mutant_null};
 int detected=0;
 for(U i=0;i<3;++i){
  U allocation=i==2?0:1;
  Result a=once(oracle,0xaabbccddu,0x87654321u,0xfedc1234u,allocation,2,1,3);
  Result b=once(mutants[i],0xaabbccddu,0x87654321u,0xfedc1234u,allocation,2,1,3);
  bool found=!equal(a,b);detected+=found;check(found);
 }
 check(VirtualFree(code,0,MEM_RELEASE)!=0);
 std::printf("cases=%d checks=%d failures=%d negative_controls=%d/3\n",cases,checks,failures,detected);
 return failures?1:0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', type=int, required=True)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    work = OUT / f'attempt-{args.attempt:03d}'
    work.mkdir(exist_ok=False)
    receipt = {'schema': 1, 'run': '329-resource-constructor', 'attempt': args.attempt, 'status': 'started', 'commands': []}
    pins = {}
    def pin(path):
        path = Path(path).resolve()
        pins[path] = sha(path)
        return path
    def guard():
        drift = [rel(p) for p, h in pins.items() if sha(p) != h]
        if drift:
            raise RuntimeError(f'input drift: {drift}')
    def run(cmd, name, timeout=90):
        guard()
        cmd = list(map(str, cmd))
        p = subprocess.run(cmd, cwd=work, capture_output=True, timeout=timeout,
                           env={**os.environ, 'VSLANG': '1033', 'CL': '', '_CL_': '', 'INCLUDE': '', 'LIB': ''})
        log = work / (name + '.log')
        log.write_bytes((p.stdout + p.stderr).replace(b'\r\n', b'\n'))
        receipt['commands'].append({'argv': cmd, 'exit_code': p.returncode, 'log': log.name, 'log_sha256': sha(log)})
        guard()
        if p.returncode:
            raise RuntimeError(f'{name} exited {p.returncode}: {log}')
        return p.stdout.decode('utf8', errors='replace')
    try:
        helper_path = pin(ROOT / 'scripts/research/verify-v2-resource-exists-326.py')
        helper = module('exists326helpers', helper_path)
        registry = pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json')
        index = pin(ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl')
        rows = {j['entry_va']: j for j in map(json.loads, index.read_text().splitlines())}
        owners = json.loads(registry.read_text())['functions']
        overlapping = []
        for owner in owners:
            if owner.get('module') != 'Porsche.exe':
                continue
            for a, b in rows.get(owner.get('entry_va'), {}).get('ranges', []):
                if int(a, 16) < 0x568293 and 0x568260 <= int(b, 16):
                    overlapping.append(owner)
        assert not overlapping, overlapping
        assert rows['00568260']['ranges'] == [['00568260', '00568292']]
        receipt['owner_check'] = {'candidate_va': '00568260', 'registered_body_or_interior_overlaps': [],
                                  'reused_canonical_vas': ['00568e90', '005682a0', '005684e0', '00568200'],
                                  'transport_adapter': 'internal allocate_with_group_word; no additional original VA'}
        original = pin(ROOT / 'local/game/Porsche.exe')
        assert sha(original) == PE_SHA
        image = original.read_bytes()
        body = helper.pe_body(image, 0x568260, 51)
        assert body[-1] == 0xc3
        body_path = work / 'original-00568260.bin'
        body_path.write_bytes(body)
        pin(body_path)
        consumer = helper.pe_body(image, 0x568309, 4)
        assert consumer == b'\x8a\x4c\x24\x18', consumer.hex()
        consumer_path = work / 'allocator-byte-consumer-00568309.bin'
        consumer_path.write_bytes(consumer)
        pin(consumer_path)
        receipt['original_sha256'] = PE_SHA
        receipt['original_body'] = {'va': '00568260', 'bytes': 51, 'sha256': sha(body_path)}
        receipt['allocator_group_consumer'] = {'va': '00568309', 'bytes_hex': consumer.hex(),
                                               'instruction': 'mov cl, byte ptr [esp+0x18]',
                                               'contract': 'original constructor transports a DWORD; canonical allocator consumes low byte'}
        rea = ROOT / 'local/experiments/v2-rea-resource-325/001'
        rea_receipt = json.loads(pin(rea / 'receipt.json').read_text())
        assert rea_receipt['exit_code'] == 0 and rea_receipt['target_sha256'] == PE_SHA
        analysis_path = pin(rea / 'request-constructor.json')
        assert sha(analysis_path) == rea_receipt['output_sha256']['request-constructor.json']
        envelope = json.loads(analysis_path.read_text())['structuredContent']
        procedure = envelope['raw_result']['value']['procedure']
        assert procedure['body']['total_bytes'] == 51 and procedure['address'] == '0x568260'
        receipt['rea325'] = {'receipt': rel(rea / 'receipt.json'), 'receipt_sha256': sha(rea / 'receipt.json'),
                             'constructor_evidence_id': envelope['evidence_id'], 'analysis_sha256': sha(analysis_path),
                             'signature_caution': 'inferred void ignored; actual queue EAX is returned'}
        source = RUN / 'resource_constructor_329.cpp'
        original_source = source.read_text(encoding='utf8')
        mutations = [
            ('group', 'push group_word', 'movzx eax, byte ptr group_word\n        push eax'),
            ('result', 'return operation_queue_00568200(operation);', 'return operation_queue_00568200(operation) != 0;'),
            ('null', 'operation_name_005684e0(operation, path);', 'if (!operation) return 0;\n    operation_name_005684e0(operation, path);'),
        ]
        mutants = []
        for name, old, new in mutations:
            assert original_source.count(old) == 1, name
            text = original_source.replace(old, new).replace('request_exists_00568260(', 'request_exists_00568260_mutant_' + name + '(')
            path = work / f'mutant_{name}.cpp'
            write(path, text)
            mutants.append(path)
        receipt['negative_controls'] = [{'name': name, 'source': rel(path), 'source_sha256': sha(path)}
                                       for (name, _, _), path in zip(mutations, mutants)]
        fixture = work / 'fixture.cpp'
        write(fixture, FIXTURE.replace('ORIGINAL_BYTES', ','.join(f'0x{x:02x}' for x in body)))
        cl, link, dumpbin = [VC / 'bin/Hostx64/x86' / name for name in ('cl.exe', 'link.exe', 'dumpbin.exe')]
        tools = [cl, link, dumpbin, *[cl.parent / name for name in ('c1xx.dll', 'c2.dll', 'mspdbcore.dll', 'mspdb140.dll') if (cl.parent / name).exists()]]
        libs = [VC / 'lib/x86/libcmt.lib', VC / 'lib/x86/libvcruntime.lib',
                SDK / 'Lib/10.0.26100.0/ucrt/x86/libucrt.lib', SDK / 'Lib/10.0.26100.0/um/x86/kernel32.lib']
        for path in (*tools, *libs):
            pin(path)
        includes = [RUN, ROOT / 'iterations/v2/001-original-recovery/source/include', VC / 'include']
        includes += [SDK / 'Include/10.0.26100.0' / part for part in ('ucrt', 'shared', 'um')]
        quoted = set()
        for path in (source, fixture, *mutants):
            helper.quoted_inputs(path, includes, quoted)
        for path in quoted:
            pin(path)
        pin(Path(__file__))
        dependencies = work / 'dependencies'
        dependencies.mkdir()
        cmd = [cl, '/nologo', '/c', '/std:c++17', '/Od', '/Oy-', '/MT', '/GS-', '/EHsc', '/W4', '/utf-8', '/sourceDependencies', dependencies]
        cmd += ['/I' + str(path) for path in includes]
        cmd += ['/Fo' + str(work) + '\\', source, fixture, *mutants]
        run(cmd, 'compile')
        discovered = set()
        for path in dependencies.glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8-sig'))['Data']
            discovered.update(Path(p).resolve() for p in [data['Source'], *data['Includes']])
            pin(path)
        assert all(p.resolve() in discovered for p in (source, fixture, *mutants))
        for path in discovered:
            pin(path)
        objects = [work / (path.stem + '.obj') for path in (source, fixture, *mutants)]
        for path in objects:
            pin(path)
        run([dumpbin, '/symbols', objects[0]], 'symbols')
        coff_path = pin(ROOT / 'scripts/research/build-v2-compile-corpus.py')
        symbols = module('coff329', coff_path).coff_symbols(objects[0])
        expected_defined = ['?request_exists_00568260@porsche@@YAIPBDIPAX@Z']
        expected_undefined = ['?file_device_name_00568e90@porsche@@YAIPBD@Z',
                              '?operation_allocate_005682a0@porsche@@YAPAUFileOperation@1@IEPAXI@Z',
                              '?operation_name_005684e0@porsche@@YAXPAUFileOperation@1@PBD@Z',
                              '?operation_queue_00568200@porsche@@YAIPAUFileOperation@1@@Z']
        assert sorted(symbols['defined']) == sorted(expected_defined), symbols
        assert sorted(symbols['undefined']) == sorted(expected_undefined), symbols
        receipt['game_object_symbols'] = symbols
        exe = work / 'fixture.exe'
        run([link, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/NODEFAULTLIB', '/OUT:' + str(exe), *objects, *libs], 'link')
        pin(exe)
        output = run([exe], 'native', timeout=30)
        match = re.fullmatch(r'cases=(\d+) checks=(\d+) failures=(\d+) negative_controls=(\d+)/3\s*', output)
        assert match and int(match[1]) == 13824 and int(match[3]) == 0 and int(match[4]) == 3, output
        receipt.update(native_cases_passed=int(match[1]), native_checks=int(match[2]), negative_controls_detected=3)
        for entry in receipt['negative_controls']:
            entry['detected'] = True
        receipt['objects_sha256'] = {p.name: sha(p) for p in objects}
        receipt['exe_sha256'] = sha(exe)
        receipt['tools_sha256'] = {rel(p): sha(p) for p in tools}
        receipt['link_libraries_sha256'] = {rel(p): sha(p) for p in libs}
        receipt['compiler_dependencies_sha256'] = {rel(p): sha(p) for p in sorted(discovered)}
        guard()
        receipt['status'] = 'pass'
    except Exception as exc:
        receipt.update(status='fail', error=f'{type(exc).__name__}: {exc}')
        write(work / 'error.log', traceback.format_exc())
        print(receipt['error'], file=sys.stderr)
    finally:
        receipt['inputs_sha256'] = {rel(p): h for p, h in sorted(pins.items())}
        receipt_path = work / 'receipt.json'
        json_write(receipt_path, receipt)
        print(rel(receipt_path))
    if receipt['status'] != 'pass':
        raise SystemExit(1)
    files = [RUN / name for name in ('resource_constructor_329.cpp', 'resource_constructor_329.hpp')]
    summary = {'schema': 1, 'status': 'native_original_constructor_verified_not_integrated',
               'original_module': 'Porsche.exe', 'original_sha256': PE_SHA,
               'original_ranges': ['00568260..00568292'], 'indexed_body_bytes': 51,
               'original_body': receipt['original_body'], 'original_function_count': 1,
               'accepted_source_list': [p.name for p in files], 'source_sha256': {p.name: sha(p) for p in files},
               'native_attempt': rel(work), 'native_attemptdir': rel(work), 'native_receipt_sha256': sha(receipt_path),
               'native_status': 'pass', 'native_cases_passed': receipt['native_cases_passed'], 'native_checks': receipt['native_checks'],
               'negative_controls': receipt['negative_controls'], 'game_object_sha256': sha(objects[0]),
               'native_executable_sha256': receipt['exe_sha256'], 'game_object_defined': symbols['defined'],
               'game_object_undefined': symbols['undefined'], 'group_transport': receipt['allocator_group_consumer'],
               'rea325': receipt['rea325'], 'open_boundaries': ['controlled canonical callees in fixture',
               'real route/allocator/name/queue state and physical file behavior remain separately bounded',
               'x86 transport adapter requires a separate ABI implementation on other targets', 'game integration332 pending']}
    json_write(RUN / 'summary.json', summary)


if __name__ == '__main__':
    main()

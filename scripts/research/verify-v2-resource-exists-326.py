"""Bounded native PE comparison for the resource-exists wrapper/request sequence.

Only fixture boundary providers own constructor/wait/completion behavior here.
Production calls retain canonical wait/completion symbols and the canonical
resource group storage. Each invocation compares raw EAX, ordered arguments,
mutable inputs and cdecl/nonvolatile ABI against relocated original PE bodies.
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
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/326-resource-exists'
OUT = ROOT / 'local/experiments/v2-resource-exists-326'
VC = ROOT / 'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207'
SDK = Path('C:/Program Files (x86)/Windows Kits/10')
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
TARGETS = ((0x561b80, 20), (0x533f00, 52))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def write(path, value):
    Path(path).write_text(value, encoding='utf8', newline='\n')


def json_write(path, value):
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def pe_body(image, va, size):
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    base = struct.unpack_from('<I', image, pe + 24 + 28)[0]
    section = pe + 24 + struct.unpack_from('<H', image, pe + 20)[0]
    for i in range(struct.unpack_from('<H', image, pe + 6)[0]):
        q = section + 40 * i
        vs, rva, raw_size, raw = struct.unpack_from('<IIII', image, q + 8)
        x = va - base
        if rva <= x and x + size <= rva + min(vs, raw_size):
            return image[raw + x - rva:raw + x - rva + size]
    raise ValueError(hex(va))


def quoted_inputs(path, include_dirs, found):
    path = path.resolve()
    if path in found:
        return
    found.add(path)
    for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"', path.read_text(encoding='utf8'), re.M):
        child = next((p / name for p in (path.parent, *include_dirs) if (p / name).is_file()), None)
        if child is None:
            raise FileNotFoundError(f'{path}: quoted include {name}')
        quoted_inputs(child, include_dirs, found)


FIXTURE = r'''#include "resource_exists_326.hpp"
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
using U=std::uint32_t;
struct Event { U tag,a,b,c; };
struct State {
 U calls; Event events[8]; U id,result,wait_result,mutation;
 unsigned char arena[128];
};
static State state;
static int checks=0,failures=0,cases=0;
static void check(bool yes){++checks;if(!yes)++failures;}
static void event(U tag,U a,U b=0,U c=0){
 if(state.calls<8)state.events[state.calls++]={tag,a,b,c};else ++failures;
}
namespace porsche {
// Test-only boundaries. No implementation of these original bodies is counted.
U __cdecl request_exists_00568260(const char* path,U group,void* context){
 event(0x568260,U(path),group,U(context));
 U id=state.id;
 if(state.mutation&1)resource_leaf_group_005df770^=0x87654321u;
 if((state.mutation&2)&&path)state.arena[48]^=0x39;
 return id;
}
std::int32_t __cdecl file_wait_00567f70(U id){
 event(0x567f70,id);
 if(state.mutation&1){resource_leaf_group_005df770+=0x12345678u;state.id^=0xcafe1000u;}
 if(state.mutation&2)state.arena[49]^=0x72;
 return static_cast<std::int32_t>(state.wait_result);
}
U __cdecl operation_complete_00567df0(U id){
 event(0x567df0,id);
 if(state.mutation&1)resource_leaf_group_005df770^=id;
 return state.result;
}
}
static const unsigned char original_wrapper[]={WRAPPER_BYTES};
static const unsigned char original_request[]={REQUEST_BYTES};
static unsigned char* code=nullptr;
static void word(U offset,U expected,U value){
 U old=0;std::memcpy(&old,code+offset,4);check(old==expected);
 std::memcpy(code+offset,&value,4);
}
static void call(U offset,U original_base,U original_target,U replacement){
 check(code[offset]==0xe8);
 U before=0;std::memcpy(&before,code+offset+1,4);
 check(original_base+offset+5+before==original_target);
 U after=replacement-U(code+offset+5);
 std::memcpy(code+offset+1,&after,4);
}
static bool init(){
 code=(unsigned char*)VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 check(code!=nullptr);if(!code)return false;
 std::memcpy(code,original_wrapper,sizeof(original_wrapper));
 std::memcpy(code+0x40,original_request,sizeof(original_request));
 word(1,0x5df770,U(&porsche::resource_leaf_group_005df770));
 call(0xb,0x561b80,0x533f00,U(code+0x40));
 // Offsets below include the request body's +0x40 placement in the slab.
 call(0x4f,0x533ec0,0x568260,U(&porsche::request_exists_00568260));
 call(0x5e,0x533ec0,0x567f70,U(&porsche::file_wait_00567f70));
 call(0x64,0x533ec0,0x567df0,U(&porsche::operation_complete_00567df0));
 DWORD previous=0;
 check(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&previous)!=0);
 check(FlushInstructionCache(GetCurrentProcess(),code,0x40+sizeof(original_request))!=0);
 return failures==0;
}
struct Registers { U eax,esp_before,esp_after,ebx_before,ebx_after,
 esi_before,esi_after,edi_before,edi_after,ebp_before,ebp_after; };
static Registers invoke(U target,const char* path,U group,U request){
 U value=0,esp_before=0,esp_after=0,ebx_before=0,ebx_after=0;
 U esi_before=0,esi_after=0,edi_before=0,edi_after=0,ebp_before=0,ebp_after=0;
 __asm {
  mov esp_before,esp
  mov ebx_before,ebx
  mov esi_before,esi
  mov edi_before,edi
  mov ebp_before,ebp
  cmp request,0
  je wrapper_call
  push group
 wrapper_call:
  push path
  mov eax,target
  call eax
  add esp,4
  cmp request,0
  je call_done
  add esp,4
 call_done:
  mov value,eax
  mov esp_after,esp
  mov ebx_after,ebx
  mov esi_after,esi
  mov edi_after,edi
  mov ebp_after,ebp
 }
 return {value,esp_before,esp_after,ebx_before,ebx_after,esi_before,esi_after,
         edi_before,edi_after,ebp_before,ebp_after};
}
static bool intact(const Registers& r){
 return r.esp_before==r.esp_after&&r.ebx_before==r.ebx_after&&
 r.esi_before==r.esi_after&&r.edi_before==r.edi_after&&r.ebp_before==r.ebp_after;
}
struct Result { U value[2],group; State post; };
static Result once(bool retail,U request,U group,U id,U result,U wait,U path_kind,U mutation){
 std::memset(&state,0,sizeof(state));
 state.id=id;state.result=result;state.wait_result=wait;state.mutation=mutation;
 std::memset(state.arena,0xa5,sizeof(state.arena));
 std::memset(state.arena+32,0,64);
 const char* path=nullptr;
 if(path_kind){
  const char* text=path_kind==1?"":path_kind==2?"Data\\Cars\\911.sim":"\x80\xff\\x";
  std::memcpy(state.arena+32,text,std::strlen(text)+1);
  path=reinterpret_cast<const char*>(state.arena+32);
 }
 porsche::resource_leaf_group_005df770=group;
 U target=retail?U(code+(request?0x40:0)):
  request?U(&porsche::resource_exists_request_00533f00):U(&porsche::file_exists_00561b80);
 Result out{};
 for(U i=0;i<2;++i){
  U before_calls=state.calls,expected_id=state.id;
  U forwarded_group=request?group:porsche::resource_leaf_group_005df770;
  Registers r=invoke(target,path,group,request);
  check(intact(r));check(r.eax==(expected_id?result:0));out.value[i]=r.eax;
  check(state.calls-before_calls==(expected_id?3u:1u));
  Event expected[3]={{0x568260,U(path),forwarded_group,0},{0x567f70,expected_id,0,0},{0x567df0,expected_id,0,0}};
  check(std::memcmp(state.events+before_calls,expected,(expected_id?3:1)*sizeof(Event))==0);
 }
 bool guards=true;
 for(U i=0;i<128;++i)if((i<32||i>=96)&&state.arena[i]!=0xa5)guards=false;
 check(guards);out.group=porsche::resource_leaf_group_005df770;out.post=state;
 return out;
}
int main(){
 if(!init())return 2;
 const U groups[]={0,0x64,0x80000000u,0xffffffffu};
 const U ids[]={0,1,0x80000000u,0xffffffffu};
 const U results[]={0,1,0xffffffffu,0x80000000u,0x7fffffffu,0x12345678u};
 const U waits[]={0,0xfffffffdu,0x80070005u};
 for(U request=0;request<2;++request)for(U group:groups)for(U id:ids)
 for(U result:results)for(U wait:waits)for(U path=0;path<4;++path)for(U mutation=0;mutation<4;++mutation){
  Result a=once(true,request,group,id,result,wait,path,mutation);
  Result b=once(false,request,group,id,result,wait,path,mutation);
  check(std::memcmp(&a,&b,sizeof(a))==0);++cases;
 }
 check(VirtualFree(code,0,MEM_RELEASE)!=0);
 std::printf("cases=%d checks=%d failures=%d\n",cases,checks,failures);
 return failures?1:0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    n = args.attempt or 1
    while args.attempt is None and (OUT / f'attempt-{n:03d}').exists():
        n += 1
    work = OUT / f'attempt-{n:03d}'
    work.mkdir(exist_ok=False)
    receipt = {'schema': 1, 'run': '326-resource-exists', 'attempt': n,
               'status': 'started', 'commands': []}
    pins = {}
    def pin(path):
        path = Path(path).resolve()
        pins[path] = sha(path)
        return path
    def guard():
        drift = [rel(p) for p, h in pins.items() if sha(p) != h]
        if drift:
            raise RuntimeError(f'input drift: {drift}')
    def run(cmd, stem, timeout=90):
        guard()
        cmd = list(map(str, cmd))
        p = subprocess.run(cmd, cwd=work, capture_output=True, timeout=timeout,
                           env={**os.environ, 'VSLANG': '1033', 'CL': '', '_CL_': '', 'INCLUDE': '', 'LIB': ''})
        log = work / (stem + '.log')
        log.write_bytes((p.stdout + p.stderr).replace(b'\r\n', b'\n'))
        receipt['commands'].append({'argv': cmd, 'exit_code': p.returncode,
                                    'log': log.name, 'log_sha256': sha(log)})
        guard()
        if p.returncode:
            raise RuntimeError(f'{stem} exited {p.returncode}: {log}')
        return p.stdout.decode('utf8', errors='replace')
    try:
        registry = pin(ROOT / 'iterations/v2/001-original-recovery/source/recovered/functions.json')
        index = pin(ROOT / 'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl')
        rows = {x['entry_va']: x for x in map(json.loads, index.read_text().splitlines())}
        owners = json.loads(registry.read_text())['functions']
        overlaps = []
        for owner in owners:
            if owner.get('module') != 'Porsche.exe':
                continue
            entry = owner.get('entry_va')
            for start, end in rows.get(entry, {}).get('ranges', []):
                a, b = int(start, 16), int(end, 16)
                if any(a < va + count and va <= b for va, count in TARGETS):
                    overlaps.append({'entry_va': entry, 'source': owner.get('source'), 'range': [start, end]})
        assert not overlaps, overlaps
        receipt['owner_check'] = {'candidate_vas': [f'{va:08x}' for va, _ in TARGETS],
                                  'indexed_body_and_interior_owner_overlaps': overlaps,
                                  'reused_owners': ['00567f70', '00567df0'],
                                  'constructor_boundary': '00568260',
                                  'canonical_group_source': 'source/recovered/Porsche.exe/resource_dispatch_globals.cpp'}
        pe = pin(ROOT / 'local/game/Porsche.exe')
        assert sha(pe) == PE_SHA, 'retail PE SHA mismatch'
        image = pe.read_bytes()
        spans = {}
        for va, size in TARGETS:
            row = rows[f'{va:08x}']
            assert row['ranges'] == [[f'{va:08x}', f'{va+size-1:08x}']]
            assert row['body_bytes'] == size
            body = pe_body(image, va, size)
            assert body[-1] == 0xc3
            output = work / f'original-{va:08x}.bin'
            output.write_bytes(body)
            pin(output)
            spans[va] = body
        receipt['original_module_sha256'] = PE_SHA
        receipt['original_bodies'] = [{'va': f'{va:08x}', 'bytes': size,
                                      'sha256': hashlib.sha256(spans[va]).hexdigest()}
                                     for va, size in TARGETS]
        assert pe_body(image, 0x5df770, 4) == b'\x64\0\0\0'
        template = FIXTURE.replace('WRAPPER_BYTES', ','.join(f'0x{x:02x}' for x in spans[0x561b80]))
        template = template.replace('REQUEST_BYTES', ','.join(f'0x{x:02x}' for x in spans[0x533f00]))
        fixture = work / 'fixture.cpp'
        write(fixture, template)
        cl, link, dumpbin = [VC / 'bin/Hostx64/x86' / name for name in ('cl.exe', 'link.exe', 'dumpbin.exe')]
        tools = [cl, link, dumpbin]
        tools += [cl.parent / p for p in ('c1xx.dll', 'c2.dll', 'mspdbcore.dll', 'mspdb140.dll') if (cl.parent / p).is_file()]
        for tool in tools:
            pin(tool)
        source = RUN / 'resource_exists_326.cpp'
        group = ROOT / 'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/resource_dispatch_globals.cpp'
        includes = [RUN, ROOT / 'iterations/v2/001-original-recovery/source/include', VC / 'include']
        includes += [SDK / 'Include/10.0.26100.0' / name for name in ('ucrt', 'shared', 'um')]
        quoted = set()
        for path in (source, fixture, group):
            quoted_inputs(path, includes, quoted)
        for path in quoted:
            pin(path)
        pin(Path(__file__))
        libs = [VC / 'lib/x86/libcmt.lib', VC / 'lib/x86/libvcruntime.lib',
                SDK / 'Lib/10.0.26100.0/ucrt/x86/libucrt.lib',
                SDK / 'Lib/10.0.26100.0/um/x86/kernel32.lib']
        for lib in libs:
            pin(lib)
        dependencies = work / 'dependencies'
        dependencies.mkdir()
        cmd = [cl, '/nologo', '/c', '/std:c++17', '/Od', '/Oy-', '/MT', '/GS-', '/EHsc', '/TP', '/W4', '/utf-8',
               '/sourceDependencies', dependencies]
        cmd += ['/I' + str(p) for p in includes]
        cmd += ['/Fo' + str(work) + '\\', source, group, fixture]
        run(cmd, 'compile')
        compiler_dependencies = set()
        for depfile in dependencies.glob('*.json'):
            data = json.loads(depfile.read_text(encoding='utf-8-sig'))['Data']
            for path in [data['Source'], *data['Includes']]:
                compiler_dependencies.add(Path(path).resolve())
            pin(depfile)
        assert compiler_dependencies and all(p.resolve() in compiler_dependencies for p in (source, group, fixture))
        for dep in compiler_dependencies:
            pin(dep)
        objects = [work / name for name in ('resource_exists_326.obj', 'resource_dispatch_globals.obj', 'fixture.obj')]
        for obj in objects:
            pin(obj)
        run([dumpbin, '/symbols', objects[0]], 'symbols')
        coff_path = pin(ROOT / 'scripts/research/build-v2-compile-corpus.py')
        coff = module('coff326', coff_path)
        symbols = coff.coff_symbols(objects[0])
        expected_defined = ['?file_exists_00561b80@porsche@@YAHPBD@Z', '?resource_exists_request_00533f00@porsche@@YAHPBDI@Z']
        expected_undefined = ['?file_wait_00567f70@porsche@@YAHI@Z', '?operation_complete_00567df0@porsche@@YAII@Z',
                              '?request_exists_00568260@porsche@@YAIPBDIPAX@Z', '?resource_leaf_group_005df770@porsche@@3IA']
        assert sorted(symbols['defined']) == sorted(expected_defined), symbols
        assert sorted(symbols['undefined']) == sorted(expected_undefined), symbols
        receipt['game_object_symbols'] = symbols
        exe = work / 'fixture.exe'
        run([link, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/NODEFAULTLIB',
             '/OUT:' + str(exe), *objects, *libs], 'link')
        pin(exe)
        output = run([exe], 'native', timeout=30)
        match = re.fullmatch(r'cases=(\d+) checks=(\d+) failures=(\d+)\s*', output)
        assert match and int(match[1]) == 9216 and int(match[3]) == 0, output
        receipt['native_cases_passed'] = int(match[1])
        receipt['native_checks'] = int(match[2])
        receipt['objects_sha256'] = {p.name: sha(p) for p in objects}
        receipt['exe_sha256'] = sha(exe)
        receipt['tools_sha256'] = {rel(p): sha(p) for p in tools}
        receipt['link_libraries_sha256'] = {rel(p): sha(p) for p in libs}
        receipt['compiler_dependencies_sha256'] = {rel(p): sha(p) for p in sorted(compiler_dependencies)}
        guard()
        receipt['status'] = 'pass'
    except Exception as exc:
        receipt['status'] = 'fail'
        receipt['error'] = f'{type(exc).__name__}: {exc}'
        write(work / 'error.log', traceback.format_exc())
        print(receipt['error'], file=sys.stderr)
    finally:
        receipt['inputs_sha256'] = {rel(p): h for p, h in sorted(pins.items())}
        receipt_path = work / 'receipt.json'
        json_write(receipt_path, receipt)
        print(rel(receipt_path))
    if receipt['status'] != 'pass':
        raise SystemExit(1)
    if args.finalize:
        source_files = [RUN / p for p in ('resource_exists_326.cpp', 'resource_exists_326.hpp')]
        summary = {'schema': 1, 'status': 'native_original_resource_exists_bounded_verified_not_integrated',
                   'original_module': 'Porsche.exe', 'original_sha256': PE_SHA,
                   'original_ranges': [f'{va:08x}..{va+size-1:08x}' for va, size in TARGETS],
                   'original_bodies': receipt['original_bodies'], 'indexed_body_bytes': sum(n for _, n in TARGETS),
                   'accepted_source_list': [p.name for p in source_files], 'original_function_count': 2,
                   'source_sha256': {p.name: sha(p) for p in source_files},
                   'native_attempt': rel(work), 'native_attempt_dir': rel(work),
                   'native_receipt_sha256': sha(receipt_path), 'native_status': 'pass',
                   'native_cases_passed': receipt['native_cases_passed'], 'native_checks': receipt['native_checks'],
                   'game_object_sha256': sha(objects[0]), 'native_executable_sha256': sha(exe),
                   'game_object_defined': symbols['defined'], 'game_object_undefined': symbols['undefined'],
                   'open_boundaries': ['constructor00568260/path-device/queue/OS behavior',
                                       'controlled wait/completion in this fixture; accepted bodies retain canonical owners',
                                       'REA325 cross-review and game-graph integration pending']}
        json_write(RUN / 'summary.json', summary)


if __name__ == '__main__':
    main()

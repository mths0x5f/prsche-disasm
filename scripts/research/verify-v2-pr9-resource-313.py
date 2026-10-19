"""Run313: exact PE cutpoint and fresh Win32 differential fixture for 0059d8e0."""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/313-pr9-resource-open"
OUT = ROOT / "local/experiments/v2-pr9-resource-313"
PE = ROOT / "local/game/Porsche.exe"
PE_SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
SOURCE = RUN / "resource_open_313.cpp"
HEADER = RUN / "resource_open_313.hpp"
SIZE = 206


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    with Path(path).open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write("\n")


def pe_at(data, va, count):
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    base = struct.unpack_from("<I", data, pe + 52)[0]
    section = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    for index in range(struct.unpack_from("<H", data, pe + 6)[0]):
        loc = section + index * 40
        virtual_size, virtual_address, raw_size, raw = struct.unpack_from("<IIII", data, loc + 8)
        rva = va - base
        if virtual_address <= rva and rva + count <= virtual_address + min(virtual_size, raw_size):
            return data[raw + rva - virtual_address:raw + rva - virtual_address + count]
    raise ValueError(f"VA {va:08x} outside PE raw sections")


def local_includes(path, found=None):
    if found is None:
        found = set()
    path = path.resolve()
    if path in found:
        return found
    found.add(path)
    for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.M):
        candidates = [path.parent / name, ROOT / "iterations/v2/001-original-recovery/source/include" / name,
                      RUN / name]
        match = next((candidate for candidate in candidates if candidate.is_file()), None)
        if match is None:
            raise ValueError(f"Unpinned quoted include {name} from {path}")
        local_includes(match, found)
    return found


def receipt(label, command, artifact=None):
    start = time.perf_counter()
    error = None
    try:
        process = subprocess.run([str(arg) for arg in command], cwd=OUT, capture_output=True, timeout=120)
        status, output = process.returncode, process.stdout + process.stderr
    except OSError as exc:
        status, error = None, str(exc)
        output = error.encode("utf-8", "replace")
    log = OUT / f"{label}.log"
    log.write_bytes(output)
    value = {"command": [str(arg) for arg in command], "exit_code": status,
             "seconds": round(time.perf_counter() - start, 6), "log": log.relative_to(ROOT).as_posix(),
             "log_sha256": sha(log)}
    if error:
        value["spawn_error"] = error
    if artifact and artifact.is_file():
        value["output"] = artifact.relative_to(ROOT).as_posix()
        try:
            value["output_sha256"] = sha(artifact)
        except OSError as exc:
            value["output_read_error"] = str(exc)
    write_json(OUT / f"{label}.json", value)
    return value


FIXTURE = r'''
#include <windows.h>
#include <cstdint>
#include <cstdarg>
#include <cstdio>
#include "resource_open_313.hpp"
using U = std::uint32_t;
static_assert(sizeof(void*) == 4, "x86 fixture required");
static const unsigned char original_bytes[206] = { @BYTES@ };
static const char original_format[] = "%s%s";
struct Event { U kind, argument; char path[48]; };
struct Result { U esp0, esp1, ebp0, ebp1, ebx0, ebx1, esi0, esi1, edi0, edi1, eax;
                U count; Event events[8]; };
static Event events[8];
static U event_count, exists_count, scenario;
static const char name[] = "car.fsh";
static void copy(char* out, const char* in) {
    while ((*out++ = *in++) != 0) {}
}
static bool equal_text(const char* a,const char* b) {
    while (*a && *a == *b) { ++a; ++b; }
    return *a == *b;
}
static void log(U kind,const char* path,U arg) {
    if(event_count >= 8) ExitProcess(90);
    Event& e=events[event_count++]; e.kind=kind; e.argument=arg;
    U i=0; for(;i<47 && path[i];++i)e.path[i]=path[i]; e.path[i]=0;
}
namespace porsche {
char file_root_006af168[260], file_fallback_006af26c[260], file_roots_enabled_006af370;
void (__cdecl* missing_file_006afbe4)(const char*,std::int32_t);
static void __cdecl callback_a(const char* path,std::int32_t code) { log(4,path,U(code)); }
static void __cdecl callback_b(const char* path,std::int32_t code) { log(5,path,U(code)); }
std::int32_t __cdecl formatter_entry_005a0fbf(char* out,const char* format,...) {
    if(!equal_text(format,original_format)) ExitProcess(91);
    va_list args; va_start(args,format);
    const char* root=va_arg(args,const char*), *tail=va_arg(args,const char*);
    va_end(args);
    char* dst=out; while(*root)*dst++=*root++; while(*tail)*dst++=*tail++; *dst=0;
    log(1,out,0); return std::int32_t(dst-out);
}
std::int32_t __cdecl file_exists_00561b80(const char* path) {
    ++exists_count; log(2,path,exists_count);
    if(exists_count==1) {
        if(scenario==5)file_fallback_006af26c[0]=0;
        if(scenario==6)file_fallback_006af26c[0]='C';
        if(scenario==7)missing_file_006afbe4=callback_b;
    }
    return (scenario==1 && exists_count==1) ||
           ((scenario==2 || scenario==6) && exists_count==2);
}
void* __cdecl file_open_00561ca0(const char* path,U flags) {
    log(3,path,flags); return reinterpret_cast<void*>(0x12345000u + flags);
}
}
static void reset(U number) {
    scenario=number;event_count=0;exists_count=0;
    for(Event& e:events){e.kind=0;e.argument=0;for(char& c:e.path)c=0;}
    copy(porsche::file_root_006af168,"A/");
    copy(porsche::file_fallback_006af26c,number==3 || number==5 || number==7 ? "" : "B/");
    porsche::file_roots_enabled_006af370=number==0 ? 0 : 1;
    porsche::missing_file_006afbe4=number==8 ? nullptr : porsche::callback_a;
}
static Result run(void* (__cdecl* fn)(const char*,U)) {
    Result r={}; U flags=0x6a31c5e7u;
    __asm {
        lea edx,r
        mov [edx],esp
        mov [edx+8],ebp
        mov [edx+16],ebx
        mov [edx+24],esi
        mov [edx+32],edi
        push flags
        push offset name
        mov ecx,fn
        call ecx
        add esp,8
        lea edx,r
        mov [edx+40],eax
        mov [edx+4],esp
        mov [edx+12],ebp
        mov [edx+20],ebx
        mov [edx+28],esi
        mov [edx+36],edi
    }
    r.count=event_count;
    for(U i=0;i<event_count;++i)r.events[i]=events[i];
    return r;
}
static bool same(const Result&a,const Result&b) {
    if(a.esp0!=a.esp1 || b.esp0!=b.esp1 || a.ebp0!=a.ebp1 || b.ebp0!=b.ebp1 ||
       a.ebx0!=a.ebx1 || b.ebx0!=b.ebx1 || a.esi0!=a.esi1 || b.esi0!=b.esi1 ||
       a.edi0!=a.edi1 || b.edi0!=b.edi1 || a.eax!=b.eax || a.count!=b.count)return false;
    for(U i=0;i<a.count;++i) if(a.events[i].kind!=b.events[i].kind ||
       a.events[i].argument!=b.events[i].argument || !equal_text(a.events[i].path,b.events[i].path))return false;
    return true;
}
static void patch32(unsigned char* where,U value) {
    for(U i=0;i<4;++i)where[i]=static_cast<unsigned char>(value>>(8*i));
}
static void patchrel(unsigned char* where,const void* target) {
    patch32(where,U(target)-U(where+4));
}
int main() {
    auto* slab=static_cast<unsigned char*>(VirtualAlloc(nullptr,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    if(!slab)return 90;
    for(U i=0;i<206;++i)slab[i]=original_bytes[i];
    patch32(slab+0x01,U(&porsche::file_roots_enabled_006af370));
    patch32(slab+0x64,U(&porsche::file_root_006af168));
    patch32(slab+0x69,U(original_format));
    patch32(slab+0x85,U(&porsche::file_fallback_006af26c));
    patch32(slab+0x8f,U(&porsche::file_fallback_006af26c));
    patch32(slab+0x98,U(original_format));
    patch32(slab+0xb4,U(&porsche::missing_file_006afbe4));
    patchrel(slab+0x48,reinterpret_cast<const void*>(&porsche::file_open_00561ca0));
    patchrel(slab+0x6f,reinterpret_cast<const void*>(&porsche::formatter_entry_005a0fbf));
    patchrel(slab+0x79,reinterpret_cast<const void*>(&porsche::file_exists_00561b80));
    patchrel(slab+0x9e,reinterpret_cast<const void*>(&porsche::formatter_entry_005a0fbf));
    patchrel(slab+0xa8,reinterpret_cast<const void*>(&porsche::file_exists_00561b80));
    DWORD previous=0;
    if(!VirtualProtect(slab,4096,PAGE_EXECUTE_READ,&previous) ||
       !FlushInstructionCache(GetCurrentProcess(),slab,4096))return 91;
    auto original=reinterpret_cast<void* (__cdecl*)(const char*,U)>(slab);
    U passed=0;
    for(U variant=0;variant<9;++variant) {
        reset(variant);Result a=run(original);
        const U expected_counts[9]={1,3,5,3,5,3,5,3,4};
        if(a.count!=expected_counts[variant]) { std::printf("case=%u wrong branch count=%u\n",variant,a.count); return 30+variant; }
        if((variant==0 || variant==1 || variant==2 || variant==6) != (a.eax!=0)) return 40+variant;
        if(a.eax && (a.events[a.count-1].kind!=3 || a.events[a.count-1].argument!=0x6a31c5e7u)) return 50+variant;
        if((variant==3 || variant==4 || variant==5 || variant==7) &&
           (a.events[a.count-1].kind!=(variant==7?5u:4u) ||
            a.events[a.count-1].argument!=0xfffffffeu ||
            !equal_text(a.events[a.count-1].path,name))) return 60+variant;
        if(variant==6 && !equal_text(a.events[2].path,"C/car.fsh")) return 70;
        reset(variant);Result b=run(&porsche::resource_open_0059d8e0);
        if(!same(a,b)) { std::printf("case=%u divergence original=%08x cpp=%08x events=%u/%u\n",
                                  variant,a.eax,b.eax,a.count,b.count); return 10+variant; }
        ++passed;
    }
    std::printf("cases=%u failures=0\n",passed);
    return passed==9?0:50;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    if args.attempt < 1:
        parser.error("attempt must be positive")
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = f"attempt-{args.attempt:03d}"
    report = OUT / f"{prefix}.json"
    if report.exists():
        raise SystemExit(f"Refusing to overwrite {report}")
    if sha(PE) != PE_SHA:
        raise SystemExit("Original PE SHA mismatch")
    data = PE.read_bytes()
    body = pe_at(data, 0x0059d8e0, SIZE)
    literal = pe_at(data, 0x005cc588, 5)
    if literal != b"%s%s\0" or body[:6].hex() != "a070f36a0081" or body[-1] != 0xc3:
        raise SystemExit("Original body/literal signature mismatch")
    calls = {0x47: 0x00561ca0, 0x6e: 0x005a0fbf, 0x78: 0x00561b80,
             0x9d: 0x005a0fbf, 0xa7: 0x00561b80}
    for offset, target in calls.items():
        if body[offset] != 0xe8 or 0x0059d8e0 + offset + 5 + struct.unpack_from("<i", body, offset+1)[0] != target:
            raise SystemExit(f"Original CALL mismatch at +{offset:x}")
    absolute = {1: (0xa0, 0x006af370), 0x64: (0x68, 0x006af168),
                0x69: (0x68, 0x005cc588), 0x85: (0xa0, 0x006af26c),
                0x8f: (0x68, 0x006af26c), 0x98: (0x68, 0x005cc588),
                0xb4: (0xa1, 0x006afbe4)}
    for offset, (opcode, address) in absolute.items():
        if body[offset-1] != opcode or struct.unpack_from("<I", body, offset)[0] != address:
            raise SystemExit(f"Original absolute operand mismatch at +{offset:x}")
    fixture = OUT / f"{prefix}-fixture.cpp"
    with fixture.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(FIXTURE.replace("@BYTES@", ",".join(str(x) for x in body)))
    pins = {path.relative_to(ROOT).as_posix(): sha(path)
            for path in sorted(local_includes(SOURCE) | local_includes(fixture) | {Path(__file__).resolve(), PE})}
    result = {"schema": 1, "run": 313, "attempt": args.attempt, "status": "static-pe-verified",
              "original_module": "Porsche.exe", "original_sha256": PE_SHA,
              "original_va": "0059d8e0", "original_bytes": SIZE, "format_va": "005cc588",
              "original_call_targets": {f"{offset:02x}": f"{target:08x}" for offset,target in calls.items()},
              "input_sha256": pins, "fixture": fixture.relative_to(ROOT).as_posix(),
              "native_cases_passed": 0}
    if args.static_only:
        write_json(report, result)
        print(result["status"])
        return
    vc = ROOT / "local/tools/BuildTools/VC/Tools/MSVC/14.44.35207"
    sdk = Path("C:/Program Files (x86)/Windows Kits/10")
    kit = "10.0.26100.0"
    cl, link = vc / "bin/Hostx64/x86/cl.exe", vc / "bin/Hostx64/x86/link.exe"
    includes = [ROOT / "iterations/v2/001-original-recovery/source/include", RUN, vc / "include",
                *[sdk / "Include" / kit / name for name in ("ucrt", "shared", "um")]]
    libs = [vc / "lib/x86/libcmt.lib", vc / "lib/x86/libvcruntime.lib",
            sdk / "Lib" / kit / "ucrt/x86/libucrt.lib", sdk / "Lib" / kit / "um/x86/kernel32.lib"]
    tools = [cl, link, *libs]
    if not all(path.is_file() for path in tools) or not all(path.is_dir() for path in includes):
        result["status"] = "toolchain-unavailable"
        write_json(report, result)
        raise SystemExit("Pinned Win32 toolchain unavailable")
    result["toolchain_sha256"] = {str(path): sha(path) for path in tools}
    result["receipts"] = {}
    objects = [OUT / f"{prefix}-game.obj", OUT / f"{prefix}-fixture.obj"]
    for label, source, obj in (("game", SOURCE, objects[0]), ("fixture", fixture, objects[1])):
        cmd = [cl, "/nologo", "/c", "/TP", "/std:c++17", "/Od", "/GS-", "/GR-", "/EHsc", "/W4", "/utf-8", "/showIncludes",
               *[part for root in includes for part in ("/I", root)], f"/Fo{obj}", source]
        value = receipt(f"{prefix}-compile-{label}", cmd, obj)
        result["receipts"][f"compile_{label}"] = value
        if value["exit_code"] != 0:
            result["status"] = "native-compile-failed"
            write_json(report, result)
            raise SystemExit("Native compile failed")
    dependency_paths = set()
    for label in ("game", "fixture"):
        log = (OUT / f"{prefix}-compile-{label}.log").read_text(encoding="utf-8", errors="replace")
        for line in log.splitlines():
            match = re.search(r"([A-Za-z]:\\.*)$", line)
            if match:
                candidate = Path(match.group(1).strip())
                if candidate.is_file():
                    dependency_paths.add(candidate.resolve())
    if not dependency_paths:
        result["status"] = "compiler-dependency-pins-missing"
        write_json(report, result)
        raise SystemExit("No /showIncludes dependencies recognized")
    result["transitive_include_sha256"] = {str(path): sha(path) for path in sorted(dependency_paths)}
    parser_path = ROOT / "scripts/research/build-v2-compile-corpus.py"
    spec = importlib.util.spec_from_file_location("coff313", parser_path)
    coff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coff)
    result["coff_parser_sha256"] = sha(parser_path)
    result["coff_symbols"] = {label: coff.coff_symbols(obj)
                              for label, obj in (("game", objects[0]), ("fixture", objects[1]))}
    expected_definitions = (
        "?resource_open_0059d8e0@porsche@@YAPAXPBDI@Z",
        "?game_setup_resource_file_open_0059d8e0@porsche@@YAPAXPBDI@Z",
        "?splash_progress_load_resource_0059d8e0@porsche@@YAPAXPBDI@Z")
    if (not all(name in result["coff_symbols"]["game"]["defined"] for name in expected_definitions)
            or result["coff_symbols"]["game"]["common"]
            or result["coff_symbols"]["game"]["weak"]):
        result["status"] = "game-coff-symbol-mismatch"
        write_json(report, result)
        raise SystemExit("Game COFF definition mismatch")
    exe = OUT / f"{prefix}-native.exe"
    value = receipt(f"{prefix}-link", [link, "/nologo", "/MACHINE:X86", "/SUBSYSTEM:CONSOLE",
                                       "/NODEFAULTLIB", "/INCREMENTAL:NO", f"/OUT:{exe}", *objects, *libs], exe)
    result["receipts"]["link"] = value
    if value["exit_code"] != 0 or "output_sha256" not in value:
        result["status"] = "native-link-failed-or-unreadable"
        write_json(report, result)
        raise SystemExit("Native link failed or output unreadable")
    value = receipt(f"{prefix}-execute", [exe])
    result["receipts"]["execute"] = value
    result["native_cases_passed"] = (
        9 if value["exit_code"] == 0 and
        (OUT / f"{prefix}-execute.log").read_bytes() == b"cases=9 failures=0\r\n" else 0)
    result["status"] = "native-pass" if result["native_cases_passed"] == 9 else "native-divergence"
    write_json(report, result)
    print(result["status"])
    if result["status"] != "native-pass":
        raise SystemExit("Native comparison failed")


if __name__ == "__main__":
    main()

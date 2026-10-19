"""Isolated Win32 dispatcher comparison for Run312; never changes game data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/312-pr7-fill-dispatch"
OUT = ROOT / "local/experiments/v2-pr7-fill-312"
HEAD = "a349d056a0dc981b770e34121c5d2b5476295393"
UPSTREAM = "iterations/v2/001-original-recovery/runs/405-app-main-timer-display/app_main_timer_display_405.cpp"
PE_SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
VC = ROOT / "local/tools/BuildTools/VC/Tools/MSVC/14.44.35207"
SDK = Path("C:/Program Files (x86)/Windows Kits/10")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def pe_body(data: bytes, va: int, size: int) -> bytes:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    section = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    for i in range(struct.unpack_from("<H", data, pe + 6)[0]):
        q = section + 40 * i
        vs, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data, q + 8)
        x = va - base
        if rva <= x and x + size <= rva + min(vs, raw_size):
            return data[raw_ptr + x - rva:raw_ptr + x - rva + size]
    raise ValueError(hex(va))


def quoted_inputs(path: Path, include_dirs: list[Path], found: set[Path]) -> None:
    if path in found:
        return
    found.add(path)
    for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.M):
        for base in [path.parent, *include_dirs]:
            child = base / name
            if child.is_file():
                quoted_inputs(child.resolve(), include_dirs, found)
                break
        else:
            raise FileNotFoundError(f"quoted include {name} from {path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 1
    while (OUT / f"attempt-{n:03d}").exists():
        n += 1
    work = OUT / f"attempt-{n:03d}"
    work.mkdir()
    receipt: dict = {"schema": 1, "attempt": n, "status": "started", "head": HEAD,
                     "upstream": UPSTREAM, "source": str(RUN.relative_to(ROOT)), "commands": []}
    receipt_path = work / "receipt.json"
    try:
        def run(cmd: list[str], stem: str, *, timeout: int = 90) -> subprocess.CompletedProcess[str]:
            p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout)
            log = work / (stem + ".log")
            write(log, p.stdout + p.stderr)
            receipt["commands"].append({"argv": cmd, "exit_code": p.returncode,
                                         "log": log.name, "log_sha256": sha(log)})
            if p.returncode:
                raise RuntimeError(f"{stem} exited {p.returncode}; {log}")
            return p

        upstream = subprocess.check_output(["git", "show", f"{HEAD}:{UPSTREAM}"], cwd=ROOT)
        (work / "upstream-405.cpp").write_bytes(upstream)
        pe_path = ROOT / "local/game/Porsche.exe"
        if sha(pe_path) != PE_SHA:
            raise RuntimeError("retail PE SHA mismatch")
        body = pe_body(pe_path.read_bytes(), 0x0053C290, 77)
        (work / "original-0053c290.bin").write_bytes(body)
        body_arr = ",".join(f"0x{x:02x}" for x in body)
        fixture = r'''#include "0053c290.hpp"
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mmintrin.h>
using U=std::uint32_t;
namespace porsche {
U copy_flag_005deb18=0;
struct Event { U backend,destination,value,bytes; };
Event event{}; U mmx_dirty_tag=0;
void __cdecl heap_fill_sse_005b0b00(void* d,U v,U n){event={0x005b0b00,U(d),v,n};}
void __cdecl heap_fill_mmx_005b0a40(void* d,U v,U n){
 event={0x005b0a40,U(d),v,n};
 __asm { mov eax,v
         movd mm0,eax }
 __declspec(align(16)) unsigned char fx[512]{};
 __asm { lea eax,fx
         fxsave [eax] }
 mmx_dirty_tag=fx[4];
}
void __cdecl heap_fill_scalar_005b0980(void* d,U v,U n){event={0x005b0980,U(d),v,n};}
}
static unsigned char original[77]={ORIGINAL_BYTES};
static unsigned char* code=nullptr;
static int failures=0,checks=0;
static void check(bool pass){++checks;if(!pass)++failures;}
static void patch_word(unsigned offset,U expected,U value){
 U old=0;std::memcpy(&old,code+offset,4);check(old==expected);
 std::memcpy(code+offset,&value,4);
}
static void patch_call(U at,U target){
 U offset=at-0x0053c290;check(code[offset]==0xe8);
 U displacement=target-U(code+offset+5);
 std::memcpy(code+offset+1,&displacement,4);
}
static void init_code(){
 code=(unsigned char*)VirtualAlloc(nullptr,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 check(code!=nullptr);if(!code)return;
 std::memcpy(code,original,sizeof(original));
 patch_word(0x04,0x005deb1c,U(&porsche::shared_runtime_word_005deb1c));
 patch_word(0x23,0x005deb18,U(&porsche::copy_flag_005deb18));
 patch_call(0x0053c2a8,U(&porsche::heap_fill_sse_005b0b00));
 patch_call(0x0053c2c7,U(&porsche::heap_fill_mmx_005b0a40));
 patch_call(0x0053c2d3,U(&porsche::heap_fill_scalar_005b0980));
 DWORD old=0;check(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old)!=0);
 check(FlushInstructionCache(GetCurrentProcess(),code,sizeof(original))!=0);
}
struct Result {porsche::Event event; U x87_tag,mmx_dirty_tag;};
static Result once(bool retail,U sse,U mmx,U d,U v,U n){
 porsche::copy_flag_005deb1c=sse;porsche::copy_flag_005deb18=mmx;
 porsche::event={};porsche::mmx_dirty_tag=0;_mm_empty();
 if(retail)reinterpret_cast<void(__cdecl*)(void*,U,U)>(code)(reinterpret_cast<void*>(d),v,n);
 else porsche::heap_fill_0053c290(reinterpret_cast<void*>(d),v,n);
 __declspec(align(16)) unsigned char fx[512]{};
 __asm { lea eax,fx
         fxsave [eax] }
 return {porsche::event,fx[4],porsche::mmx_dirty_tag};
}
int main(){
 init_code();if(!code)return 2;
 const U sizes[]={0,1,7,31,32,33,64};
 int cases=0;
 for(U mask=0;mask<4;++mask)for(U n:sizes){
  U sse=(mask&2)?0x1234:0,mmx=(mask&1)?0xff:0;
  U dest=0x13572468+n,value=0xa1b2c3d4u^n;
  Result a=once(true,sse,mmx,dest,value,n),b=once(false,sse,mmx,dest,value,n);
  U expected=sse?0x005b0b00:(mmx?0x005b0a40:0x005b0980);
  check(a.event.backend==expected);check(b.event.backend==expected);
  check(a.event.destination==dest&&b.event.destination==dest);
  check(a.event.value==value&&b.event.value==value);
  check(a.event.bytes==n&&b.event.bytes==n);
  check(a.x87_tag==0&&b.x87_tag==0);
  if(expected==0x005b0a40)check(a.mmx_dirty_tag!=0&&b.mmx_dirty_tag!=0);
  check(std::memcmp(&a,&b,sizeof(Result))==0);
  ++cases;
 }
 std::printf("cases=%d checks=%d failures=%d\n",cases,checks,failures);
 return failures?1:0;
}
'''.replace("ORIGINAL_BYTES", body_arr)
        fixture_path = work / "fixture.cpp"
        write(fixture_path, fixture)
        cl = VC / "bin/Hostx64/x86/cl.exe"
        link = VC / "bin/Hostx64/x86/link.exe"
        src = RUN / "0053c290.cpp"
        includes = [RUN, ROOT / "iterations/v2/001-original-recovery/source/include", VC / "include"]
        includes += [SDK / "Include/10.0.26100.0" / x for x in ("ucrt", "shared", "um")]
        quoted: set[Path] = set()
        shared_src = ROOT / "iterations/v2/001-original-recovery/source/recovered/Porsche.exe/shared_runtime_globals.cpp"
        for path in (src, fixture_path, shared_src):
            quoted_inputs(path.resolve(), includes, quoted)
        receipt["inputs_sha256"] = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p)
                                     for p in sorted(quoted)}
        receipt["inputs_sha256"].update({"local/game/Porsche.exe": PE_SHA,
                                          f"{HEAD}:{UPSTREAM}": hashlib.sha256(upstream).hexdigest(),
                                          "original-0053c290.bin": sha(work / "original-0053c290.bin"),
                                          str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())})
        receipt["tools_sha256"] = {str(p.relative_to(ROOT)): sha(p) for p in (cl, link)}
        cmd = [str(cl), "/nologo", "/c", "/std:c++17", "/arch:SSE2", "/Od", "/Oi", "/MT", "/GS-", "/EHsc",
               "/TP", "/W4", "/utf-8"]
        cmd += ["/I" + str(p) for p in includes]
        cmd += ["/Fo" + str(work) + "\\", str(src), str(fixture_path),
                str(shared_src)]
        run(cmd, "compile")
        dumpbin = VC / "bin/Hostx64/x86/dumpbin.exe"
        receipt["tools_sha256"][str(dumpbin.relative_to(ROOT))] = sha(dumpbin)
        symbols = run([str(dumpbin), "/symbols", str(work / "0053c290.obj")], "symbols").stdout
        receipt["game_object_symbols"] = {
            "defined": re.findall(r"SECT\d+\s+notype.*External\s+\|\s+(\?\S+)", symbols),
            "undefined": re.findall(r"UNDEF\s+notype.*External\s+\|\s+(\?\S+)", symbols),
        }
        libs = [VC / "lib/x86/libcmt.lib", VC / "lib/x86/libvcruntime.lib",
                SDK / "Lib/10.0.26100.0/ucrt/x86/libucrt.lib",
                SDK / "Lib/10.0.26100.0/um/x86/kernel32.lib"]
        receipt["link_libraries_sha256"] = {str(p): sha(p) for p in libs}
        objs = [work / (p + ".obj") for p in ("0053c290", "fixture", "shared_runtime_globals")]
        receipt["objects_sha256"] = {p.name: sha(p) for p in objs}
        exe = work / "fixture.exe"
        run([str(link), "/nologo", "/MACHINE:X86", "/SUBSYSTEM:CONSOLE", "/NODEFAULTLIB",
             "/OUT:" + str(exe), *map(str, objs), *map(str, libs)], "link")
        receipt["exe_sha256"] = sha(exe)
        p = run([str(exe)], "native", timeout=30)
        m = re.fullmatch(r"cases=(\d+) checks=(\d+) failures=(\d+)\s*", p.stdout)
        if not m or int(m[1]) != 28 or int(m[3]) != 0:
            raise RuntimeError("native output mismatch")
        receipt["native_cases_passed"] = int(m[1])
        receipt["native_checks"] = int(m[2])
        receipt["status"] = "pass"
    except Exception as exc:
        receipt["status"] = "fail"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        write(work / "error.log", traceback.format_exc())
        print(receipt["error"], file=sys.stderr)
    finally:
        write(receipt_path, json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        print(receipt_path)
    if receipt["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

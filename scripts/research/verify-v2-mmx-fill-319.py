"""Original-PE Win32 differential fixture for Run319 MMX fill."""

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
RUN = ROOT / "iterations/v2/001-original-recovery/runs/319-mmx-fill-backend"
OUT = ROOT / "local/experiments/v2-mmx-fill-319"
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
    receipt: dict = {"schema": 1, "attempt": n, "status": "started",
                     "source": str(RUN.relative_to(ROOT)).replace("\\", "/"), "commands": []}
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

        pe_path = ROOT / "local/game/Porsche.exe"
        if sha(pe_path) != PE_SHA:
            raise RuntimeError("retail PE SHA mismatch")
        span = pe_body(pe_path.read_bytes(), 0x005B0A40, 176)
        (work / "original-005b0a40.bin").write_bytes(span)
        if span[:4] != b"\x8b\x44\x24\x04" or span[-5:] != b"\xe9\x63\xff\xff\xff":
            raise RuntimeError("unexpected original MMX entry/tail bytes")
        original_arr = ",".join(f"0x{x:02x}" for x in span)
        fixture = r'''#include "005b0a40.hpp"
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mmintrin.h>
using U=std::uint32_t;
using Fn=void* (__cdecl*)(void*,U,U);
static unsigned char original_span[176]={ORIGINAL_BYTES};
static unsigned char* code=nullptr;
static int checks=0,failures=0,cases=0;
static void check(bool yes){++checks;if(!yes)++failures;}
struct Registers {U eax,esp_before,esp_after,ebx_before,ebx_after,esi_before,esi_after,edi_before,edi_after,ebp_before,ebp_after,tag;std::uint64_t mm0;};
static Registers invoke(Fn fn,void* dst,U value,U count){
 Registers r{};
 U eax_result=0,ebx_before=0,ebx_after=0,esi_before=0,esi_after=0;
 U edi_before=0,edi_after=0,ebp_before=0,ebp_after=0,esp_before=0,esp_after=0;
 __declspec(align(16)) unsigned char fx[512]{};
 _mm_empty();
 __asm {
  mov esp_before,esp
  mov ebx_before,ebx
  mov esi_before,esi
  mov edi_before,edi
  mov ebp_before,ebp
  push count
  push value
  push dst
  mov eax,fn
  call eax
  add esp,12
  mov eax_result,eax
  mov esp_after,esp
  mov ebx_after,ebx
  mov esi_after,esi
  mov edi_after,edi
  mov ebp_after,ebp
  lea eax,fx
  fxsave [eax]
 }
 r={eax_result,esp_before,esp_after,ebx_before,ebx_after,esi_before,esi_after,
    edi_before,edi_after,ebp_before,ebp_after,fx[4],0};
 std::memcpy(&r.mm0,fx+32,8);
 _mm_empty();
 return r;
}
static bool intact(const Registers& r){
 return r.esp_before==r.esp_after&&r.ebx_before==r.ebx_after&&
        r.esi_before==r.esi_after&&r.edi_before==r.edi_after&&r.ebp_before==r.ebp_after;
}
static void init_code(){
 code=(unsigned char*)VirtualAlloc(nullptr,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 check(code!=nullptr);if(!code)return;
 std::memcpy(code,original_span,sizeof(original_span));
 DWORD old=0;check(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old)!=0);
 check(FlushInstructionCache(GetCurrentProcess(),code,sizeof(original_span))!=0);
}
static void one(U alignment,U count,U value){
 __declspec(align(16)) unsigned char original[512],candidate[512],adapter[512];
 std::memset(original,0x5a,sizeof(original));
 std::memset(candidate,0x5a,sizeof(candidate));
 std::memset(adapter,0x5a,sizeof(adapter));
 auto* a=original+64+alignment;auto* b=candidate+64+alignment;
 auto* c=adapter+64+alignment;
 Registers x=invoke(reinterpret_cast<Fn>(code),a,value,count);
 Registers y=invoke(&porsche::heap_fill_mmx_005b0a40_core,b,value,count);
 _mm_empty();
 porsche::heap_fill_mmx_005b0a40(c,value,count);
 __declspec(align(16)) unsigned char adapter_fx[512]{};
 __asm { lea eax,adapter_fx
         fxsave [eax] }
 std::uint64_t adapter_mm0=0;std::memcpy(&adapter_mm0,adapter_fx+32,8);
 _mm_empty();
 check(intact(x));check(intact(y));
 check(x.eax==U(a+count));check(y.eax==U(b+count));
 const std::uint64_t packed=(std::uint64_t(value)<<32)|value;
 check(x.tag==0xff&&y.tag==0xff&&adapter_fx[4]==0xff);
 check(x.mm0==packed&&y.mm0==packed&&adapter_mm0==packed);
 check(std::memcmp(original,candidate,sizeof(original))==0);
 check(std::memcmp(original,adapter,sizeof(original))==0);
 bool guards=true;
 for(U i=0;i<512;++i)
  if((i<64+alignment||i>=64+alignment+count) &&
     (original[i]!=0x5a||candidate[i]!=0x5a||adapter[i]!=0x5a))guards=false;
 check(guards);
 ++cases;
}
int main(){
 init_code();if(!code)return 2;
 const U counts[]={0,1,2,3,4,7,8,15,16,23,24,25,31,32,33,39,40,41,63,64,65,95,96,97,127,128,129,255,256,257};
 const U patterns[]={0,0xa1b2c3d4u,0xffffffffu};
 for(U align=0;align<16;++align)for(U n:counts)for(U v:patterns)one(align,n,v);
 std::printf("cases=%d checks=%d failures=%d\n",cases,checks,failures);
 return failures?1:0;
}
'''.replace("ORIGINAL_BYTES", original_arr)
        fixture_path = work / "fixture.cpp"
        write(fixture_path, fixture)

        cl = VC / "bin/Hostx64/x86/cl.exe"
        link = VC / "bin/Hostx64/x86/link.exe"
        dumpbin = VC / "bin/Hostx64/x86/dumpbin.exe"
        source = RUN / "005b0a40.cpp"
        includes = [RUN, ROOT / "iterations/v2/001-original-recovery/source/include", VC / "include"]
        includes += [SDK / "Include/10.0.26100.0" / x for x in ("ucrt", "shared", "um")]
        quoted: set[Path] = set()
        for path in (source, fixture_path):
            quoted_inputs(path.resolve(), includes, quoted)
        receipt["inputs_sha256"] = {str(p.relative_to(ROOT)).replace("\\", "/") if p.is_relative_to(ROOT) else str(p): sha(p)
                                     for p in sorted(quoted)}
        receipt["inputs_sha256"].update({"local/game/Porsche.exe": PE_SHA,
            "original-005b0a40.bin": sha(work / "original-005b0a40.bin"),
            "scripts/research/verify-v2-mmx-fill-319.py": sha(Path(__file__).resolve())})
        receipt["tools_sha256"] = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p)
                                    for p in (cl, link, dumpbin)}
        cmd = [str(cl), "/nologo", "/c", "/std:c++17", "/arch:SSE2", "/Od", "/Oy-", "/MT", "/GS-", "/EHsc", "/TP", "/W4", "/utf-8"]
        cmd += ["/I" + str(p) for p in includes]
        cmd += ["/Fo" + str(work) + "\\", str(source), str(fixture_path)]
        run(cmd, "compile")
        symbols = run([str(dumpbin), "/symbols", str(work / "005b0a40.obj")], "symbols").stdout
        receipt["game_object_symbols"] = {
            "defined": re.findall(r"SECT\d+\s+notype.*External\s+\|\s+(\?\S+)", symbols),
            "undefined": re.findall(r"UNDEF\s+notype.*External\s+\|\s+(\?\S+)", symbols),
        }
        libs = [VC / "lib/x86/libcmt.lib", VC / "lib/x86/libvcruntime.lib",
                SDK / "Lib/10.0.26100.0/ucrt/x86/libucrt.lib",
                SDK / "Lib/10.0.26100.0/um/x86/kernel32.lib"]
        receipt["link_libraries_sha256"] = {str(p): sha(p) for p in libs}
        objs = [work / "005b0a40.obj", work / "fixture.obj"]
        receipt["objects_sha256"] = {p.name: sha(p) for p in objs}
        exe = work / "fixture.exe"
        run([str(link), "/nologo", "/MACHINE:X86", "/SUBSYSTEM:CONSOLE", "/NODEFAULTLIB",
             "/OUT:" + str(exe), *map(str, objs), *map(str, libs)], "link")
        receipt["exe_sha256"] = sha(exe)
        p = run([str(exe)], "native", timeout=30)
        m = re.fullmatch(r"cases=(\d+) checks=(\d+) failures=(\d+)\s*", p.stdout)
        if not m or int(m[1]) != 1440 or int(m[3]) != 0:
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
        path = work / "receipt.json"
        write(path, json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        print(path)
    if receipt["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

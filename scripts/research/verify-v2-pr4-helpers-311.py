"""Read original 004a54b0/e0 bytes and compare a fresh Win32 COFF with them.

The fixture is generated under local/experiments. No upstream fixture, object,
receipt, or executable is trusted or executed.
"""

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/311-pr4-shutdown-helpers"
OUT = ROOT / "local/experiments/v2-pr4-helpers-311"
EXE = ROOT / "local/game/Porsche.exe"
ORIGINAL_SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
SOURCES = (RUN / "shutdown_helpers_311.cpp", RUN / "shutdown_helpers_311.hpp")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pe_bytes(data, va, size):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    image_base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    rva = va - image_base
    for index in range(section_count):
        section = pe + 24 + optional_size + index * 40
        virtual_size, section_rva, raw_size, raw_offset = struct.unpack_from("<IIII", data, section + 8)
        if section_rva <= rva and rva + size <= section_rva + min(virtual_size, raw_size):
            start = raw_offset + rva - section_rva
            return data[start : start + size]
    raise ValueError(f"VA outside raw PE sections: {va:08x}")


def c_array(data):
    return ", ".join(f"0x{value:02x}" for value in data)


FIXTURE = r'''#include "shutdown_helpers_311.hpp"
#include <windows.h>
#include <cstdint>
#include <cstddef>

// Fixture-only compiler support. Volatile writes prevent the optimizer from
// lowering this definition back into an unresolved call to memset.
extern "C" void* __cdecl memset(void* target, int value, std::size_t bytes) {
    auto* output = static_cast<volatile unsigned char*>(target);
    for (std::size_t i = 0; i < bytes; ++i) output[i] = static_cast<unsigned char>(value);
    return target;
}

using U = std::uint32_t;
static_assert(sizeof(void*) == 4, "Win32 fixture required");
static const unsigned char kOriginalB0[44] = { @BYTES_B0@ };
static const unsigned char kOriginalE0[5] = { @BYTES_E0@ };

static void* g_after_cleanup;
static void* g_after_destroy;
static void* g_after_free;
static U g_events[12];
static U g_event_count;
static U g_passed;
static unsigned char g_network_a, g_network_b, g_network_c;

static void log_event(U kind, const void* receiver) {
    if (g_event_count + 2 > 12) ExitProcess(91);
    g_events[g_event_count++] = kind;
    g_events[g_event_count++] = reinterpret_cast<U>(receiver);
}

namespace porsche {
void* startup_network_00628c70;
std::uint32_t __cdecl install_paths_cleanup_004b7070() {
    log_event(1, startup_network_00628c70);
    startup_network_00628c70 = g_after_cleanup;
    return 0x751101u;
}
void __thiscall ShutdownNetwork311::destroy_0048ff30() {
    log_event(2, this);
    startup_network_00628c70 = g_after_destroy;
}
std::uint32_t __cdecl application_release_0059f050(void* address) {
    log_event(3, address);
    startup_network_00628c70 = g_after_free;
    return 0x751103u;
}
void __cdecl platform_flush_0059eb20() {
    log_event(4, startup_network_00628c70);
    startup_network_00628c70 = g_after_free;
}
} // namespace porsche

struct Observation {
    U before_esp, after_esp, before_ebp, after_ebp;
    U before_ebx, after_ebx, before_esi, after_esi, before_edi, after_edi;
    U after_eax, event_count, events[12], final_network;
};

static void copy_bytes(void* target, const void* source, U bytes) {
    auto* dst = static_cast<unsigned char*>(target);
    const auto* src = static_cast<const unsigned char*>(source);
    for (U i = 0; i < bytes; ++i) dst[i] = src[i];
}
static void patch_u32(unsigned char* where, U value) {
    copy_bytes(where, &value, 4);
}
static void patch_rel32(unsigned char* where, const void* target) {
    U from = reinterpret_cast<U>(where + 4);
    U to = reinterpret_cast<U>(target);
    patch_u32(where, to - from);
}

static void reset_case(int scenario) {
    for (U& event : g_events) event = 0;
    g_event_count = 0;
    porsche::startup_network_00628c70 = scenario == 0 ? nullptr : &g_network_a;
    g_after_cleanup = scenario == 2 ? &g_network_b :
                      scenario == 3 ? nullptr : porsche::startup_network_00628c70;
    g_after_destroy = &g_network_c;
    g_after_free = &g_network_c;
}

static Observation invoke(void (__cdecl *fn)()) {
    Observation o = {};
    __asm {
        mov ecx, fn
        lea edx, o
        mov [edx], esp
        mov [edx + 8], ebp
        mov [edx + 16], ebx
        mov [edx + 24], esi
        mov [edx + 32], edi
        call ecx
        lea edx, o
        mov [edx + 40], eax
        mov [edx + 4], esp
        mov [edx + 12], ebp
        mov [edx + 20], ebx
        mov [edx + 28], esi
        mov [edx + 36], edi
    }
    o.event_count = g_event_count;
    for (U i = 0; i < 12; ++i) o.events[i] = g_events[i];
    o.final_network = reinterpret_cast<U>(porsche::startup_network_00628c70);
    return o;
}

static bool same(const Observation& a, const Observation& b, bool compare_eax) {
    if (a.before_esp != a.after_esp || b.before_esp != b.after_esp) return false;
    if (a.before_ebp != a.after_ebp || b.before_ebp != b.after_ebp) return false;
    if (a.before_ebx != a.after_ebx || b.before_ebx != b.after_ebx) return false;
    if (a.before_esi != a.after_esi || b.before_esi != b.after_esi) return false;
    if (a.before_edi != a.after_edi || b.before_edi != b.after_edi) return false;
    if (compare_eax && a.after_eax != b.after_eax) return false;
    if (a.event_count != b.event_count || a.final_network != b.final_network) return false;
    for (U i = 0; i < 12; ++i) if (a.events[i] != b.events[i]) return false;
    return true;
}

extern "C" int main() {
    unsigned char* slab = static_cast<unsigned char*>(VirtualAlloc(
        nullptr, 4096, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
    if (!slab) ExitProcess(90);
    copy_bytes(slab, kOriginalB0, 44);
    copy_bytes(slab + 64, kOriginalE0, 5);
    patch_rel32(slab + 2, reinterpret_cast<const void*>(&porsche::install_paths_cleanup_004b7070));
    patch_u32(slab + 8, reinterpret_cast<U>(&porsche::startup_network_00628c70));
    union MethodAddress {
        void (__thiscall porsche::ShutdownNetwork311::*method)();
        U address;
    } method_address = {};
    static_assert(sizeof(method_address) == 4, "single-inheritance thiscall address required");
    method_address.method = &porsche::ShutdownNetwork311::destroy_0048ff30;
    patch_rel32(slab + 19, reinterpret_cast<const void*>(method_address.address));
    patch_rel32(slab + 25, reinterpret_cast<const void*>(&porsche::application_release_0059f050));
    patch_u32(slab + 34, reinterpret_cast<U>(&porsche::startup_network_00628c70));
    patch_rel32(slab + 65, reinterpret_cast<const void*>(&porsche::platform_flush_0059eb20));
    DWORD previous_protection = 0;
    if (!VirtualProtect(slab, 4096, PAGE_EXECUTE_READ, &previous_protection)) ExitProcess(92);
    if (!FlushInstructionCache(GetCurrentProcess(), slab, 4096)) ExitProcess(93);

    auto original_b0 = reinterpret_cast<void (__cdecl *)()>(slab);
    auto original_e0 = reinterpret_cast<void (__cdecl *)()>(slab + 64);
    for (int scenario = 0; scenario < 4; ++scenario) {
        reset_case(scenario);
        Observation original = invoke(original_b0);
        reset_case(scenario);
        Observation cpp = invoke(&porsche::application_main_function_004a54b0);
        if (!same(original, cpp, false)) ExitProcess(10 + scenario);
        U expected_events = scenario == 0 || scenario == 3 ? 2 : 6;
        if (original.event_count != expected_events || original.final_network != 0) ExitProcess(20 + scenario);
        if (scenario == 2 && (original.events[2] != 2 ||
                              original.events[3] != reinterpret_cast<U>(&g_network_b) ||
                              original.events[5] != reinterpret_cast<U>(&g_network_b))) ExitProcess(30);
        ++g_passed;
    }
    reset_case(1);
    Observation original = invoke(original_e0);
    reset_case(1);
    Observation cpp = invoke(&porsche::application_main_function_004a54e0);
    if (!same(original, cpp, true) || original.event_count != 2 ||
        original.events[0] != 4) ExitProcess(40);
    ++g_passed;
    return g_passed == 5 ? 0 : 50;
}
'''


def locate_compiler(explicit):
    candidates = [(ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)] if explicit else []
    local_tools = ROOT / "local/tools/BuildTools/VC/Tools/MSVC"
    if local_tools.exists():
        candidates.extend(sorted(local_tools.glob("*/bin/Hostx64/x86/cl.exe"), reverse=True))
    on_path = shutil.which("cl.exe")
    if on_path:
        candidates.append(Path(on_path))
    for year in ("18", "2022", "2019"):
        for edition in ("Community", "Professional", "Enterprise", "BuildTools"):
            base = Path("C:/Program Files/Microsoft Visual Studio") / year / edition / "VC/Tools/MSVC"
            if base.exists():
                candidates.extend(sorted(base.glob("*/bin/Hostx64/x86/cl.exe"), reverse=True))
    return next((p.resolve() for p in candidates if p.is_file()), None)


def run_command(name, command, cwd, output=None):
    started = time.perf_counter()
    spawn_error = None
    try:
        process = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True, timeout=120)
        exit_code = process.returncode
        output_bytes = process.stdout + process.stderr
    except OSError as error:
        spawn_error = str(error)
        exit_code = None
        output_bytes = spawn_error.encode("utf-8", errors="replace")
    log = OUT / f"{name}.log"
    log.write_bytes(output_bytes)
    receipt = {
        "command": [str(x) for x in command],
        "exit_code": exit_code,
        "seconds": round(time.perf_counter() - started, 6),
        "log": str(log.relative_to(ROOT)).replace("\\", "/"),
        "log_sha256": sha(log),
    }
    if spawn_error is not None:
        receipt["spawn_error"] = spawn_error
    if output is not None and Path(output).is_file():
        receipt["output"] = str(Path(output).relative_to(ROOT)).replace("\\", "/")
        try:
            receipt["output_sha256"] = sha(output)
        except OSError as error:
            receipt["output_read_error"] = str(error)
    write_json(OUT / f"{name}.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--cl", help="path to the Win32 MSVC compiler")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    if args.attempt < 1:
        parser.error("attempt must be positive")
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = f"attempt-{args.attempt:03d}"
    report = OUT / f"{prefix}.json"
    if report.exists():
        raise SystemExit(f"Refusing to overwrite {report}")

    data = EXE.read_bytes()
    if sha(EXE) != ORIGINAL_SHA:
        raise SystemExit("Original Porsche.exe SHA mismatch")
    b0 = pe_bytes(data, 0x004A54B0, 44)
    e0 = pe_bytes(data, 0x004A54E0, 5)
    if b0[:2] != bytes.fromhex("56e8") or b0[-2:] != bytes.fromhex("5ec3"):
        raise SystemExit("004a54b0 body signature mismatch")
    if e0[0] != 0xE9:
        raise SystemExit("004a54e0 is not the expected tail JMP")
    for offset, target in ((1, 0x004B7070), (18, 0x0048FF30), (24, 0x0059F050)):
        if b0[offset] != 0xE8:
            raise SystemExit(f"Missing CALL at 004a54b0+{offset:x}")
        displacement = struct.unpack_from("<i", b0, offset + 1)[0]
        if 0x004A54B0 + offset + 5 + displacement != target:
            raise SystemExit(f"Wrong original callee at 004a54b0+{offset:x}")
    if struct.unpack_from("<I", b0, 8)[0] != 0x00628C70 or struct.unpack_from("<I", b0, 34)[0] != 0x00628C70:
        raise SystemExit("004a54b0 does not use the canonical 00628c70 cell")
    if 0x004A54E5 + struct.unpack_from("<i", e0, 1)[0] != 0x0059EB20:
        raise SystemExit("004a54e0 tail target mismatch")
    fixture = OUT / f"{prefix}-fixture.cpp"
    fixture.write_text(FIXTURE.replace("@BYTES_B0@", c_array(b0)).replace("@BYTES_E0@", c_array(e0)), encoding="utf-8")
    inputs = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p)
              for p in (EXE, *SOURCES, Path(__file__), fixture)}
    result = {"schema": 1, "run": 311, "attempt": args.attempt, "original_sha256": ORIGINAL_SHA,
              "original_vas": ["004a54b0", "004a54e0"], "original_bytes": 49,
              "fixture": str(fixture.relative_to(ROOT)).replace("\\", "/"),
              "input_sha256": inputs, "status": "static-pe-verified", "native_cases_passed": 0}
    if args.static_only:
        write_json(report, result)
        print(json.dumps({"status": result["status"], "report": str(report)}))
        return

    compiler = locate_compiler(args.cl)
    if compiler is None:
        result["status"] = "native-blocked-no-win32-msvc"
        write_json(report, result)
        raise SystemExit("Win32 MSVC cl.exe unavailable; original bytes verified, native test not run")
    linker = compiler.with_name("link.exe")
    vc_include = compiler.parents[3] / "include"
    sdk = Path("C:/Program Files (x86)/Windows Kits/10")
    kit = "10.0.26100.0"
    includes = [ROOT / "iterations/v2/001-original-recovery/source/include", RUN, vc_include,
                sdk / "Include" / kit / "ucrt", sdk / "Include" / kit / "shared",
                sdk / "Include" / kit / "um"]
    libraries = [compiler.parents[3] / "lib/x86/libcmt.lib",
                 compiler.parents[3] / "lib/x86/libvcruntime.lib",
                 sdk / "Lib" / kit / "ucrt/x86/libucrt.lib",
                 sdk / "Lib" / kit / "um/x86/kernel32.lib"]
    if not linker.is_file() or not all(p.is_file() for p in libraries) or not all(p.is_dir() for p in includes):
        raise SystemExit("Win32 linker or pinned include/SDK roots unavailable")
    tools = {"cl.exe": compiler, "link.exe": linker,
             **{path.name: path for path in libraries}}
    result["toolchain_sha256"] = {name: sha(path) for name, path in tools.items()}
    result["toolchain_paths"] = {name: str(path) for name, path in tools.items()}
    result["receipts"] = {}
    objs = [OUT / f"{prefix}-game.obj", OUT / f"{prefix}-fixture.obj"]
    for label, source, obj in (("game", SOURCES[0], objs[0]), ("fixture", fixture, objs[1])):
        command = [compiler, "/nologo", "/c", "/TP", "/std:c++17", "/Od", "/GS-", "/GR-", "/EHsc-", "/W4",
                   *[part for root in includes for part in ("/I", root)], f"/Fo{obj}", source]
        receipt = run_command(f"{prefix}-compile-{label}", command, OUT, obj)
        result["receipts"][f"compile_{label}"] = receipt
        if receipt["exit_code"]:
            result["status"] = "native-compile-failed"
            write_json(report, result)
            raise SystemExit(receipt["exit_code"])
    native = OUT / f"{prefix}-native.exe"
    receipt = run_command(f"{prefix}-link", [linker, "/nologo", "/MACHINE:X86", "/SUBSYSTEM:CONSOLE",
                                             "/NODEFAULTLIB", "/INCREMENTAL:NO", f"/OUT:{native}", *objs, *libraries], OUT, native)
    result["receipts"]["link"] = receipt
    if receipt["exit_code"]:
        result["status"] = "native-link-failed"
        write_json(report, result)
        raise SystemExit(receipt["exit_code"])
    if "output_sha256" not in receipt:
        result["status"] = "native-executable-unreadable"
        write_json(report, result)
        raise SystemExit("Linked fixture EXE cannot be read; native comparison was not run")
    receipt = run_command(f"{prefix}-execute", [native], OUT)
    result["receipts"]["execute"] = receipt
    result["native_cases_passed"] = 5 if receipt["exit_code"] == 0 else 0
    result["status"] = "native-pass" if receipt["exit_code"] == 0 else "native-divergence"
    result["native_executable_sha256"] = sha(native)
    write_json(report, result)
    if receipt["exit_code"]:
        raise SystemExit(receipt["exit_code"])
    print(json.dumps({"status": result["status"], "cases": 5, "report": str(report)}))


if __name__ == "__main__":
    main()

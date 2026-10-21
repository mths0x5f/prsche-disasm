"""Run 430 (branch feat/lowered-whole-game): hardware oracle for the lowered `lock inc/dec`.

The game's only LOCK instructions are `lock inc/dec dword ptr [006c02e8]` (CRT locale reader
count, 005ae3c0/005ae490). The lowering (SEMANTIC_PATCHES in build-v2-lowered-exe-430.py) uses
_InterlockedExchangeAdd. This oracle checks, on this CPU, with the operand as [esi]:
1. flags and memory: native vs lowered from the same random value and EFLAGS (100000 cases,
   including 0x7fffffff/0x80000000/0xffffffff/0 edges);
2. atomicity: two threads run the lowered instruction 2,000,000 times each on one counter;
   the result must be exact. A negative control (the plain read-modify-write lowering) must
   lose updates.

Usage: py -3 scripts/research/verify-v2-lock-430.py
"""
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'local/experiments/v2-lock-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'

HARNESS = r'''
#include <windows.h>
#include <stdio.h>
#include "machine257.h"
void dispatch257(Machine257& s, U target) { s.stop = Stop257::BadReturn; (void)target; }
void unlowered430(Machine257& s) { s.stop = Stop257::BadReturn; }
void translated_10000000(Machine257& s);   // lock inc dword ptr [esi]; ret
void translated_10000100(Machine257& s);   // lock dec dword ptr [esi]; ret
void plain_inc(Machine257& s);             // negative control: non-atomic read-modify-write
static unsigned long long rng = 88172645463325252ull;
static U rnd() { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return (U)rng; }
static const unsigned char INC[] = {0xf0, 0xff, 0x06, 0xc3}, DEC[] = {0xf0, 0xff, 0x0e, 0xc3};
static U cell, flags_in, flags_n, code_ptr, saved_esi;
__declspec(naked) static void run_native() {
    __asm {
        push esi
        pushfd
        pop eax
        and eax, 0xfffff72a
        or eax, flags_in
        push eax
        popfd
        lea esi, cell
        call code_ptr
        pushfd
        pop flags_n
        pop esi
        ret
    }
}
static volatile U counter;
static Lowered_dummy;
static DWORD WINAPI worker(void* p) {
    void (*fn)(Machine257&) = (void (*)(Machine257&))p;
    U stack[8]; Machine257 s; memset(&s, 0, sizeof(s));
    for (int k = 0; k < 2000000; ++k) {
        stack[4] = 0; s.r[4] = (U)&stack[4]; s.r[6] = (U)&counter; s.stop = Stop257::Running;
        fn(s);
    }
    return 0;
}
int main() {
    unsigned char* exec = (unsigned char*)VirtualAlloc(0, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    int bad = 0;
    static const U edges[] = {0u, 1u, 0x7fffffffu, 0x80000000u, 0xffffffffu, 0x7ffffffeu, 0x80000001u};
    for (int op = 0; op < 2; ++op) {
        memcpy(exec, op ? DEC : INC, 4); FlushInstructionCache(GetCurrentProcess(), exec, 4096); code_ptr = (U)exec;
        for (int c = 0; c < 100000; ++c) {
            U v = c < 7 ? edges[c] : rnd(); flags_in = rnd() & 0x8d5u;
            cell = v; run_native(); U nv = cell, nf = flags_n;
            U stack[8]; stack[4] = 0; Machine257 s; memset(&s, 0, sizeof(s));
            cell = v; s.r[6] = (U)&cell; s.r[4] = (U)&stack[4]; s.flags = flags_in;
            if (op) translated_10000100(s); else translated_10000000(s);
            if (cell != nv || (s.flags & 0x8d5u) != (nf & 0x8d5u)) { if (!bad) printf("diff op=%d v=%08x\n", op, v); ++bad; }
        }
    }
    printf("flags_memory_cases 200000 bad %d\n", bad);
    void* fns[2] = {(void*)translated_10000000, (void*)plain_inc};
    const char* names[2] = {"lowered", "plain"};
    U results[2];
    for (int k = 0; k < 2; ++k) {
        counter = 0;
        HANDLE t[2] = {CreateThread(0, 0, worker, fns[k], 0, 0), CreateThread(0, 0, worker, fns[k], 0, 0)};
        WaitForMultipleObjects(2, t, TRUE, INFINITE);
        results[k] = counter;
        printf("atomicity %s %u of 4000000\n", names[k], counter);
    }
    int ok = bad == 0 && results[0] == 4000000u && results[1] != 4000000u;
    printf("%s\n", ok ? "PASS" : "FAIL");
    return !ok;
}
'''


def main():
    spec = importlib.util.spec_from_file_location('build430', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    translate, header = b.backend()
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'machine257.h').write_text(header, encoding='utf-8')
    inc, _ = translate(bytes.fromhex('f0ff06c3'), 0x10000000)
    dec, _ = translate(bytes.fromhex('f0ff0ec3'), 0x10000100)
    plain = ('void plain_inc(Machine257&s){ U a=read257(s.r[6],4u); write257(s.r[6],4u,a+1u); '
             's.stop=Stop257::Returned; }\n')
    (WORK / 'fragments.cpp').write_text(inc + '\n' + dec.replace('#include "machine257.h"\n', '') + '\n' + plain,
                                        encoding='utf-8')
    (WORK / 'harness.cpp').write_text(HARNESS.replace('static Lowered_dummy;\n', ''), encoding='utf-8')
    cl, link, env = b.toolchain()
    r = subprocess.run([str(cl), '/nologo', '/TP', '/std:c++17', '/O2', '/GS-', '/EHs-c-', '/W0', f'/I{WORK}',
                        'harness.cpp', 'fragments.cpp', '/Fe:lock.exe'], cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit('compile failed')
    run = subprocess.run([str(WORK / 'lock.exe')], cwd=WORK, capture_output=True, text=True)
    print(run.stdout)
    (RUN / 'lock-oracle.json').write_text(json.dumps(dict(schema=1, output=run.stdout.splitlines(),
                                                          exit_code=run.returncode), indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

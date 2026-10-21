"""Run 430 (branch feat/lowered-whole-game): hardware oracle for the native x87/MMX/RCPSS lowering.

Every distinct x87, MMX and RCPSS instruction form used by Porsche.exe (mnemonic + operand kinds,
taken from the catalogued code) becomes a fragment: the original instruction, with its memory
operand re-encoded as [esi] and as [esi+ebx*2+0x10], followed by RET. Each fragment runs on this
CPU twice per case, natively and through the Run 430 lowering (build-v2-lowered-exe-430.py
backend), from the same random state:
- GPRs, arithmetic EFLAGS, MXCSR and XMM0-7;
- a random x87 image restored with FRSTOR: TOP, C0-C3, sticky flags, every precision and
  rounding control, tags consistent with contents (normals, zeros, infinities, NaNs,
  denormals, unnormal-free) and empty registers for stack under/overflow;
- a 512-byte memory buffer whose first 108 bytes are another valid FNSAVE image (so FRSTOR and
  FLDENV operands are well formed) and the rest random.
After each run it compares GPRs (ESP excluded), EFLAGS & 0x8d5, MXCSR, XMM, the memory buffer
and the FNSAVE image (FIP/FCS/opcode excluded: those name the instruction's own address and
encoding, which differ by design between [esi] and the lowering's [ecx]).

Usage: py -3 scripts/research/verify-v2-native-fpu-430.py [--cases N]
Output: local/experiments/v2-native-fpu-430/ (work files) and
iterations/v2/001-original-recovery/runs/430-lowered-whole-game/native-fpu-oracle.json
"""
import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'local/experiments/v2-native-fpu-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
CATALOG = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'


# Negative controls: each must make the oracle fail at least one form.
MUTANTS = {
    'address+4': ('U a_=', 'U a_=4u+'),                                  # wrong memory operand
    'fnstsw-lost': ('s.r[0]=(s.r[0]&0xffff0000u)|(g_&0xffffu);', ''),    # status word not stored
    'gpr-load': ('U g_=s.r[', 'U g_=1u+s.r['),                          # GPR operand read wrong
    'xmm-store': ('movups [edx], xmm0', 'movups [edx], xmm1'),           # XMM result lost
    'emulated': None,                                                     # previous emulation
    'no-parity': None,                                                    # header: PF never set
    'no-af': None,                                                        # header: AF never set
    # Not applicable to this game (no such forms in Porsche.exe, so no form can fail): fcomi /
    # fucomi EFLAGS bridging, fcmov condition flags, a GPR destination of movd.
}


def load_build():
    spec = importlib.util.spec_from_file_location('build430', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EXCLUDED_INT = {'push', 'pop', 'call', 'ret', 'jmp', 'leave', 'enter', 'int3', 'rdtsc', 'cpuid', 'pushal',
                'popal', 'pushfd', 'popfd', 'lock', 'rep', 'repne', 'repe', 'stosb', 'stosw', 'stosd', 'movsb',
                'movsw', 'movsd', 'lodsb', 'lodsd', 'scasb', 'cmpsb', 'xlatb', 'nop', 'prefetcht0', 'prefetchw',
                'jecxz', 'ldmxcsr', 'stmxcsr', 'loop'}


def wanted(b, i, which):
    """fpu: the natively executed x87/MMX/RCPSS forms; int: every other data instruction whose
    operands the harness controls (no control flow, stack, string/rep, time or CPU-id, no ESP)."""
    if which == 'fpu':
        return bool(b.native_kind(i))
    m = i.mnemonic
    if which == 'sse':
        xmm = any(op.type == 1 and i.reg_name(op.reg).startswith('xmm') for op in i.operands)
        return (xmm or m in ('ldmxcsr', 'stmxcsr', 'movntps')) and not b.native_kind(i)             and not any(op.type == 3 and op.mem.segment for op in i.operands)
    if b.native_kind(i) or m in EXCLUDED_INT or m in b.THREEDNOW or m.startswith('j'):
        return False
    if any(p not in (0, 0x66) for p in i.prefix):
        return False
    for op in i.operands:
        if op.type == 1 and i.reg_name(op.reg).startswith(('xmm', 'mm')):
            return False
        if op.type == 1 and i.reg_name(op.reg) in ('esp', 'sp'):
            return False          # the harness's stack pointer differs between the two runs
        if op.type == 3 and op.mem.segment:
            return False
    regs_read, regs_write = i.regs_access()
    written = {i.reg_name(r) for r in regs_write}
    read = {i.reg_name(r) for r in regs_read}
    if written & {'esp', 'sp'}:
        return False          # the harness's own stack
    return 'esp' not in read or any(op.type == 3 for op in i.operands)


def forms(b, which='fpu'):
    """One representative instruction per (mnemonic, operand kinds) used by the game."""
    data = (ROOT / 'local/game/Porsche.exe').read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    seen = {}
    for line in CATALOG.read_text(encoding='utf-8').splitlines():
        e = json.loads(line)
        for lo, hi in e['ranges']:
            lo, hi = int(lo, 16), int(hi, 16) + 1
            for i in md.disasm(data[lo - 0x400000:hi - 0x400000], lo):
                if not wanted(b, i, which):
                    continue
                kinds = []
                for op in i.operands:
                    if op.type == 1:
                        r = i.reg_name(op.reg)
                        kinds.append(r if (r.startswith(('st', 'mm', 'xmm')) or r in b.GPR32 or r == 'ax') else 'reg')
                    elif op.type == 3:
                        kinds.append(f'm{op.size}')
                    else:
                        kinds.append('imm')
                key = (i.mnemonic, tuple(kinds))
                seen.setdefault(key, bytes(i.bytes))
    return seen


def reencode(raw, mode):
    """Memory operand -> [esi] (mode 0) or [esi+edi*2+0x10] (mode 1); same opcode/reg/imm."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    i = next(md.disasm(raw, 0))
    if not any(op.type == 3 for op in i.operands):
        return raw if mode == 0 else None
    k = i.modrm_offset
    if not k:
        return None          # moffs forms (mov eax, [abs]) have no ModRM to redirect
    reg = raw[k] & 0x38
    tail = raw[i.imm_offset:] if i.imm_offset else b''
    if mode == 0:
        return raw[:k] + bytes([reg | 0x06]) + tail
    return raw[:k] + bytes([0x80 | reg | 0x04, 0x5e]) + (0x10).to_bytes(4, 'little') + tail   # [esi+ebx*2+0x10]


HARNESS = r'''
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "machine257.h"
#define INTSET %INTSET%
void dispatch257(Machine257& s, U target) { s.stop = Stop257::BadReturn; (void)target; }
void unlowered430(Machine257& s) { s.stop = Stop257::BadReturn; }
%DECLS%
typedef void (*Lowered)(Machine257&);
struct Frag { const char* name; const unsigned char* code; U len; Lowered low; };
%FRAGS%
static unsigned long long rng = 0x9e3779b97f4a7c15ull;
static U rnd() { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return (U)(rng >> 16); }
static void put80(unsigned char* p, int kind) {
    unsigned long long man = ((unsigned long long)rnd() << 32) | rnd(); unsigned exp = rnd() & 0x7fff; unsigned sign = rnd() & 1;
    switch (kind) {
    case 0: man |= 1ull << 63; exp = 0x3fff - 40 + (rnd() % 80); break;            // normal, moderate
    case 1: man |= 1ull << 63; exp = 1 + (rnd() % 0x7ffd); break;                   // normal, any exponent
    case 2: man = 0; exp = 0; break;                                                // zero
    case 3: man = 1ull << 63; exp = 0x7fff; break;                                  // infinity
    case 4: man |= 3ull << 62; exp = 0x7fff; break;                                  // quiet NaN
    case 5: man &= ~(1ull << 63); if (!man) man = 1; exp = 0; break;                 // denormal
    case 6: man = (unsigned long long)(rnd() % 1000) << 53 | (1ull << 63); exp = 0x3fff + 9; break;  // small integer-ish
    }
    memcpy(p, &man, 8); unsigned short se = (unsigned short)((sign << 15) | exp); memcpy(p + 8, &se, 2);
}
static int kind_tag(int kind) { return kind == 2 ? 1 : (kind == 0 || kind == 1 || kind == 6) ? 0 : 2; }
static const unsigned short CW[] = {0x037f, 0x027f, 0x007f, 0x0c7f, 0x047f, 0x087f, 0x0f7f, 0x017f};
static void image(unsigned char* img) {
    memset(img, 0, 108);
    unsigned top = rnd() & 7; unsigned short tw = 0;
    for (int r = 0; r < 8; ++r) {                       // r = physical register
        int empty = (rnd() % 5) == 0; int kind = rnd() % 7;
        unsigned tag = empty ? 3 : kind_tag(kind);
        tw |= (unsigned short)(tag << (2 * r));
        int st = (r - (int)top) & 7;                     // FNSAVE stores ST(i) in order
        put80(img + 28 + 10 * st, kind);
    }
    unsigned short cw = CW[rnd() % 8]; unsigned short sw = (unsigned short)((top << 11) | (rnd() & 0x4700) | (rnd() & 0x3f & 0));
    memcpy(img + 0, &cw, 2); memcpy(img + 4, &sw, 2); memcpy(img + 8, &tw, 2);
}
alignas(16) static unsigned char fpu_in[108], fpu_n[108], fpu_l[108];
alignas(16) static U xmm_in[8][4], xmm_n[8][4], xmm_l[8][4];
static int r_in_fix;
static U r_in[8], r_n[8], flags_in, flags_n, mx_in, mx_n, mx_l, saved_esp, code_ptr;
alignas(16) static unsigned char mem_in[512], buf[512], mem_n[512];
__declspec(naked) static void run_native() {
    __asm {
        pushad
        mov saved_esp, esp
        frstor fpu_in
        movups xmm0, xmm_in[0]
        movups xmm1, xmm_in[16]
        movups xmm2, xmm_in[32]
        movups xmm3, xmm_in[48]
        movups xmm4, xmm_in[64]
        movups xmm5, xmm_in[80]
        movups xmm6, xmm_in[96]
        movups xmm7, xmm_in[112]
        ldmxcsr mx_in
        pushfd
        pop eax
        and eax, 0xfffff72a
        or eax, flags_in
        push eax
        popfd
        mov eax, r_in[0]
        mov ecx, r_in[4]
        mov edx, r_in[8]
        mov ebx, r_in[12]
        mov ebp, r_in[20]
        mov esi, r_in[24]
        mov edi, r_in[28]
        call code_ptr
        mov r_n[0], eax
        mov r_n[4], ecx
        mov r_n[8], edx
        mov r_n[12], ebx
        mov r_n[20], ebp
        mov r_n[24], esi
        mov r_n[28], edi
        pushfd
        pop flags_n
        cld
        fnsave fpu_n
        stmxcsr mx_n
        movups xmm_n[0], xmm0
        movups xmm_n[16], xmm1
        movups xmm_n[32], xmm2
        movups xmm_n[48], xmm3
        movups xmm_n[64], xmm4
        movups xmm_n[80], xmm5
        movups xmm_n[96], xmm6
        movups xmm_n[112], xmm7
        mov esp, saved_esp
        popad
        ret
    }
}
static int same_fpu(const unsigned char* a, const unsigned char* b) {
    return !memcmp(a, b, 12) && !memcmp(a + 20, b + 20, 88);
}
int main(int argc, char** argv) {
    int cases = argc > 1 ? atoi(argv[1]) : 200;
    int failed_forms = 0, total = 0;
    unsigned char* exec = (unsigned char*)VirtualAlloc(0, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    U fake_stack[64];
    for (U f = 0; f < sizeof(frags) / sizeof(frags[0]); ++f) {
        int bad = 0, skipped = 0; char why[160] = "";
        fprintf(stderr, "%s\n", frags[f].name); fflush(stderr);
        memcpy(exec, frags[f].code, frags[f].len); FlushInstructionCache(GetCurrentProcess(), exec, 4096);
        code_ptr = (U)exec;
        for (int c = 0; c < cases; ++c) {
            image(fpu_in);
            for (int k = 0; k < 512; ++k) mem_in[k] = (unsigned char)rnd();
            image(mem_in + 64);                               // a valid image at [esi]
            if (strstr(frags[f].name, "ebx*2")) { r_in_fix = 1; image(mem_in + 64 + 0x10); }  // and at [esi+ebx*2+0x10], ebx = 0
            else r_in_fix = 0;
            for (int r = 0; r < 8; ++r) r_in[r] = rnd();
            r_in[6] = (U)(buf + 64); r_in[3] = r_in_fix ? 0u : rnd() % 64; if (INTSET) r_in[7] = (U)(buf + 256);
            if (!strncmp(frags[f].name, "bt", 2)) r_in[0] = rnd() % 1024;   // bit strings stay inside the buffer
            flags_in = rnd() & 0x8d5;
            for (int r = 0; r < 8; ++r) for (int l = 0; l < 4; ++l) xmm_in[r][l] = rnd();
            mx_in = 0x1f80 | ((rnd() & 3) << 13) | ((rnd() & 1) << 15);
            memcpy(buf, mem_in, 512);
            int nf = 0; __try { run_native(); } __except (1) { nf = 1; }
            if (nf) { --c; if (++skipped > 100000) break; continue; }
            memcpy(mem_n, buf, 512);
            memcpy(buf, mem_in, 512);
            Machine257 s; memset(&s, 0, sizeof(s));
            for (int r = 0; r < 8; ++r) s.r[r] = r_in[r];
            fake_stack[32] = 0x12345678u; s.r[4] = (U)&fake_stack[32];
            s.flags = flags_in; s.mxcsr = mx_in; memcpy(s.xmm, xmm_in, sizeof(xmm_in));
            __asm frstor fpu_in
            int lf = 0; __try { frags[f].low(s); } __except (1) { lf = 1; }
            __asm fnsave fpu_l
            __asm fninit
            const char* d = 0;
            for (int r = 0; r < 8; ++r) if (r != 4 && s.r[r] != r_n[r]) d = "gpr";
            if ((s.flags & 0xcd5u) != (flags_n & 0xcd5u)) d = "eflags";
            if (memcmp(buf, mem_n, 512)) d = "memory";
            if (!same_fpu(fpu_l, fpu_n)) d = "x87 state";
            if (memcmp(s.xmm, xmm_n, sizeof(xmm_n))) d = "xmm";
            if (s.mxcsr != mx_n) d = "mxcsr";
            if (s.stop != Stop257::Returned) d = "stop";
            if (lf) d = "lowered faulted";
            ++total;
            if (d) { if (!bad) sprintf(why, "%s (case %d) flags native %03x lowered %03x in %03x", d, c, flags_n & 0x8d5u, s.flags & 0x8d5u, flags_in); ++bad; }
        }
        printf("%s\t%s\t%d/%d\n", bad ? "FAIL" : "PASS", frags[f].name, cases - bad, cases);
        if (bad) { ++failed_forms; printf("  first difference: %s\n", why); }
    }
    printf("forms %u failed %d cases %d\n", (U)(sizeof(frags) / sizeof(frags[0])), failed_forms, total);
    return failed_forms != 0;
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=int, default=300)
    ap.add_argument('--set', choices=('fpu', 'int', 'sse', 'branch'), default='fpu')
    ap.add_argument('--mutate', choices=sorted(MUTANTS), help='negative control: a deliberately wrong lowering')
    args = ap.parse_args()
    b = load_build()
    if args.set == 'branch':
        # jcc rel8 over 'mov eax,1; ret' to 'mov eax,2': every condition code 70..7f.
        form_list = {(f'jcc{op:02x}', ()): bytes([op, 0x06]) + bytes.fromhex('b801000000c3b802000000')
                     for op in range(0x70, 0x80)}
    else:
        form_list = forms(b, args.set)
    if args.mutate == 'emulated':
        b.native_kind = lambda i: None     # the previous double-based emulation, for comparison
    elif args.mutate and MUTANTS[args.mutate]:
        good = b.native_code
        before, after = MUTANTS[args.mutate]
        b.native_code = lambda i, address: good(i, address).replace(before, after)
    translate, header = b.backend()
    if args.mutate == 'no-parity':
        header = header.replace('return (~v&1u)<<2;', 'return 0u*(~v&1u);')
    if args.mutate == 'no-af':
        header = header.replace('&0x10u', '&0u').replace('& 0x10u', '& 0u')
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'machine257.h').write_text(header, encoding='utf-8')
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decls, frags, bodies, names, untranslated = [], [], [], [], []
    for (m, kinds), raw in sorted(form_list.items()):
        for mode in (0, 1):
            code = reencode(raw, mode) if args.set != 'branch' else (raw if mode == 0 else None)
            if code is None:
                continue
            decoded = list(md.disasm(code, 0))
            if args.set != 'branch' and (len(decoded) != 1 or decoded[0].size != len(code)):
                untranslated.append(f'{m} {kinds}: re-encoding not decodable')
                continue
            frag = code + b'\xc3'
            va = 0x10000000 + 0x100 * len(frags)
            try:
                low, _ = translate(frag, va)
            except ValueError as e:
                untranslated.append(f'{m} {kinds}: {e}')
                continue
            low = low.replace('#include "machine257.h"\n', '')
            text = decoded[0]
            name = f'{text.mnemonic} {text.op_str}'.replace('"', "'")
            bodies.append(low)
            decls.append(f'void translated_{va:08x}(Machine257&s);')
            arr = ', '.join(f'0x{x:02x}' for x in frag)
            frags.append(f'{{"{name}", (const unsigned char[]){{{arr}}}, {len(frag)}u, translated_{va:08x}}}')
            names.append(name)
    frag_arrays = []
    for k, f in enumerate(frags):
        arr = f.split('(const unsigned char[]){', 1)[1].split('}', 1)[0]
        frag_arrays.append(f'static const unsigned char code{k}[] = {{{arr}}};')
    table = 'static const Frag frags[] = {\n' + ',\n'.join(
        f.split('(const unsigned char[])', 1)[0] + f'code{k}, ' + f.split('}, ', 1)[1] for k, f in enumerate(frags)) + '\n};'
    src = HARNESS.replace('%INTSET%', '1' if args.set == 'int' else '0').replace('%DECLS%', '\n'.join(decls)).replace('%FRAGS%', '\n'.join(frag_arrays) + '\n' + table)
    (WORK / 'harness.cpp').write_text(src, encoding='utf-8')
    (WORK / 'fragments.cpp').write_text('#include "machine257.h"\n' + '\n'.join(bodies), encoding='utf-8')
    cl, link, env = b.toolchain()
    flags = ['/nologo', '/TP', '/std:c++17', '/O2', '/GS-', '/EHs-c-', '/W0', f'/I{WORK}']
    r = subprocess.run([str(cl), *flags, 'harness.cpp', 'fragments.cpp', '/Fe:oracle.exe', '/link', 'user32.lib'],
                       cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-4000:], r.stderr[-2000:])
        raise SystemExit('compile failed')
    run = subprocess.run([str(WORK / 'oracle.exe'), str(args.cases)], cwd=WORK, capture_output=True, text=True)
    (WORK / 'oracle.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    lines = run.stdout.splitlines()
    results = [dict(form=l.split('\t')[1], result=l.split('\t')[0], cases=l.split('\t')[2]) for l in lines if '\t' in l]
    summary = dict(schema=1, cpu=subprocess.run(['powershell', '-NoProfile', '-Command',
                                                 '(Get-CimInstance Win32_Processor | Select-Object -First 1).Name'],
                                                capture_output=True, text=True).stdout.strip(),
                   forms=len(results), failed=[r for r in results if r['result'] != 'PASS'],
                   cases_per_form=args.cases, exit_code=run.returncode, untranslated=untranslated, tail=lines[-1] if lines else '')
    if args.mutate:
        print(json.dumps(dict(mutant=args.mutate, failed_forms=len(summary['failed']))))
        return
    (RUN / {'fpu': 'native-fpu-oracle.json', 'int': 'integer-oracle.json', 'sse': 'sse-oracle.json',
           'branch': 'branch-oracle.json'}[args.set]).write_text(json.dumps(dict(summary, results=results), indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'failed'}, indent=1))
    for f in summary['failed'][:40]:
        print('FAIL', f)


if __name__ == '__main__':
    main()

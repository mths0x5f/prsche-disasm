"""Run 430: hardware oracle for humanized functions, built with Visual C++ 6.0.

The harness maps the original Porsche.exe at its own address (0x00400000, imports resolved;
reserve_430.cpp linked first holds the range) and, for every function in HUMANIZED
(build-v2-lowered-exe-430.py) without its own oracle, runs from the same random inputs:
- the original at its VA, called natively (arguments pushed, ECX = this for thiscall);
- the generated bridge `humanized_<va>_430` with the humanized C++ behind it, on a Machine257
  whose stack is a real array.
Compared: EAX (AX for 16-bit results, EDX too for 64-bit ones), a 16 KB argument buffer, the
global spans the spec names, the return address the bridge takes, the bytes the RET removes and,
for functions that call other game code, every call: each callee listed in `stubs` is replaced
by a recorder that logs its ECX (thiscall) and arguments and returns a pointer into the buffer
(the same sequence of values for both runs).
Argument kinds: dword, ptr (into the buffer), str, char, cursor (a slot holding a pointer into
the buffer), list (a linked list in the buffer), small (0..15), small8 (0..7), handle (0..127),
maybezero12 (12 bytes, each word 0 or random), table:ADDR:N (a value of that global table or
random). Global kinds: bytes (random), ptrs (pointers into the buffer), maybezero, count (0..128).
--mutate VA perturbs that function's result: the oracle must fail it.
--batch NAME checks only humanized/specs/NAME.json and writes NAME.oracle.json next to it.

Usage: py -3 scripts/research/verify-v2-humanized-430.py [--cases N] [--mutate VA] [--batch NAME]
"""
import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
WORK = ROOT / 'local/experiments/v2-humanized-430'
STREAM = Path(__file__).with_name('verify-v2-humanized-stream-430.py')

HARNESS = r'''#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "machine257.h"
extern "C" char reserve430[];
%DECLS%
static unsigned long rng = 0x2545F491;
static unsigned long rnd() { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }
static const char alphabet[] = "ab/\\.cd";
#define BUF 16384
static unsigned char *buf_n, buf_in[BUF], after_n[BUF];
static unsigned char gl_in[8192], gl_n[8192];
static unsigned long g_code_ret, g_args[4], g_self, g_code, g_eax, g_edx, g_saved, g_after, g_kept;
/* calls out run natively here, on the harness stack */
extern "C" void __cdecl humanized_on_guest430(void (__cdecl *body)(Machine257 *), Machine257 *s) { body(s); }

%MAP_IMAGE%

/* ---- callee recorders: a stubbed callee logs its arguments and returns a buffer pointer ---- */
#define MAX_STUBS 16
static unsigned char *tramp;
static unsigned long st_k, st_ecx, st_esp, st_popk, st_rv, st_seed;
static unsigned long st_at[MAX_STUBS], st_nargs[MAX_STUBS], st_conv[MAX_STUBS];   /* 0 cdecl 1 thiscall 2 stdcall */
static unsigned char st_saved[MAX_STUBS][5];
static unsigned long st_log[512];
static int st_logn, st_count;

static void stub_record(void)
{
    unsigned long k = st_k, i;
    if (st_logn < 500) {
        st_log[st_logn++] = st_at[k];
        if (st_conv[k] == 1) st_log[st_logn++] = st_ecx;
        for (i = 0; i < st_nargs[k] && st_logn < 510; ++i) st_log[st_logn++] = ((unsigned long *)st_esp)[1 + i];
    }
    st_popk = st_conv[k] ? 4 * st_nargs[k] : 0;
    st_seed = st_seed * 1103515245u + 12345u;
    st_rv = (unsigned long)buf_n + ((16 + (st_seed >> 8) % (BUF - 4096)) & ~3u);
}

static __declspec(naked) void stub_common(void)
{
    __asm {
        pop st_k
        mov st_ecx, ecx
        mov st_esp, esp
        pushad
        call stub_record
        popad
        pop g_code_ret
        add esp, st_popk
        mov eax, st_rv
        mov edx, st_rv
        jmp dword ptr g_code_ret
    }
}

static void stubs_install(int n)
{
    int k;
    unsigned long old;
    for (k = 0; k < n; ++k) {
        unsigned char *t = tramp + 16 * k, *at = (unsigned char *)st_at[k];
        t[0] = 0x68; *(unsigned long *)(t + 1) = (unsigned long)k;
        t[5] = 0xe9; *(long *)(t + 6) = (long)((unsigned char *)stub_common - (t + 10));
        VirtualProtect(at, 5, PAGE_EXECUTE_READWRITE, &old);
        memcpy(st_saved[k], at, 5);
        at[0] = 0xe9; *(long *)(at + 1) = (long)(t - (at + 5));
    }
    st_count = n;
    FlushInstructionCache(GetCurrentProcess(), NULL, 0);
}

static void stubs_remove(void)
{
    int k;
    for (k = 0; k < st_count; ++k) memcpy((void *)st_at[k], st_saved[k], 5);
    st_count = 0;
    FlushInstructionCache(GetCurrentProcess(), NULL, 0);
}

/* Native call of the original: four DWORDs pushed (a3..a0), ECX = this. */
static void call_native()
{
    __asm {
        push ebp
        push ebx
        push esi
        push edi
        mov ebx, 0x0b0b0b0b
        mov esi, 0x05050505
        mov edi, 0x0d0d0d0d
        mov ebp, 0x0e0e0e0e
        mov g_saved, esp
        push dword ptr g_args + 12
        push dword ptr g_args + 8
        push dword ptr g_args + 4
        push dword ptr g_args
        mov ecx, g_self
        call dword ptr g_code
        mov g_eax, eax
        mov g_edx, edx
        mov g_after, esp
        mov esp, g_saved
        xor ebx, 0x0b0b0b0b
        xor esi, 0x05050505
        xor edi, 0x0d0d0d0d
        xor ebp, 0x0e0e0e0e
        or ebx, esi
        or ebx, edi
        or ebx, ebp
        mov g_kept, ebx
        pop edi
        pop esi
        pop ebx
        pop ebp
    }
}

static unsigned long buf_ptr(void) { return (unsigned long)(buf_n + ((16 + rnd() % (BUF - 4096)) & ~3u)); }

static unsigned long make_arg(int kind, unsigned long table, int n)
{
    unsigned long off = 16 + rnd() % (BUF - 512), p, q;
    int k, len;
    switch (kind) {
    case 1: return (unsigned long)(buf_n + off);                       /* ptr */
    case 2:                                                              /* str */
        len = (int)(rnd() % 24);
        for (k = 0; k < len; ++k) buf_n[off + k] = alphabet[rnd() % 7];
        buf_n[off + len] = 0;
        return (unsigned long)(buf_n + off);
    case 3: return (rnd() % 8) ? (unsigned char)alphabet[rnd() % 7] : 0; /* char */
    case 4: p = buf_ptr(); *(unsigned long *)p = buf_ptr(); return p;   /* cursor */
    case 5:                                                              /* list */
        p = buf_ptr(); q = p; len = (int)(rnd() % 9);
        for (k = 0; k < len; ++k) { unsigned long node = (unsigned long)(buf_n + 64 * (k + 1 + 8 * (rnd() % 30)));
                                    *(unsigned long *)q = node; q = node; }
        *(unsigned long *)q = 0;
        return p;
    case 6: return rnd() % 16;
    case 7: return rnd() % 8;
    case 8: return (rnd() % 10) ? rnd() % 128 : rnd();
    case 9: p = buf_ptr(); for (k = 0; k < 3; ++k) ((unsigned long *)p)[k] = (rnd() % 2) ? 0 : rnd(); return p;
    case 10: return (rnd() % 3) ? ((unsigned long *)table)[rnd() % n] : rnd();
    case 11: return (rnd() % 2) ? 0 : rnd();                            /* maybezero dword */
    case 12: return (rnd() % 2) ? 0 : buf_ptr();                        /* null or ptr */
    case 14: return buf_ptr();                                          /* aligned pointer (soup) */
    case 13: p = buf_ptr(); for (k = 0; k < 64; ++k) ((unsigned long *)p)[k] = buf_ptr(); return p;  /* deep: pointers to pointers */
    default: return rnd();
    }
}

static void set_global(int kind, unsigned long at, int size)
{
    int k;
    for (k = 0; k < size; ++k) ((unsigned char *)at)[k] = (unsigned char)rnd();
    for (k = 0; k + 4 <= size; k += 4) {
        unsigned long *w = (unsigned long *)(at + k);
        if (kind == 1) *w = buf_ptr();
        else if (kind == 2 && rnd() % 2) *w = 0;
        else if (kind == 3) *w = rnd() % 129;
    }
}

int main(int argc, char **argv)
{
    int cases = argc > 1 ? atoi(argv[1]) : 10000, failed = 0, c, k;
    setvbuf(stdout, NULL, _IONBF, 0);   /* a crash must not lose the lines already printed */
    if (!map_image(argc > 2 ? argv[2] : "Porsche.exe")) { printf("cannot map the original at 0x00400000\n"); return 2; }
    buf_n = (unsigned char *)VirtualAlloc(NULL, BUF, MEM_COMMIT, PAGE_READWRITE);
    tramp = (unsigned char *)VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
%CASES%
    printf("functions %d failed %d\n", %COUNT%, failed);
    return failed != 0;
}
'''

CASE = r'''    {   /* %VA% */
        static const int kinds[4] = { %KINDS% };
        static const unsigned long g_at[] = { %GAT% 0 };
        static const int g_kind[] = { %GKIND% 0 }, g_size[] = { %GSIZE% 0 };
        static unsigned long log_n[512];
        int bad = 0, ng = %NG%, g, off, nlog_n;
        unsigned long seed;
        g_code = 0x%VA%u;
%STUBS%        stubs_install(%NSTUBS%);
        for (c = 0; c < cases; ++c) {
            Machine257 s;
            U stack[8];
            unsigned long eax_n, edx_n, pop_n;
            if (%SOUP%) for (k = 0; k < BUF / 4; ++k) ((unsigned long *)buf_n)[k] = buf_ptr();
            else for (k = 0; k < BUF; ++k) buf_n[k] = (unsigned char)rnd();
            for (g = 0; g < ng; ++g) set_global(g_kind[g], g_at[g], g_size[g]);
            for (k = 0; k < 4; ++k) g_args[k] = make_arg(kinds[k], %TABLE%, %TABLEN%);
            g_self = make_arg(%SELF%, 0, 0);
            seed = rnd();
            memcpy(buf_in, buf_n, BUF);
            for (g = 0, off = 0; g < ng; off += g_size[g++]) memcpy(gl_in + off, (void *)g_at[g], g_size[g]);
            st_seed = seed; st_logn = 0;
            call_native();
            memcpy(log_n, st_log, sizeof st_log); nlog_n = st_logn;
            eax_n = g_eax; edx_n = g_edx;
            pop_n = g_after - (g_saved - 16);
            memcpy(after_n, buf_n, BUF);
            memcpy(buf_n, buf_in, BUF);
            for (g = 0, off = 0; g < ng; off += g_size[g++]) {
                memcpy(gl_n + off, (void *)g_at[g], g_size[g]);
                memcpy((void *)g_at[g], gl_in + off, g_size[g]);
            }
            memset(&s, 0, sizeof s);
            s.stop = STOP257_RUNNING;
            stack[0] = 0xdeadbeefu;
            for (k = 0; k < 4; ++k) stack[1 + k] = g_args[k];
            s.r[4] = (U)stack;
            s.r[1] = g_self;
            st_seed = seed; st_logn = 0;
            humanized_%VA%_430(s);
            %MUT%
            {
                int gdiff = 0;
                for (g = 0, off = 0; g < ng; off += g_size[g++])
                    gdiff |= memcmp(gl_n + off, (void *)g_at[g], g_size[g]) != 0;
                if (%RETCMP% || nlog_n != st_logn || memcmp(log_n, st_log, 4 * nlog_n) ||
                    memcmp(after_n, buf_n, BUF) || gdiff || s.pc != 0xdeadbeefu ||
                    s.r[4] - (U)stack != 4 + pop_n || g_kept || s.stop != STOP257_RETURNED) {
                    if (!bad) printf("  %VA% case %d: eax %08lx/%08lx pop %lu/%lu globals %d calls %d/%d buffer %d\n",
                                     c, eax_n, (unsigned long)s.r[0], pop_n, (unsigned long)(s.r[4] - (U)stack - 4),
                                     gdiff, nlog_n, st_logn, memcmp(after_n, buf_n, BUF) != 0);
                    ++bad;
                }
            }
        }
        stubs_remove();
        printf("%s %VA% %d/%d\n", bad ? "FAIL" : "PASS", cases - bad, cases);
        if (bad) ++failed;
    }
'''

KIND = {'dword': 0, 'ptr': 1, 'str': 2, 'char': 3, 'cursor': 4, 'ptrptr': 4, 'list': 5, 'small': 6,
        'small8': 7, 'handle': 8, 'maybezero12': 9, 'table': 10, 'maybezero': 11, 'nullptr': 12, 'deep': 13, 'sptr': 14}
GKIND = {'bytes': 0, 'ptrs': 1, 'maybezero': 2, 'count': 3}
CONV = {'cdecl': 0, 'thiscall': 1, 'stdcall': 2}
RETCMP = {True: 's.r[0] != eax_n', False: '0', 'ax': '(s.r[0] & 0xffff) != (eax_n & 0xffff)',
          'al': '(s.r[0] & 0xff) != (eax_n & 0xff)',
          'edx:eax': '(s.r[0] != eax_n || s.r[2] != edx_n)'}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def map_image_source():
    """map_image() of the stream oracle: one copy of the loader."""
    text = load(STREAM, 'stream430').HARNESS
    start = text.index('static int map_image')
    return text[start:text.index('/* ---- the error handler')]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=int, default=20000)
    ap.add_argument('--mutate', help='VA whose result is perturbed (+1): the oracle must fail it')
    ap.add_argument('--batch', help='check only humanized/specs/BATCH.json')
    args = ap.parse_args()
    b = load(ROOT / 'scripts/research/build-v2-lowered-exe-430.py', 'build430')
    work = WORK / args.batch if args.batch else WORK
    if args.batch:
        spec_file = RUN / 'humanized' / 'specs' / f'{args.batch}.json'
        todo = json.loads(spec_file.read_text(encoding='utf-8-sig'))
    else:
        todo = b.HUMANIZED
    work.mkdir(parents=True, exist_ok=True)
    (work / 'humanized').mkdir(exist_ok=True)
    for hdr in (RUN / 'humanized').glob('*.h'):
        (work / 'humanized' / hdr.name).write_text(hdr.read_text(encoding='utf-8'), encoding='utf-8')
    decls, cases, units = [], [], []
    for va, h in sorted(todo.items()):
        if h.get('oracle'):
            continue   # proven by its own oracle (e.g. verify-v2-humanized-stream-430.py)
        if h.get('stubs'):
            h = dict(h, calls_out=True)
        kinds, table, tablen = [], '0', '0'
        for k in h['args']:
            if k.startswith('table:'):
                _, at, n = k.split(':')
                table, tablen = at, n
                k = 'table'
            kinds.append(KIND[k])
        kinds += [0] * (4 - len(kinds))
        gl = h.get('globals', [])
        stubs = h.get('stubs', {})
        unit = work / f'h_{va}.cpp'
        unit.write_text('#include "machine257.h"\n' + (RUN / h['source']).read_text(encoding='utf-8') + '\n' +
                        b.bridge_code(va, h), encoding='utf-8')
        units.append(unit.name)
        decls.append(f'void humanized_{va}_430(Machine257 &s);')
        sizes = [n * 4 if kind == 'ptrs' else n for kind, _, n in gl]
        stub_lines = ''.join(f'        st_at[{i}] = 0x{int(cv, 16):08x}u; st_nargs[{i}] = {n}; st_conv[{i}] = {CONV[conv]};\n'
                             for i, (cv, (n, conv)) in enumerate(sorted(stubs.items())))
        cases.append(CASE.replace('%VA%', va)
                     .replace('%KINDS%', ', '.join(map(str, kinds)))
                     .replace('%GAT%', ''.join(f'0x{at:08x}u, ' for _, at, _ in gl))
                     .replace('%GKIND%', ''.join(f'{GKIND[kind]}, ' for kind, _, _ in gl))
                     .replace('%GSIZE%', ''.join(f'{n}, ' for n in sizes))
                     .replace('%NG%', str(len(gl))).replace('%SOUP%', '1' if h.get('soup') else '0')
                     .replace('%STUBS%', stub_lines).replace('%NSTUBS%', str(len(stubs)))
                     .replace('%TABLE%', table + 'u').replace('%TABLEN%', tablen)
                     .replace('%SELF%', str(KIND[h.get('this', 'dword')]))
                     .replace('%RETCMP%', RETCMP[h['ret']])
                     .replace('%MUT%', 's.r[0] += 1;' if args.mutate == va else ''))
    src = HARNESS.replace('%MAP_IMAGE%', map_image_source()).replace('%DECLS%', '\n'.join(decls)) \
                 .replace('%CASES%', ''.join(cases)).replace('%COUNT%', str(len(cases)))
    (work / 'oracle.cpp').write_text(src, encoding='utf-8')
    (work / 'machine257.h').write_text((b.GEN / 'machine257.h').read_text(encoding='utf-8'), encoding='utf-8')
    env = b.vc6_env()
    r = subprocess.run([str(b.VC6_ROOT / 'Bin' / 'CL.EXE'), '/nologo', '/TP', '/MT', '/O2', '/W3', f'/I{work}',
                        str(RUN / 'reserve_430.cpp'), 'oracle.cpp', *units, '/Feoracle.exe', '/link',
                        '/BASE:0x400000', '/FIXED', 'kernel32.lib'],
                       cwd=work, capture_output=True, text=True, env=env)
    if r.returncode:
        print('\n'.join(l for l in r.stdout.splitlines() if 'error' in l)[-6000:])
        raise SystemExit('VC6 compile failed')
    game = ROOT / 'local/run-430'
    run = subprocess.run([str(work / 'oracle.exe'), str(args.cases), str(game / 'Porsche.exe')], cwd=game,
                         capture_output=True, text=True, timeout=3600)
    print(run.stdout.strip())
    if run.returncode not in (0, 1):
        print(f'oracle exited with {run.returncode:#x} (a crash)')
    if args.mutate:
        return
    receipt = dict(schema=3, compiler=f'Visual C++ 6.0 ({b.VC6_ROOT})', harness='original Porsche.exe mapped at 0x00400000',
                   cases_per_function=args.cases, functions=sorted(v for v, h in todo.items() if not h.get('oracle')),
                   output=run.stdout.splitlines(), exit_code=run.returncode)
    out = (RUN / 'humanized' / 'specs' / f'{args.batch}.oracle.json') if args.batch else (RUN / 'humanized-oracle.json')
    out.write_text(json.dumps(receipt, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

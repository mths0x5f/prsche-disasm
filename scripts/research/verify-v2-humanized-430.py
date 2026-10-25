"""Run 430: hardware oracle for humanized functions, built with Visual C++ 6.0.

The harness maps the original Porsche.exe at its own address (0x00400000, imports resolved;
reserve_430.cpp linked first holds the range) and, for every function in HUMANIZED
(build-v2-lowered-exe-430.py) without its own oracle, runs from the same random inputs:
- the original at its VA, called natively (arguments pushed, ECX = this for thiscall);
- the generated bridge `humanized_<va>_430` with the humanized C++ behind it, on a Machine257
  whose stack is a real array.
Compared: EAX (AX for 16-bit results, EDX too for 64-bit ones), a 16 KB argument buffer, the
global spans the spec names, the return address the bridge takes and the bytes the RET removes.
Argument kinds: dword, ptr (into the buffer), str, char, cursor (a slot holding a pointer into
the buffer), list (a linked list in the buffer), small (0..15), small8 (0..7), handle (0..127),
maybezero12 (12 bytes, each word 0 or random), table:ADDR:N (a value of that global table or
random). Global kinds: bytes (random), ptrs (pointers into the buffer), maybezero, count (0..128).
--mutate VA perturbs that function's result: the oracle must fail it.

Usage: py -3 scripts/research/verify-v2-humanized-430.py [--cases N] [--mutate VA]
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
static unsigned long g_args[4], g_self, g_code, g_eax, g_edx, g_saved, g_after;

%MAP_IMAGE%

/* Native call of the original: four DWORDs pushed (a3..a0), ECX = this. */
static void call_native()
{
    __asm {
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
    if (!map_image(argc > 2 ? argv[2] : "Porsche.exe")) { printf("cannot map the original at 0x00400000\n"); return 2; }
    buf_n = (unsigned char *)VirtualAlloc(NULL, BUF, MEM_COMMIT, PAGE_READWRITE);
%CASES%
    printf("functions %d failed %d\n", %COUNT%, failed);
    return failed != 0;
}
'''

CASE = r'''    {   /* %VA% */
        static const int kinds[4] = { %KINDS% };
        static const unsigned long g_at[] = { %GAT% 0 };
        static const int g_kind[] = { %GKIND% 0 }, g_size[] = { %GSIZE% 0 };
        int bad = 0, ng = %NG%, g, off;
        g_code = 0x%VA%u;
        for (c = 0; c < cases; ++c) {
            Machine257 s;
            U stack[8];
            unsigned long eax_n, edx_n, pop_n;
            for (k = 0; k < BUF; ++k) buf_n[k] = (unsigned char)rnd();
            for (g = 0; g < ng; ++g) set_global(g_kind[g], g_at[g], g_size[g]);
            for (k = 0; k < 4; ++k) g_args[k] = make_arg(kinds[k], %TABLE%, %TABLEN%);
            g_self = make_arg(%SELF%, 0, 0);
            memcpy(buf_in, buf_n, BUF);
            for (g = 0, off = 0; g < ng; off += g_size[g++]) memcpy(gl_in + off, (void *)g_at[g], g_size[g]);
            call_native();
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
            humanized_%VA%_430(s);
            %MUT%
            {
                int gdiff = 0;
                for (g = 0, off = 0; g < ng; off += g_size[g++])
                    gdiff |= memcmp(gl_n + off, (void *)g_at[g], g_size[g]) != 0;
                if (%RETCMP% || memcmp(after_n, buf_n, BUF) || gdiff || s.pc != 0xdeadbeefu ||
                    s.r[4] - (U)stack != 4 + pop_n || s.stop != STOP257_RETURNED) {
                    if (!bad) printf("  %VA% case %d: eax %08lx/%08lx pop %lu/%lu globals %d\n", c, eax_n,
                                     (unsigned long)s.r[0], pop_n, (unsigned long)(s.r[4] - (U)stack - 4), gdiff);
                    ++bad;
                }
            }
        }
        printf("%s %VA% %d/%d\n", bad ? "FAIL" : "PASS", cases - bad, cases);
        if (bad) ++failed;
    }
'''

KIND = {'dword': 0, 'ptr': 1, 'str': 2, 'char': 3, 'cursor': 4, 'ptrptr': 4, 'list': 5, 'small': 6,
        'small8': 7, 'handle': 8, 'maybezero12': 9, 'table': 10}
GKIND = {'bytes': 0, 'ptrs': 1, 'maybezero': 2, 'count': 3}
RETCMP = {True: 's.r[0] != eax_n', False: '0', 'ax': '(s.r[0] & 0xffff) != (eax_n & 0xffff)',
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
    args = ap.parse_args()
    b = load(ROOT / 'scripts/research/build-v2-lowered-exe-430.py', 'build430')
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'humanized').mkdir(exist_ok=True)
    for hdr in (RUN / 'humanized').glob('*.h'):
        (WORK / 'humanized' / hdr.name).write_text(hdr.read_text(encoding='utf-8'), encoding='utf-8')
    decls, cases, units = [], [], []
    for va, h in sorted(b.HUMANIZED.items()):
        if h.get('oracle'):
            continue   # proven by its own oracle (e.g. verify-v2-humanized-stream-430.py)
        kinds, table, tablen = [], '0', '0'
        for k in h['args']:
            if k.startswith('table:'):
                _, at, n = k.split(':')
                table, tablen = at, n
                k = 'table'
            kinds.append(KIND[k])
        kinds += [0] * (4 - len(kinds))
        gl = h.get('globals', [])
        unit = WORK / f'h_{va}.cpp'
        unit.write_text('#include "machine257.h"\n' + (RUN / h['source']).read_text(encoding='utf-8') + '\n' +
                        b.bridge_code(va, h), encoding='utf-8')
        units.append(unit.name)
        decls.append(f'void humanized_{va}_430(Machine257 &s);')
        sizes = [n * 4 if kind == 'ptrs' else n for kind, _, n in gl]
        cases.append(CASE.replace('%VA%', va)
                     .replace('%KINDS%', ', '.join(map(str, kinds)))
                     .replace('%GAT%', ''.join(f'0x{at:08x}u, ' for _, at, _ in gl))
                     .replace('%GKIND%', ''.join(f'{GKIND[kind]}, ' for kind, _, _ in gl))
                     .replace('%GSIZE%', ''.join(f'{n}, ' for n in sizes))
                     .replace('%NG%', str(len(gl)))
                     .replace('%TABLE%', table + 'u').replace('%TABLEN%', tablen)
                     .replace('%SELF%', str(KIND[h.get('this', 'dword')]))
                     .replace('%RETCMP%', RETCMP[h['ret']])
                     .replace('%MUT%', 's.r[0] += 1;' if args.mutate == va else ''))
    src = HARNESS.replace('%MAP_IMAGE%', map_image_source()).replace('%DECLS%', '\n'.join(decls)) \
                 .replace('%CASES%', ''.join(cases)).replace('%COUNT%', str(len(cases)))
    (WORK / 'oracle.cpp').write_text(src, encoding='utf-8')
    (WORK / 'machine257.h').write_text((b.GEN / 'machine257.h').read_text(encoding='utf-8'), encoding='utf-8')
    env = b.vc6_env()
    r = subprocess.run([str(b.VC6_ROOT / 'Bin' / 'CL.EXE'), '/nologo', '/TP', '/MT', '/O2', '/W3', f'/I{WORK}',
                        str(RUN / 'reserve_430.cpp'), 'oracle.cpp', *units, '/Feoracle.exe', '/link',
                        '/BASE:0x400000', '/FIXED', 'kernel32.lib'],
                       cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-4000:])
        raise SystemExit('VC6 compile failed')
    game = ROOT / 'local/run-430'
    run = subprocess.run([str(WORK / 'oracle.exe'), str(args.cases), str(game / 'Porsche.exe')], cwd=game,
                         capture_output=True, text=True, timeout=1800)
    print(run.stdout.strip())
    if not args.mutate:
        (RUN / 'humanized-oracle.json').write_text(json.dumps(dict(
            schema=3, compiler=f'Visual C++ 6.0 ({b.VC6_ROOT})', harness='original Porsche.exe mapped at 0x00400000',
            cases_per_function=args.cases,
            functions=sorted(v for v, h in b.HUMANIZED.items() if not h.get('oracle')), output=run.stdout.splitlines(),
            exit_code=run.returncode), indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

"""Run 430: hardware oracle for humanized functions, built with Visual C++ 6.0.

For every function in HUMANIZED (build-v2-lowered-exe-430.py) the oracle runs, from the same
random inputs:
- the original bytes from local/game/Porsche.exe, copied into executable memory and called
  natively (arguments pushed, ECX = this for thiscall);
- the generated bridge `humanized_<va>_430` with the humanized C++ behind it, on a Machine257
  whose stack is a real array.
It compares EAX (functions with a result), the 4 KB buffer the arguments point into, the
return address the bridge takes and how many bytes the RET removes (cdecl 4, thiscall 4+4n).
Argument kinds: 'ptr' (into the buffer), 'str' (a short string in the buffer, from a small
alphabet), 'char' (a character of that alphabet or 0), 'dword' (random).
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

HARNESS = r'''#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "machine257.h"
%DECLS%
static unsigned long rng = 0x2545F491;
static unsigned long rnd() { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }
static const char alphabet[] = "ab/\\.cd";
static unsigned char buf_in[4096], buf_n[4096];
static unsigned long g_args[4], g_self, g_code, g_eax, g_saved, g_after;

/* Native call of the original bytes: four DWORDs pushed (a3..a0), ECX = this. */
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
        mov g_after, esp
        mov esp, g_saved
    }
}

static unsigned long make_arg(int kind)
{
    unsigned long off = 16 + rnd() % (4096 - 512);
    int n, k;
    switch (kind) {
    case 1: return (unsigned long)(buf_n + off);                       /* ptr */
    case 2:                                                              /* str */
        n = (int)(rnd() % 24);
        for (k = 0; k < n; ++k) buf_n[off + k] = alphabet[rnd() % 7];
        buf_n[off + n] = 0;
        return (unsigned long)(buf_n + off);
    case 3: return (rnd() % 8) ? (unsigned char)alphabet[rnd() % 7] : 0; /* char */
    default: return rnd();                                               /* dword */
    }
}

int main(int argc, char **argv)
{
    int cases = argc > 1 ? atoi(argv[1]) : 10000, failed = 0, c, k;
    unsigned char *exec = (unsigned char *)VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    g_code = (unsigned long)exec;
%CASES%
    printf("functions %d failed %d\n", %COUNT%, failed);
    return failed != 0;
}
'''

CASE = r'''    {   /* %VA% */
        static const unsigned char code[] = { %BYTES% };
        static const int kinds[4] = { %KINDS% };
        int bad = 0;
        memcpy(exec, code, sizeof code);
        FlushInstructionCache(GetCurrentProcess(), exec, sizeof code);
        for (c = 0; c < cases; ++c) {
            Machine257 s;
            U stack[8];
            unsigned long eax_n, pop_n;
            for (k = 0; k < 4096; ++k) buf_n[k] = (unsigned char)rnd();
            for (k = 0; k < 4; ++k) g_args[k] = make_arg(kinds[k]);
            g_self = make_arg(%SELF%);
            memcpy(buf_in, buf_n, 4096);
            call_native();
            eax_n = g_eax;
            pop_n = g_after - (g_saved - 16);
            memcpy(stack + 4, buf_n, 0);              /* keep the native result buffer aside */
            {
                static unsigned char after_n[4096];
                memcpy(after_n, buf_n, 4096);
                memcpy(buf_n, buf_in, 4096);
                memset(&s, 0, sizeof s);
                s.stop = STOP257_RUNNING;
                stack[0] = 0xdeadbeefu;
                for (k = 0; k < 4; ++k) stack[1 + k] = g_args[k];
                s.r[4] = (U)stack;
                s.r[1] = g_self;
                humanized_%VA%_430(s);
                %MUT%
                if ((%RET% && s.r[0] != eax_n) || memcmp(after_n, buf_n, 4096) || s.pc != 0xdeadbeefu ||
                    s.r[4] - (U)stack != 4 + pop_n || s.stop != STOP257_RETURNED) {
                    if (!bad) printf("  %VA% case %d: eax %08lx/%08lx pop %lu/%lu\n", c, eax_n,
                                     (unsigned long)s.r[0], pop_n, (unsigned long)(s.r[4] - (U)stack - 4));
                    ++bad;
                }
            }
        }
        printf("%s %VA% %d/%d\n", bad ? "FAIL" : "PASS", cases - bad, cases);
        if (bad) ++failed;
    }
'''

KIND = {'dword': 0, 'ptr': 1, 'str': 2, 'char': 3}


def load_build():
    spec = importlib.util.spec_from_file_location('build430', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=int, default=20000)
    ap.add_argument('--mutate', help='VA whose result is perturbed (+1): the oracle must fail it')
    args = ap.parse_args()
    b = load_build()
    img = b.Image(b.PE_PATH.read_bytes())
    catalog = {json.loads(l)['entry_va']: json.loads(l) for l in b.CATALOG.read_text(encoding='utf-8').splitlines()}
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'humanized').mkdir(exist_ok=True)
    for hdr in (RUN / 'humanized').glob('*.h'):
        (WORK / 'humanized' / hdr.name).write_text(hdr.read_text(encoding='utf-8'), encoding='utf-8')
    decls, cases = [], []
    units = []
    for va, h in sorted(b.HUMANIZED.items()):
        lo, hi = (int(x, 16) for x in catalog[va]['ranges'][0])
        code = img.read(lo, hi - lo + 1)
        kinds = [KIND[k] for k in h['args']] + [0] * (4 - len(h['args']))
        unit = WORK / f'h_{va}.cpp'
        unit.write_text('#include "machine257.h"\n' + (RUN / h['source']).read_text(encoding='utf-8') + '\n' +
                        b.bridge_code(va, h), encoding='utf-8')
        units.append(unit.name)
        decls.append(f'void humanized_{va}_430(Machine257 &s);')
        cases.append(CASE.replace('%VA%', va).replace('%BYTES%', ', '.join(f'0x{x:02x}' for x in code))
                     .replace('%KINDS%', ', '.join(map(str, kinds)))
                     .replace('%SELF%', str(KIND[h.get('this', 'dword')]))
                     .replace('%RET%', '1' if h['ret'] else '0')
                     .replace('%MUT%', 's.r[0] += 1;' if args.mutate == va else ''))
    src = HARNESS.replace('%DECLS%', '\n'.join(decls)).replace('%CASES%', ''.join(cases)) \
                 .replace('%COUNT%', str(len(cases)))
    (WORK / 'oracle.cpp').write_text(src, encoding='utf-8')
    (WORK / 'machine257.h').write_text((b.GEN / 'machine257.h').read_text(encoding='utf-8'), encoding='utf-8')
    env = b.vc6_env()
    r = subprocess.run([str(b.VC6_ROOT / 'Bin' / 'CL.EXE'), '/nologo', '/TP', '/MT', '/O2', '/W3', f'/I{WORK}',
                        'oracle.cpp', *units, '/Feoracle.exe', '/link', 'kernel32.lib'],
                       cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-4000:])
        raise SystemExit('VC6 compile failed')
    run = subprocess.run([str(WORK / 'oracle.exe'), str(args.cases)], cwd=WORK, capture_output=True, text=True)
    print(run.stdout.strip())
    if not args.mutate:
        (RUN / 'humanized-oracle.json').write_text(json.dumps(dict(
            schema=2, compiler=f'Visual C++ 6.0 ({b.VC6_ROOT})', cases_per_function=args.cases,
            functions=sorted(b.HUMANIZED), output=run.stdout.splitlines(), exit_code=run.returncode),
            indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

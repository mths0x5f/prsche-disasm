"""Run 430: hardware oracle for humanized functions (Visual C++ 6.0 build).

For every humanized function listed in HUMANIZED (build-v2-lowered-exe-430.py), the original
bytes from local/game/Porsche.exe are copied into executable memory and called natively next to
the humanized C++ compiled by VC6, from the same random inputs. Arguments are described per
function: 'dword' (random), 'ptr' (pointer 16..240 bytes into a random 256-byte buffer).
Return value (EAX) and the buffer are compared. --mutate checks that a wrong body fails.

Usage: py -3 scripts/research/verify-v2-humanized-430.py [--cases N] [--mutate VA]
Output: local/experiments/v2-humanized-430/ and runs/430-lowered-whole-game/humanized-oracle.json
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
static unsigned char buf_n[256], buf_h[256], buf_in[256];
typedef unsigned long (__cdecl *Fn4)(unsigned long, unsigned long, unsigned long, unsigned long);
int main(int argc, char **argv)
{
    int cases = argc > 1 ? atoi(argv[1]) : 10000, failed = 0, f, c, k;
    unsigned char *exec = (unsigned char *)VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
%CASES%
    printf("functions %d failed %d\n", (int)(sizeof(names) / sizeof(names[0])), failed);
    return failed != 0;
}
'''

CASE = r'''    /* %VA% */
    {
        static const unsigned char code[] = { %BYTES% };
        int bad = 0;
        memcpy(exec, code, sizeof code);
        FlushInstructionCache(GetCurrentProcess(), exec, sizeof code);
        for (c = 0; c < cases; ++c) {
            unsigned long a[4], n, h;
            for (k = 0; k < 256; ++k) buf_in[k] = (unsigned char)rnd();
            for (k = 0; k < 4; ++k) a[k] = rnd();
%ARGS%
            memcpy(buf_n, buf_in, 256);
            n = ((Fn4)exec)(%NARGS%);
            memcpy(buf_h, buf_n, 256);
            memcpy(buf_n, buf_in, 256);
            h = (unsigned long)%NAME%(%HARGS%)%MUT%;
            if (n != h || memcmp(buf_h, buf_n, 256)) {
                if (!bad) printf("  %VA% case %d: original %08lx humanized %08lx\n", c, n, h);
                ++bad;
            }
        }
        printf("%s %VA% %NAME% %d/%d\n", bad ? "FAIL" : "PASS", cases - bad, cases);
        if (bad) ++failed;
    }
'''


def load_build():
    spec = importlib.util.spec_from_file_location('build430', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=int, default=20000)
    ap.add_argument('--mutate', help='VA whose humanized result is perturbed (+1): must fail')
    args = ap.parse_args()
    b = load_build()
    data = b.PE_PATH.read_bytes()
    img = b.Image(data)
    catalog = {json.loads(l)['entry_va']: json.loads(l) for l in b.CATALOG.read_text(encoding='utf-8').splitlines()}
    WORK.mkdir(parents=True, exist_ok=True)
    decls, cases, sources, names = [], [], [], []
    for va, h in sorted(b.HUMANIZED.items()):
        lo, hi = (int(x, 16) for x in catalog[va]['ranges'][0])
        code = img.read(lo, hi - lo + 1)
        src = RUN / h['source']
        sources.append(src)
        sig = ', '.join(('const void *' if k == 'ptr' else 'unsigned long') for k in h['args'])
        decls.append(f'{h["return"]} __cdecl {h["name"]}({sig});')
        setup, nargs, hargs = [], [], []
        for i, kind in enumerate(h['args']):
            if kind == 'ptr':
                setup.append(f'            a[{i}] = (unsigned long)(buf_n + 16 + (rnd() % 225));')
                hargs.append(f'(const void *)a[{i}]')
            else:
                hargs.append(f'a[{i}]')
            nargs.append(f'a[{i}]')
        nargs += ['0'] * (4 - len(nargs))
        cases.append(CASE.replace('%VA%', va).replace('%BYTES%', ', '.join(f'0x{x:02x}' for x in code))
                     .replace('%ARGS%', '\n'.join(setup)).replace('%NARGS%', ', '.join(nargs))
                     .replace('%NAME%', h['name']).replace('%HARGS%', ', '.join(hargs))
                     .replace('%MUT%', ' + 1' if args.mutate == va else ''))
        names.append(f'"{va}"')
    src = HARNESS.replace('%DECLS%', '\n'.join(decls) + '\nstatic const char *names[] = { ' + ', '.join(names) + ' };') \
                 .replace('%CASES%', ''.join(cases))
    (WORK / 'oracle.cpp').write_text(src, encoding='utf-8')
    (WORK / 'machine257.h').write_text((b.GEN / 'machine257.h').read_text(encoding='utf-8'), encoding='utf-8')
    unit = WORK / 'humanized.cpp'
    unit.write_text('#include "machine257.h"\n' + '\n'.join(s.read_text(encoding='utf-8') for s in sources),
                    encoding='utf-8')
    env = b.vc6_env()
    cl = str(b.VC6_ROOT / 'Bin' / 'CL.EXE')
    r = subprocess.run([cl, '/nologo', '/TP', '/O2', '/W3', f'/I{WORK}', 'oracle.cpp', 'humanized.cpp',
                        '/Feoracle.exe', '/link', 'kernel32.lib'], cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit('VC6 compile failed')
    run = subprocess.run([str(WORK / 'oracle.exe'), str(args.cases)], cwd=WORK, capture_output=True, text=True)
    print(run.stdout.strip())
    if not args.mutate:
        (RUN / 'humanized-oracle.json').write_text(json.dumps(dict(
            schema=1, compiler='Visual C++ 6.0 (' + str(b.VC6_ROOT) + ')', cases=args.cases,
            output=run.stdout.splitlines(), exit_code=run.returncode), indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

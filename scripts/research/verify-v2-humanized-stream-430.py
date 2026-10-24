"""Run 430: hardware oracle for the humanized stream.c functions (Visual C++ 6.0).

These functions call other game code (the stream lock, the real library's error handler), so
the harness maps the original Porsche.exe at its own address (0x00400000, executable, imports
resolved) and runs, from the same random scenario:
- the original bytes natively (0056be40 classifier, 0056c540 STREAM_get, 0056c000, 0056b380);
- the humanized VC6 code, whose calls go to the same original functions.
A scenario is a stream with filters, taps, a request and a ring buffer of chunks, built in one
arena that is restored between the two runs. Compared: the result, the whole arena, the error
globals [005deb74]/[005deb78] and every call of the error handler (format, first arguments).
--mutate applies a deliberate bug to the humanized source; the oracle must fail it.

Usage: py -3 scripts/research/verify-v2-humanized-stream-430.py [--cases N] [--mutate NAME]
"""
import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
WORK = ROOT / 'local/experiments/v2-humanized-stream-430'
SOURCES = ['0056b380.cpp', '0056c000.cpp', '0056be40.cpp', '0056c540.cpp']
MUTANTS = {
    'greedy': ('0056be40.cpp', 'received + size >= stream->greedy_level', 'received + size > stream->greedy_level'),
    'head': ('0056be40.cpp', 'if (bytes == size)', 'if (bytes >= size)'),
    'remaining': ('0056c540.cpp', 'if (remaining > 0) {', 'if (remaining >= 0) {'),
    'filter': ('0056c000.cpp', 'return STREAM_ABORT_TAP;', 'return -1;'),
}

HARNESS = r'''#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "humanized/stream.h"
extern "C" char reserve430[];

static unsigned long rng = 0x1234567;
static unsigned long rnd() { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }

/* ---- the original image at 0x00400000 ---- */
static int map_image(const char *path)
{
    HANDLE f = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    DWORD size, got;
    BYTE *file, *img;
    IMAGE_NT_HEADERS *nt;
    IMAGE_SECTION_HEADER *sec;
    IMAGE_IMPORT_DESCRIPTOR *d;
    unsigned i;
    if (f == INVALID_HANDLE_VALUE) return 0;
    size = GetFileSize(f, NULL);
    file = (BYTE *)VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_READWRITE);
    ReadFile(f, file, size, &got, NULL);
    CloseHandle(f);
    nt = (IMAGE_NT_HEADERS *)(file + ((IMAGE_DOS_HEADER *)file)->e_lfanew);
    /* reserve_430.obj, linked first, holds 0x00401000..0x006e3000 of this EXE (based at 0x00400000). */
    img = (BYTE *)0x00400000;
    if ((unsigned long)reserve430 != 0x00401000u) return 0;
    VirtualProtect(img + 0x1000, nt->OptionalHeader.SizeOfImage - 0x1000, PAGE_EXECUTE_READWRITE, &got);
    sec = IMAGE_FIRST_SECTION(nt);
    for (i = 0; i < nt->FileHeader.NumberOfSections; ++i)
        memcpy(img + sec[i].VirtualAddress, file + sec[i].PointerToRawData,
               sec[i].SizeOfRawData < sec[i].Misc.VirtualSize ? sec[i].SizeOfRawData : sec[i].Misc.VirtualSize);
    d = (IMAGE_IMPORT_DESCRIPTOR *)(img + nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
    for (; d->Name; ++d) {
        HMODULE h = LoadLibraryA((const char *)(img + d->Name));
        unsigned long *names = (unsigned long *)(img + (d->OriginalFirstThunk ? d->OriginalFirstThunk : d->FirstThunk));
        unsigned long *iat = (unsigned long *)(img + d->FirstThunk);
        for (; *names; ++names, ++iat)
            *iat = h ? (unsigned long)GetProcAddress(h, (*names & 0x80000000u) ? (const char *)(*names & 0xffff)
                                                                                : (const char *)(img + *names + 2)) : 0;
    }
    return 1;
}

/* ---- the error handler: every call is recorded ---- */
static unsigned long g_log[64];   /* fmt, then its arguments */
static int g_log_n, g_dbg_logn;
static void __cdecl error_handler(const char *fmt, ...)
{
    unsigned long *a = (unsigned long *)&fmt;
    int k;
    if (g_log_n < 54) {
        g_log[g_log_n++] = (unsigned long)fmt;
        if (fmt == STREAM_MSG_BAD_CHUNK)           /* the only format with arguments: 8 bytes */
            for (k = 1; k <= 8; ++k) g_log[g_log_n++] = a[k];
    }
}

/* ---- scenario arena ---- */
#define ARENA_SIZE 0x6000
static unsigned char *arena, snapshot[ARENA_SIZE], after_n[ARENA_SIZE];
static CRITICAL_SECTION lock;
#define S        ((Stream *)(arena + 0x000))
#define REQ      ((StreamRequest *)(arena + 0x200))
#define FILTERS  ((StreamFilter *)(arena + 0x400))
#define TAPS     ((StreamTap *)(arena + 0x500))
#define BUF      ((char *)(arena + 0x1000))
#define BUF_SIZE 0x4000
static unsigned long ids[64];
static int n_ids;

static void fill_random(void) { int k; for (k = 0; k < ARENA_SIZE; ++k) arena[k] = (unsigned char)rnd(); }

static void base_stream(void)
{
    int k;
    S->magic = STREAM_MAGIC;
    S->lock = &lock;
    S->filters = FILTERS;
    S->filter_count = (long)(rnd() % 6);
    S->taps = TAPS;
    S->buffer = BUF;
    S->request = REQ;
    S->greedy_level = (long)(rnd() % 0x400);
    S->received = (long)(rnd() % 0x400);
    S->greedy_wait = (long)(rnd() % 3);
    REQ->state = (long)(rnd() % 6);
    for (k = 0; k < 4; ++k) {
        TAPS[k].stream = S;
        TAPS[k].id = (unsigned long)(k + 1);
        TAPS[k].bytes = (rnd() % 3) ? 0 : (long)(rnd() % 0x200);
        TAPS[k].head = (StreamChunk *)(BUF + 4 * (rnd() % 64));
    }
}

/* Chunks from the start of the buffer; returns the byte length. marks: 0 none, else tap. */
static long build_chunks(int count, int marked, int with_wrap)
{
    long at = 0;
    int k;
    n_ids = 0;
    for (k = 0; k < count && at < BUF_SIZE - 0x200; ++k) {
        StreamChunk *c = (StreamChunk *)(BUF + at);
        unsigned long size = 8 + 4 * (rnd() % 40);
        unsigned long id = (rnd() % 2) ? (0x4d410000u | (rnd() % 4)) : rnd();
        c->id = id;
        c->size_tap = size;
        if (marked) c->size_tap |= (unsigned long)(1 + rnd() % 4) << 24;
        ids[n_ids++] = id;
        at += (long)size;
    }
    if (with_wrap) {
        StreamChunk *w = (StreamChunk *)(BUF + at);
        w->id = STREAM_CHUNK_WRAP;
        w->size_tap = 8;
    }
    return at;
}

static void scenario_classify(void)
{
    long len;
    int k;
    fill_random();
    base_stream();
    len = build_chunks(1 + (int)(rnd() % 12), 0, 0);
    if (rnd() % 30 == 0) ((StreamChunk *)(BUF + 8 * (rnd() % 4)))->size_tap |= 0x01000000u;  /* bad chunk */
    for (k = 0; k < S->filter_count; ++k) {
        static const unsigned long masks[4] = { 0xffffffffu, 0xffff0000u, 0x0000ffffu, 0xffffff00u };
        static const long taps[6] = { 1, 2, 3, 4, -1, -2 };
        FILTERS[k].mask = masks[rnd() % 4];
        FILTERS[k].value = FILTERS[k].mask & ids[rnd() % n_ids];
        FILTERS[k].tap = taps[rnd() % 6];
    }
    REQ->last_id = (rnd() % 3) ? ids[rnd() % n_ids] : rnd();
    S->parse = BUF;
    S->fill = BUF + len - (long)((rnd() % 3) ? 0 : rnd() % 24);
}

static int scenario_get(void)
{
    long len;
    int t, k, marked[64], n_marked = 0;
    StreamChunk *chunks[64];
    long at = 0;
    fill_random();
    base_stream();
    len = build_chunks(4 + (int)(rnd() % 12), 1, 1);
    t = (int)(rnd() % 4);
    /* the chunks, and two of them carrying the tap's mark (STREAM_get looks for the next one) */
    for (k = 0; k < n_ids; ++k) {
        chunks[k] = (StreamChunk *)(BUF + at);
        at += (long)(chunks[k]->size_tap & 0xffffff);
    }
    marked[n_marked++] = (int)(rnd() % n_ids);
    marked[n_marked++] = (marked[0] + 1 + (int)(rnd() % (n_ids - 1))) % n_ids;   /* a different chunk */
    for (k = 0; k < n_marked; ++k)
        chunks[marked[k]]->size_tap = (chunks[marked[k]]->size_tap & 0xffffff) | ((unsigned long)(t + 1) << 24);
    TAPS[t].head = chunks[marked[0]];
    switch (rnd() % 4) {
    case 0: TAPS[t].bytes = 0; break;
    case 1: TAPS[t].bytes = (long)(chunks[marked[0]]->size_tap & 0xffffff); break;
    default: TAPS[t].bytes = (long)(chunks[marked[0]]->size_tap & 0xffffff) + (long)(rnd() % 0x300); break;
    }
    if (rnd() % 15 == 0) S->magic = 0x12345678;
    (void)len;
    return t;
}

typedef long (__cdecl *ClassifyFn)(Stream *);
typedef StreamChunk *(__cdecl *GetFn)(StreamTap *);

static int run_case(int which, unsigned long *res_n, unsigned long *res_h, int *diff)
{
    unsigned long g74, g78, log_n[64], s74, s78;
    int n_log, t = 0;
    StreamTap *handle;
    if (which == 0) scenario_classify(); else t = scenario_get();
    handle = (which == 1 && rnd() % 20 == 0) ? NULL : &TAPS[which == 1 ? t : 0];
    memcpy(snapshot, arena, ARENA_SIZE);
    s74 = *(unsigned long *)0x005deb74; s78 = *(unsigned long *)0x005deb78;
    g_log_n = 0;
    *res_n = which == 0 ? (unsigned long)((ClassifyFn)0x0056be40)(S) : (unsigned long)((GetFn)0x0056c540)(handle);
    memcpy(after_n, arena, ARENA_SIZE);
    memcpy(log_n, g_log, sizeof g_log); n_log = g_log_n;
    g74 = *(unsigned long *)0x005deb74; g78 = *(unsigned long *)0x005deb78;
    memcpy(arena, snapshot, ARENA_SIZE);
    *(unsigned long *)0x005deb74 = s74; *(unsigned long *)0x005deb78 = s78;
    g_log_n = 0;
    *res_h = which == 0 ? (unsigned long)stream_classify_0056be40(S) : (unsigned long)STREAM_get(handle);
    g_dbg_logn = n_log;
    *diff = memcmp(after_n, arena, ARENA_SIZE) != 0 || n_log != g_log_n || memcmp(log_n, g_log, n_log * 4) != 0 ||
            g74 != *(unsigned long *)0x005deb74 || g78 != *(unsigned long *)0x005deb78;
    return *res_n == *res_h && !*diff;
}

int main(int argc, char **argv)
{
    int cases = argc > 1 ? atoi(argv[1]) : 10000, which, c, failed = 0;
    if (!map_image(argc > 2 ? argv[2] : "Porsche.exe")) { printf("cannot map the original at 0x00400000\n"); return 2; }
    *(unsigned long *)0x005debf0 = (unsigned long)&error_handler;
    InitializeCriticalSection(&lock);
    arena = (unsigned char *)VirtualAlloc(NULL, ARENA_SIZE, MEM_COMMIT, PAGE_READWRITE);
    for (which = 0; which < 2; ++which) {
        int bad = 0;
        for (c = 0; c < cases; ++c) {
            unsigned long rn, rh;
            int diff;
            if (!run_case(which, &rn, &rh, &diff)) {
                if (bad < 3) {
                    int o;
                    for (o = 0; o < ARENA_SIZE && after_n[o] == arena[o]; ++o) ;
                    printf("  %s case %d: original %08lx humanized %08lx; first arena diff at +%04x: %08lx / %08lx; log %d/%d\n",
                           which ? "0056c540" : "0056be40", c, rn, rh, o,
                           o < ARENA_SIZE ? *(unsigned long *)(after_n + (o & ~3)) : 0ul,
                           o < ARENA_SIZE ? *(unsigned long *)(arena + (o & ~3)) : 0ul, g_dbg_logn, g_log_n);
                }
                ++bad;
            }
        }
        printf("%s %s %d/%d\n", bad ? "FAIL" : "PASS", which ? "0056c540 STREAM_get (+0056b380)" : "0056be40 classify (+0056c000)",
               cases - bad, cases);
        if (bad) ++failed;
    }
    printf("functions 2 failed %d\n", failed);
    return failed != 0;
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cases', type=int, default=20000)
    ap.add_argument('--mutate', choices=sorted(MUTANTS))
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('build430', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'humanized').mkdir(exist_ok=True)
    (WORK / 'humanized' / 'stream.h').write_text((RUN / 'humanized' / 'stream.h').read_text(encoding='utf-8'),
                                                 encoding='utf-8')
    units = []
    for name in SOURCES:
        text = (RUN / 'humanized' / name).read_text(encoding='utf-8')
        if args.mutate and MUTANTS[args.mutate][0] == name:
            assert MUTANTS[args.mutate][1] in text
            text = text.replace(MUTANTS[args.mutate][1], MUTANTS[args.mutate][2])
        (WORK / name).write_text(text, encoding='utf-8')
        units.append(name)
    (WORK / 'oracle.cpp').write_text(HARNESS, encoding='utf-8')
    env = b.vc6_env()
    r = subprocess.run([str(b.VC6_ROOT / 'Bin' / 'CL.EXE'), '/nologo', '/TP', '/MT', '/O2', '/W3', f'/I{WORK}',
                        str(RUN / 'reserve_430.cpp'), 'oracle.cpp', *units, '/Feoracle.exe', '/link', '/BASE:0x400000',
                        '/FIXED', 'kernel32.lib'],
                       cwd=WORK, capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout[-4000:])
        raise SystemExit('VC6 compile failed')
    game = ROOT / 'local/run-430'
    run = subprocess.run([str(WORK / 'oracle.exe'), str(args.cases), str(game / 'Porsche.exe')], cwd=game,
                         capture_output=True, text=True, timeout=1800)
    print(run.stdout.strip())
    if not args.mutate:
        (RUN / 'humanized-stream-oracle.json').write_text(json.dumps(dict(
            schema=1, compiler=f'Visual C++ 6.0 ({b.VC6_ROOT})', cases_per_function=args.cases,
            output=run.stdout.splitlines(), exit_code=run.returncode), indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

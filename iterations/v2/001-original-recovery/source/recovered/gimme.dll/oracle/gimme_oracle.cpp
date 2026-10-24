// Differential oracle: the original gimme.dll and the recovered sources in one process.
//
//   gimme_oracle convert <original.dll> <source> <frame> <outdir> [--pad | --guard]
//       Runs the original ConvertFile and the recovered one on the same input and compares
//       the output files byte for byte.  --pad gives both CRT heaps zero padding after every
//       block, so reads past a block are deterministic; --guard faults on them instead.
//
// The original DLL must load at its preferred base 0x10000000 (the oracle links at 0x400000).

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "heaphook.h"

extern "C" char __cdecl ConvertFile(const char *source, const char *destination, int frame);
typedef char(__cdecl *ConvertFileFn)(const char *, const char *, int);

static HMODULE LoadOriginal(const char *path)
{
    HMODULE original = LoadLibraryA(path);
    if (original != (HMODULE)0x10000000)
    {
        fprintf(stderr, "original %s not loaded at 0x10000000 (%p, error %lu)\n", path, (void *)original,
                GetLastError());
        exit(2);
    }
    return original;
}

static void ApplyHeapMode(HMODULE original, int argc, char **argv, int first)
{
    for (int i = first; i < argc; ++i)
    {
        if (strcmp(argv[i], "--pad") == 0 || strcmp(argv[i], "--guard") == 0)
        {
            SIZE_T pad = strcmp(argv[i], "--pad") == 0 ? 0x1000 : 0;
            heaphook::HookHeap(original, pad);
            heaphook::HookHeap(GetModuleHandleA(NULL), pad);
        }
    }
}

static unsigned char *ReadAll(const char *name, long *size)
{
    FILE *file = fopen(name, "rb");
    *size = -1;
    if (!file)
        return NULL;
    fseek(file, 0, SEEK_END);
    *size = ftell(file);
    fseek(file, 0, SEEK_SET);
    unsigned char *data = (unsigned char *)malloc(*size + 1);
    fread(data, 1, *size, file);
    fclose(file);
    return data;
}

static int CompareFiles(const char *expected, const char *actual)
{
    long expectedsize, actualsize;
    unsigned char *a = ReadAll(expected, &expectedsize);
    unsigned char *b = ReadAll(actual, &actualsize);
    if (!a || !b)
    {
        printf("MISSING %s=%ld %s=%ld\n", expected, expectedsize, actual, actualsize);
        return 1;
    }
    long common = expectedsize < actualsize ? expectedsize : actualsize;
    for (long i = 0; i < common; ++i)
        if (a[i] != b[i])
        {
            printf("DIFF at %#lx: original %02x recovered %02x (sizes %ld/%ld)\n", i, a[i], b[i], expectedsize,
                   actualsize);
            return 1;
        }
    if (expectedsize != actualsize)
    {
        printf("DIFF sizes %ld/%ld\n", expectedsize, actualsize);
        return 1;
    }
    printf("MATCH %ld bytes\n", expectedsize);
    return 0;
}

static int Convert(int argc, char **argv)
{
    if (argc < 6)
        return 2;
    HMODULE original = LoadOriginal(argv[2]);
    ApplyHeapMode(original, argc, argv, 6);
    ConvertFileFn originalconvert = (ConvertFileFn)GetProcAddress(original, "ConvertFile");
    int frame = atoi(argv[4]);
    char expected[MAX_PATH], actual[MAX_PATH];
    sprintf(expected, "%s\\original_%d.fsh", argv[5], frame);
    sprintf(actual, "%s\\recovered_%d.fsh", argv[5], frame);
    DeleteFileA(expected);
    DeleteFileA(actual);
    char destination[0x80];
    memset(destination, 0, sizeof(destination));
    strncpy(destination, expected, sizeof(destination) - 1);
    int originalresult = (unsigned char)originalconvert(argv[3], destination, frame);
    memset(destination, 0, sizeof(destination));
    strncpy(destination, actual, sizeof(destination) - 1);
    int recoveredresult = (unsigned char)ConvertFile(argv[3], destination, frame);
    fflush(stdout);
    printf("results original %d recovered %d\n", originalresult, recoveredresult);
    return CompareFiles(expected, actual) | (originalresult != recoveredresult);
}

// ---------------------------------------------------------------------------------------------
// Module-level comparison.  The original's own callbacks and module table are called at their
// VAs, the recovered ones by symbol; each side only ever sees its own handles.

#include "../_sem_arquivo/gimex/gimex.h"

struct Side
{
    const char *label;
    GMODULE *modules;
    GSTREAM *(GCALL *open)(const char *);
    GSTREAM *(GCALL *wopen)(const char *);
    int(GCALL *close)(GSTREAM *);
    void *(GCALL *alloc)(int);
    int(GCALL *free)(void *);
};

static Side OriginalSide()
{
    Side side = { "original", (GMODULE *)0x10431a50, (GSTREAM * (GCALL *)(const char *))0x10003650,
                  (GSTREAM * (GCALL *)(const char *))0x10003840, (int(GCALL *)(GSTREAM *))0x10003d20,
                  (void *(GCALL *)(int))0x10003170, (int(GCALL *)(void *))0x100032a0 };
    return side;
}

static Side RecoveredSide()
{
    Side side = { "recovered", gimexmodules, gopen, gwopen, gclose, galloc, gfree };
    return side;
}

// Finds the recovered module with the same tag and name as original module `index`.
static int MatchRecovered(int index)
{
    GABOUT *wanted = ((GMODULE *)0x10431a50)[index].about();
    int found = -1;
    for (int i = 0; gimexmodules[i].about && found < 0; ++i)
    {
        GABOUT *about = gimexmodules[i].about();
        if (about && about->tag == wanted->tag && strcmp(about->name, wanted->name) == 0)
            found = i;
        if (about)
            gfree(about);
    }
    return found;
}

struct Frame
{
    int ok;
    GINFO *info;
    unsigned char *pixels;
    int rowbytes;
};

// Reads one frame with module m of a side; is() and open() results are part of the comparison.
static Frame ReadFrame(const Side &side, int m, const char *name, int frame, int *isscore, int *opened)
{
    Frame result = { 0, 0, 0, 0 };
    GSTREAM *stream = side.open(name);
    if (!stream)
        return result;
    *isscore = side.modules[m].is(stream);
    void *handle = 0;
    *opened = side.modules[m].open(&handle, stream, name, frame);
    if (*opened)
    {
        result.info = side.modules[m].info(handle, frame);
        if (result.info)
        {
            result.rowbytes = result.info->width * result.info->bpp / 8;
            int bytes = result.rowbytes * result.info->height;
            result.pixels = (unsigned char *)side.alloc(bytes > 0 ? bytes : 1);
            if (result.pixels && bytes > 0)
                memset(result.pixels, 0x5a, bytes);
            result.ok = side.modules[m].read(handle, result.info, result.pixels, result.rowbytes);
        }
        side.modules[m].close(handle);
    }
    side.close(stream);
    return result;
}

static int WriteFrame(const Side &side, int m, const char *name, const Frame &frame)
{
    GSTREAM *stream = side.wopen(name);
    if (!stream)
        return 0;
    void *handle = 0;
    int ok = side.modules[m].wopen(&handle, stream, name, 1);
    if (ok)
    {
        ok = side.modules[m].write(handle, frame.info, frame.pixels, frame.rowbytes);
        side.modules[m].wclose(handle);
    }
    side.close(stream);
    return ok;
}

// gimme_oracle module <original.dll> <module index> <file> <frames> <outdir> [--pad|--guard]
// Reads frames 0..frames-1 of file through both sides, compares is/open/read results, the whole
// descriptor (its own size) and the pixels, then writes each frame back with the same module.
static int Module(int argc, char **argv)
{
    if (argc < 7)
        return 2;
    HMODULE original = LoadOriginal(argv[2]);
    ApplyHeapMode(original, argc, argv, 7);
    int index = atoi(argv[3]);
    const char *name = argv[4];
    int frames = atoi(argv[5]);
    int recoveredindex = MatchRecovered(index);
    if (recoveredindex < 0)
    {
        printf("module %d not recovered\n", index);
        return 1;
    }
    Side sides[2] = { OriginalSide(), RecoveredSide() };
    int modules[2] = { index, recoveredindex };
    int failures = 0;
    for (int f = 0; f < frames; ++f)
    {
        Frame frame[2];
        int score[2] = { 0, 0 }, opened[2] = { 0, 0 };
        for (int s = 0; s < 2; ++s)
            frame[s] = ReadFrame(sides[s], modules[s], name, f, &score[s], &opened[s]);
        bool same = score[0] == score[1] && opened[0] == opened[1] && frame[0].ok == frame[1].ok &&
                    !frame[0].info == !frame[1].info;
        const char *what = same ? "" : "results";
        if (same && frame[0].info)
        {
            if (frame[0].info->size != frame[1].info->size ||
                memcmp(frame[0].info, frame[1].info, frame[0].info->size) != 0)
            {
                same = false;
                what = "descriptor";
                for (int i = 0; i < frame[0].info->size; ++i)
                    if (((unsigned char *)frame[0].info)[i] != ((unsigned char *)frame[1].info)[i])
                    {
                        printf("  descriptor differs first at +%#x\n", i);
                        break;
                    }
            }
            else if (frame[0].pixels && memcmp(frame[0].pixels, frame[1].pixels,
                                               frame[0].rowbytes * frame[0].info->height) != 0)
            {
                same = false;
                what = "pixels";
            }
        }
        printf("frame %d: is %d/%d open %d/%d read %d/%d %s%s\n", f, score[0], score[1], opened[0], opened[1],
               frame[0].ok, frame[1].ok, same ? "MATCH" : "DIFF ", what);
        failures += !same;
        if (same && frame[0].info && frame[0].ok)
        {
            char written[2][MAX_PATH];
            for (int s = 0; s < 2; ++s)
            {
                sprintf(written[s], "%s\\%s_%d.out", argv[6], sides[s].label, f);
                DeleteFileA(written[s]);
                WriteFrame(sides[s], modules[s], written[s], frame[s]);
            }
            printf("  write: ");
            failures += CompareFiles(written[0], written[1]);
        }
    }
    printf("%s\n", failures ? "FAIL" : "PASS");
    return failures != 0;
}

// gimme_oracle abouts <original.dll>
// Compares every recovered about() record, byte for byte over its own size field, with the
// original entry of the same index in the original table order given by its name.
static int CompareAbout(const char *kind, int index, const unsigned char *original, const unsigned char *recovered,
                        int nameoffset)
{
    int size = ((const int *)original)[1];
    int differs = ((const int *)recovered)[1] != size || memcmp(original, recovered, size) != 0;
    printf("%s %2d %-16s %s\n", kind, index, (const char *)original + nameoffset, differs ? "DIFF" : "MATCH");
    if (differs)
        for (int i = 0; i < size; ++i)
            if (original[i] != recovered[i])
            {
                printf("  first difference at +%#x: %02x/%02x\n", i, original[i], recovered[i]);
                break;
            }
    return differs;
}

typedef unsigned char *(__cdecl *AboutFn)(void);

static int FindByName(AboutFn *table, int stride, int nameoffset, const char *name)
{
    for (int i = 0; table[i * stride]; ++i)
    {
        unsigned char *about = table[i * stride]();
        bool same = about && strcmp((const char *)about + nameoffset, name) == 0;
        if (same)
            return i;
    }
    return -1;
}

static int Abouts(int argc, char **argv)
{
    if (argc < 3)
        return 2;
    LoadOriginal(argv[2]);
    struct
    {
        const char *kind;
        AboutFn *original;
        AboutFn *recovered;
        int stride, nameoffset;
    } lists[] = {
        { "module", (AboutFn *)0x10431a50, (AboutFn *)gimexmodules, 9, 0xbc },
        { "filter", (AboutFn *)0x10432428, (AboutFn *)gimexfilters, 5, 0x48 },
        { "quantizer", (AboutFn *)0x10432720, (AboutFn *)gimexquantizers, 4, 0x38 } };
    int failures = 0, count = 0;
    for (int l = 0; l < 3; ++l)
        for (int i = 0; lists[l].recovered[i * lists[l].stride]; ++i)
        {
            unsigned char *mine = lists[l].recovered[i * lists[l].stride]();
            int index = FindByName(lists[l].original, lists[l].stride, lists[l].nameoffset,
                                   (const char *)mine + lists[l].nameoffset);
            ++count;
            if (index < 0)
            {
                printf("%s %s has no original\n", lists[l].kind, (const char *)mine + lists[l].nameoffset);
                ++failures;
                continue;
            }
            failures += CompareAbout(lists[l].kind, index, lists[l].original[index * lists[l].stride](), mine,
                                     lists[l].nameoffset);
        }
    printf("%d records, %s\n", count, failures ? "FAIL" : "PASS");
    return failures != 0;
}

#include "filters_oracle.h"

int main(int argc, char **argv)
{
    if (argc > 1 && strcmp(argv[1], "filters") == 0)
        return filteroracle::Filters(argc, argv);
    if (argc > 1 && strcmp(argv[1], "convert") == 0)
        return Convert(argc, argv);
    if (argc > 1 && strcmp(argv[1], "module") == 0)
        return Module(argc, argv);
    if (argc > 1 && strcmp(argv[1], "abouts") == 0)
        return Abouts(argc, argv);
    if (argc > 3 && strcmp(argv[1], "is") == 0)
    {
        int IsOracle(int argc, char **argv);   // is_oracle.cpp
        HMODULE original = LoadOriginal(argv[2]);
        ApplyHeapMode(original, argc, argv, 4);
        return IsOracle(argc, argv);
    }
    fprintf(stderr, "usage: gimme_oracle convert <original.dll> <source> <frame> <outdir> [--pad|--guard]\n"
                    "       gimme_oracle module <original.dll> <module> <file> <frames> <outdir> [--pad|--guard]\n");
    return 2;
}

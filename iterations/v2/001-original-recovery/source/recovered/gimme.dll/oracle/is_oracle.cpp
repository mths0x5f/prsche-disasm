// Detection oracle: every module's is() and the whole GIMEX_detect on a list of files.
//
//   gimme_oracle is <original.dll> <list.txt> [--pad]
//
// list.txt names one file per line.  For each file, each recovered module is paired with the
// original module of the same name; both open the file with their own gopen and score it.
// Then GIMEX_detect (original 100049c0) runs on both sides.  Prints one line per mismatch and
// a summary.

#include <windows.h>
#include <stdio.h>
#include <string.h>

#include "../_sem_arquivo/gimex/gimex.h"

typedef GSTREAM *(GCALL *OpenFn)(const char *);
typedef int(GCALL *CloseFn)(GSTREAM *);
typedef int(GCALL *DetectFn)(const char *, GSTREAM *);

static GMODULE *const originalmodules = (GMODULE *)0x10431a50;
static const OpenFn originalopen = (OpenFn)0x10003650;
static const CloseFn originalclose = (CloseFn)0x10003d20;
static const DetectFn originaldetect = (DetectFn)0x100049c0;
static int(GCALL *const originalfree)(void *) = (int(GCALL *)(void *))0x100032a0;

static int OriginalIndexOf(const char *name)
{
    for (int i = 0; originalmodules[i].about; ++i)
    {
        GABOUT *about = originalmodules[i].about();
        bool same = about && strcmp(about->name, name) == 0;
        if (about)
            originalfree(about);
        if (same)
            return i;
    }
    return -1;
}

int IsOracle(int argc, char **argv)
{
    if (argc < 4)
        return 2;
    FILE *list = fopen(argv[3], "r");
    if (!list)
        return 2;
    int pairs[128][2];
    int count = 0;
    for (int i = 0; gimexmodules[i].about && count < 128; ++i)
    {
        GABOUT *about = gimexmodules[i].about();
        int original = OriginalIndexOf(about->name);
        if (original >= 0)
        {
            pairs[count][0] = original;
            pairs[count][1] = i;
            ++count;
        }
        gfree(about);
    }
    int files = 0, scores = 0, mismatches = 0;
    char name[MAX_PATH];
    while (fgets(name, sizeof(name), list))
    {
        name[strcspn(name, "\r\n")] = 0;
        if (!name[0])
            continue;
        ++files;
        for (int p = 0; p < count; ++p)
        {
            GSTREAM *a = originalopen(name);
            GSTREAM *b = gopen(name);
            if (!a || !b)
            {
                printf("%s: open failed\n", name);
                ++mismatches;
                break;
            }
            int expected = originalmodules[pairs[p][0]].is(a);
            int actual = gimexmodules[pairs[p][1]].is(b);
            ++scores;
            if (expected != actual)
            {
                GABOUT *about = gimexmodules[pairs[p][1]].about();
                printf("%s: module %d %s is %d / %d\n", name, pairs[p][0], about->name, expected, actual);
                gfree(about);
                ++mismatches;
            }
            originalclose(a);
            gclose(b);
        }
        GSTREAM *a = originalopen(name);
        GSTREAM *b = gopen(name);
        if (a && b)
        {
            int expected = originaldetect(name, a);
            int actual = GIMEX_detect(name, b);
            GABOUT *mine = gimexmodules[actual].about();
            GABOUT *theirs = originalmodules[expected].about();
            if (strcmp(mine->name, theirs->name) != 0)
            {
                printf("%s: detect %s / %s\n", name, theirs->name, mine->name);
                ++mismatches;
            }
            gfree(mine);
            originalfree(theirs);
        }
        if (a)
            originalclose(a);
        if (b)
            gclose(b);
    }
    fclose(list);
    printf("%d files, %d modules, %d scores, %d mismatches: %s\n", files, count, scores, mismatches,
           mismatches ? "FAIL" : "PASS");
    return mismatches != 0;
}

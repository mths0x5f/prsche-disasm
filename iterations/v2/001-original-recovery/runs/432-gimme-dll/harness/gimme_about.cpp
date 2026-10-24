// Dumps the "about" record of every GIMEX format module linked into the original gimme.dll.
// The module table lives at VA 0x10431a50 (9 entry points per module, 0x24 bytes each) and ends
// with a null about() pointer; FUN_10005161 counts it the same way.
//
// Usage: gimme_about <gimme.dll>   (the DLL must load at its preferred base 0x10000000)

#include <windows.h>
#include <stdio.h>
#include <ctype.h>

typedef unsigned char *(__cdecl *AboutFn)(void);

static void PrintText(const unsigned char *p, int n)
{
    putchar('"');
    for (int i = 0; i < n && p[i]; ++i)
        putchar(isprint(p[i]) ? p[i] : '.');
    putchar('"');
}

int main(int argc, char **argv)
{
    HMODULE gimme = LoadLibraryA(argc > 1 ? argv[1] : "gimme.dll");
    if (gimme != (HMODULE)0x10000000)
    {
        fprintf(stderr, "gimme.dll not at its preferred base (%p)\n", (void *)gimme);
        return 2;
    }
    AboutFn *table = (AboutFn *)0x10431a50;
    for (int module = 0; table[module * 9]; ++module)
    {
        const unsigned char *about = table[module * 9]();
        if (!about)
        {
            printf("%2d about() returned null\n", module);
            continue;
        }
        const unsigned *w = (const unsigned *)about;
        printf("%2d tag=%08x size=%#x version=%u flags=%08x w5=%u w6=%u w7=%08x w8=%08x",
               module, w[0], w[1], w[2], w[3], w[5], w[6], w[7], w[8]);
        printf("\n   ext:");
        for (int i = 0; i < 8; ++i)
            if (about[0x3c + i * 8])
            {
                putchar(' ');
                PrintText(about + 0x3c + i * 8, 8);
            }
        printf("\n   author ");
        PrintText(about + 0x7c, 32);
        printf(" short ");
        PrintText(about + 0x9c, 8);
        printf(" a4 ");
        PrintText(about + 0xa4, 8);
        printf(" ac ");
        PrintText(about + 0xac, 16);
        printf(" bc ");
        PrintText(about + 0xbc, 32);
        printf("\n   raw ");
        for (unsigned i = 0; i < w[1]; ++i)
            printf("%02x", about[i]);
        printf("\n");
    }

    // Filter table at 0x10432428 (5 entry points, 0x14 bytes each); FUN_100054ae matches the
    // name at about+0x48.  Quantizer table at 0x10432720 (4 entry points); name at about+0x38.
    struct { unsigned table, stride, name; const char *kind; } lists[] = {
        { 0x10432428, 5, 0x48, "filter" }, { 0x10432720, 4, 0x38, "quantizer" } };
    for (int l = 0; l < 2; ++l)
    {
        AboutFn *entries = (AboutFn *)(ULONG_PTR)lists[l].table;
        for (int i = 0; entries[i * lists[l].stride]; ++i)
        {
            const unsigned char *about = entries[i * lists[l].stride]();
            if (!about)
                continue;
            const unsigned *w = (const unsigned *)about;
            printf("%s %2d tag=%08x size=%#x version=%u ", lists[l].kind, i, w[0], w[1], w[2]);
            for (int t = 0x10; t < 0x80; t += 0x10)
            {
                printf(" +%02x ", t);
                PrintText(about + t, 16);
            }
            printf(" name@%#x ", lists[l].name);
            PrintText(about + lists[l].name, 32);
            printf("\n");
        }
    }
    return 0;
}

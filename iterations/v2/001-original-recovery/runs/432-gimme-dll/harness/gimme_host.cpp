// Loads a gimme.dll and calls ConvertFile exactly as Porsche.exe does at 004dbe36:
//   char ConvertFile(const char *source, char *destination, int image_index)   (cdecl)
//
// With --guard, every heap block the DLL allocates through its KERNEL32 imports
// (HeapAlloc/HeapReAlloc/HeapFree/HeapSize/HeapValidate) is placed at the end of
// its own committed pages, followed by a PAGE_NOACCESS page.  The block keeps the
// 8-byte granularity of the Windows heap, so only reads past what the real heap
// would have reserved for the block fault.  A vectored handler reports the fault
// against the block that owns the guard page and exits with code 3.
//
// Usage: gimme_host <gimme.dll> <source> <destination> <image_index> [--guard] [--log <file>]

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef char (__cdecl *ConvertFileFn)(const char *, char *, int);

struct GuardBlock
{
    unsigned char *user;
    SIZE_T requested;
    unsigned char *base;
    SIZE_T reserved;
};

static GuardBlock g_blocks[65536];
static int g_blockCount;
static HMODULE g_gimme;
static FILE *g_log;

static GuardBlock *FindBlock(const void *user)
{
    for (int i = 0; i < g_blockCount; ++i)
        if (g_blocks[i].user == user)
            return &g_blocks[i];
    return NULL;
}

static GuardBlock *FindBlockByGuard(ULONG_PTR address)
{
    for (int i = 0; i < g_blockCount; ++i)
    {
        ULONG_PTR guard = (ULONG_PTR)g_blocks[i].base + g_blocks[i].reserved - 0x1000;
        if (g_blocks[i].user && address >= guard && address < guard + 0x1000)
            return &g_blocks[i];
    }
    return NULL;
}

static void *GuardAlloc(SIZE_T size)
{
    SIZE_T rounded = (size + 7) & ~(SIZE_T)7;
    if (rounded == 0)
        rounded = 8;
    SIZE_T dataPages = (rounded + 0xfff) & ~(SIZE_T)0xfff;
    SIZE_T reserved = dataPages + 0x1000;
    unsigned char *base = (unsigned char *)VirtualAlloc(NULL, reserved, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (!base)
        return NULL;
    DWORD old;
    VirtualProtect(base + dataPages, 0x1000, PAGE_NOACCESS, &old);

    GuardBlock *slot = NULL;
    for (int i = 0; i < g_blockCount; ++i)
        if (!g_blocks[i].user) { slot = &g_blocks[i]; break; }
    if (!slot)
    {
        if (g_blockCount == (int)(sizeof(g_blocks) / sizeof(g_blocks[0])))
            return NULL;
        slot = &g_blocks[g_blockCount++];
    }
    slot->base = base;
    slot->reserved = reserved;
    slot->requested = size;
    slot->user = base + dataPages - rounded;
    if (g_log)
        fprintf(g_log, "alloc %p size %#lx\n", slot->user, (unsigned long)size);
    return slot->user;
}

static LPVOID WINAPI HookHeapAlloc(HANDLE heap, DWORD flags, SIZE_T size)
{
    (void)heap; (void)flags;
    return GuardAlloc(size);
}

static BOOL WINAPI HookHeapFree(HANDLE heap, DWORD flags, LPVOID memory)
{
    GuardBlock *block = FindBlock(memory);
    if (!block)
        return HeapFree(heap, flags, memory);
    VirtualFree(block->base, 0, MEM_RELEASE);
    block->user = NULL;
    return TRUE;
}

static LPVOID WINAPI HookHeapReAlloc(HANDLE heap, DWORD flags, LPVOID memory, SIZE_T size)
{
    GuardBlock *block = FindBlock(memory);
    if (!block)
        return HeapReAlloc(heap, flags, memory, size);
    if (flags & HEAP_REALLOC_IN_PLACE_ONLY)
        return NULL;
    SIZE_T keep = block->requested < size ? block->requested : size;
    void *moved = GuardAlloc(size);
    if (!moved)
        return NULL;
    memcpy(moved, memory, keep);
    HookHeapFree(heap, 0, memory);
    return moved;
}

static SIZE_T WINAPI HookHeapSize(HANDLE heap, DWORD flags, LPCVOID memory)
{
    GuardBlock *block = FindBlock(memory);
    if (!block)
        return HeapSize(heap, flags, memory);
    return block->requested;
}

static BOOL WINAPI HookHeapValidate(HANDLE heap, DWORD flags, LPCVOID memory)
{
    if (memory && FindBlock(memory))
        return TRUE;
    return HeapValidate(heap, flags, memory);
}

static void PatchImport(HMODULE module, const char *dll, const char *name, void *replacement)
{
    unsigned char *image = (unsigned char *)module;
    IMAGE_NT_HEADERS *nt = (IMAGE_NT_HEADERS *)(image + ((IMAGE_DOS_HEADER *)image)->e_lfanew);
    IMAGE_DATA_DIRECTORY dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    for (IMAGE_IMPORT_DESCRIPTOR *desc = (IMAGE_IMPORT_DESCRIPTOR *)(image + dir.VirtualAddress); desc->Name; ++desc)
    {
        if (_stricmp((const char *)(image + desc->Name), dll) != 0)
            continue;
        IMAGE_THUNK_DATA *names = (IMAGE_THUNK_DATA *)(image + (desc->OriginalFirstThunk ? desc->OriginalFirstThunk : desc->FirstThunk));
        IMAGE_THUNK_DATA *slots = (IMAGE_THUNK_DATA *)(image + desc->FirstThunk);
        for (; names->u1.AddressOfData; ++names, ++slots)
        {
            if (IMAGE_SNAP_BY_ORDINAL(names->u1.Ordinal))
                continue;
            IMAGE_IMPORT_BY_NAME *byName = (IMAGE_IMPORT_BY_NAME *)(image + names->u1.AddressOfData);
            if (strcmp((const char *)byName->Name, name) != 0)
                continue;
            DWORD old;
            VirtualProtect(&slots->u1.Function, sizeof(void *), PAGE_READWRITE, &old);
            slots->u1.Function = (ULONG_PTR)replacement;
            VirtualProtect(&slots->u1.Function, sizeof(void *), old, &old);
            return;
        }
    }
    fprintf(stderr, "import %s!%s not found\n", dll, name);
}

static LONG CALLBACK FaultHandler(EXCEPTION_POINTERS *info)
{
    if (info->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION)
        return EXCEPTION_CONTINUE_SEARCH;
    CONTEXT *c = info->ContextRecord;
    ULONG_PTR address = info->ExceptionRecord->ExceptionInformation[1];
    ULONG_PTR eip = c->Eip;
    MEMORY_BASIC_INFORMATION mbi;
    VirtualQuery((void *)eip, &mbi, sizeof(mbi));
    printf("FAULT eip=%08lx module_rva=%08lx %s address=%08lx\n", (unsigned long)eip,
           (unsigned long)(eip - (ULONG_PTR)mbi.AllocationBase),
           mbi.AllocationBase == (void *)g_gimme ? "gimme" : "other",
           (unsigned long)address);
    printf("      eax=%08lx ecx=%08lx edx=%08lx esi=%08lx edi=%08lx ebp=%08lx\n",
           (unsigned long)c->Eax, (unsigned long)c->Ecx, (unsigned long)c->Edx,
           (unsigned long)c->Esi, (unsigned long)c->Edi, (unsigned long)c->Ebp);
    GuardBlock *block = FindBlockByGuard(address);
    if (block)
        printf("      past heap block %p (HeapAlloc size %#lx) at block offset %#lx\n",
               block->user, (unsigned long)block->requested,
               (unsigned long)(address - (ULONG_PTR)block->user));
    fflush(stdout);
    ExitProcess(3);
    return EXCEPTION_CONTINUE_SEARCH;
}

int main(int argc, char **argv)
{
    if (argc < 5)
    {
        fprintf(stderr, "usage: gimme_host <gimme.dll> <source> <destination> <image_index> [--guard] [--log file]\n");
        return 2;
    }
    bool guard = false;
    for (int i = 5; i < argc; ++i)
    {
        if (strcmp(argv[i], "--guard") == 0)
            guard = true;
        else if (strcmp(argv[i], "--log") == 0 && i + 1 < argc)
            g_log = fopen(argv[++i], "w");
    }

    g_gimme = LoadLibraryA(argv[1]);
    if (!g_gimme)
    {
        fprintf(stderr, "LoadLibrary failed %lu\n", GetLastError());
        return 2;
    }
    ConvertFileFn convert = (ConvertFileFn)GetProcAddress(g_gimme, "ConvertFile");
    if (!convert)
        return 2;
    if (guard)
    {
        PatchImport(g_gimme, "KERNEL32.dll", "HeapAlloc", (void *)HookHeapAlloc);
        PatchImport(g_gimme, "KERNEL32.dll", "HeapFree", (void *)HookHeapFree);
        PatchImport(g_gimme, "KERNEL32.dll", "HeapReAlloc", (void *)HookHeapReAlloc);
        PatchImport(g_gimme, "KERNEL32.dll", "HeapSize", (void *)HookHeapSize);
        PatchImport(g_gimme, "KERNEL32.dll", "HeapValidate", (void *)HookHeapValidate);
        AddVectoredExceptionHandler(1, FaultHandler);
    }

    // Porsche.exe passes a 0x80-byte destination buffer that already holds the path.
    char destination[0x80];
    memset(destination, 0, sizeof(destination));
    strncpy(destination, argv[3], sizeof(destination) - 1);
    char result = convert(argv[2], destination, atoi(argv[4]));
    printf("ConvertFile returned %d\n", (int)(unsigned char)result);
    if (g_log)
        fclose(g_log);
    return result ? 0 : 1;
}

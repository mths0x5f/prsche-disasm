// Heap redirection for differential runs of gimme.dll.
//
// HookHeap(module, pad) patches a module's KERNEL32 HeapAlloc/HeapFree/HeapReAlloc/HeapSize/
// HeapValidate imports.  Every block it then allocates sits at the end of its own pages,
// followed by `pad` zero bytes and a PAGE_NOACCESS page; the 8-byte heap granularity is kept.
//   pad == 0      any read past what the Windows heap would reserve faults (guard mode)
//   pad == 0x1000 reads past a block see zeros, the same for every run and every module
// A vectored handler reports a fault inside a guard page and exits with code 3.

#ifndef GIMME_HEAPHOOK_H
#define GIMME_HEAPHOOK_H

#include <windows.h>
#include <stdio.h>
#include <string.h>

namespace heaphook
{
struct Block
{
    unsigned char *user;
    SIZE_T requested;
    unsigned char *base;
    SIZE_T reserved;
};

static Block blocks[1 << 17];
static int blockcount;
static SIZE_T padding;
// The real functions, so fallbacks never go through a patched import of our own module.
static BOOL(WINAPI *RealHeapFree)(HANDLE, DWORD, LPVOID);
static LPVOID(WINAPI *RealHeapReAlloc)(HANDLE, DWORD, LPVOID, SIZE_T);
static SIZE_T(WINAPI *RealHeapSize)(HANDLE, DWORD, LPCVOID);
static BOOL(WINAPI *RealHeapValidate)(HANDLE, DWORD, LPCVOID);

static Block *Find(const void *user)
{
    for (int i = blockcount - 1; i >= 0; --i)
        if (blocks[i].user == user)
            return &blocks[i];
    return NULL;
}

static Block *FindByGuard(ULONG_PTR address)
{
    for (int i = 0; i < blockcount; ++i)
    {
        ULONG_PTR guard = (ULONG_PTR)blocks[i].base + blocks[i].reserved - 0x1000;
        if (blocks[i].user && address >= guard && address < guard + 0x1000)
            return &blocks[i];
    }
    return NULL;
}

static void *Allocate(SIZE_T size)
{
    SIZE_T rounded = (size + 7) & ~(SIZE_T)7;
    if (rounded == 0)
        rounded = 8;
    SIZE_T dataPages = (rounded + padding + 0xfff) & ~(SIZE_T)0xfff;
    SIZE_T reserved = dataPages + 0x1000;
    unsigned char *base = (unsigned char *)VirtualAlloc(NULL, reserved, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    if (!base)
        return NULL;
    DWORD old;
    VirtualProtect(base + dataPages, 0x1000, PAGE_NOACCESS, &old);
    Block *slot = NULL;
    for (int i = 0; i < blockcount; ++i)
        if (!blocks[i].user)
        {
            slot = &blocks[i];
            break;
        }
    if (!slot)
    {
        if (blockcount == (int)(sizeof(blocks) / sizeof(blocks[0])))
            return NULL;
        slot = &blocks[blockcount++];
    }
    slot->base = base;
    slot->reserved = reserved;
    slot->requested = size;
    slot->user = base + dataPages - padding - rounded;
    return slot->user;
}

static LPVOID WINAPI HookHeapAlloc(HANDLE, DWORD, SIZE_T size)
{
    return Allocate(size);
}

static BOOL WINAPI HookHeapFree(HANDLE heap, DWORD flags, LPVOID memory)
{
    Block *block = Find(memory);
    if (!block)
        return RealHeapFree(heap, flags, memory);
    VirtualFree(block->base, 0, MEM_RELEASE);
    block->user = NULL;
    return TRUE;
}

static LPVOID WINAPI HookHeapReAlloc(HANDLE heap, DWORD flags, LPVOID memory, SIZE_T size)
{
    Block *block = Find(memory);
    if (!block)
        return RealHeapReAlloc(heap, flags, memory, size);
    if (flags & HEAP_REALLOC_IN_PLACE_ONLY)
        return NULL;
    SIZE_T keep = block->requested < size ? block->requested : size;
    void *moved = Allocate(size);
    if (!moved)
        return NULL;
    memcpy(moved, memory, keep);
    HookHeapFree(heap, 0, memory);
    return moved;
}

static SIZE_T WINAPI HookHeapSize(HANDLE heap, DWORD flags, LPCVOID memory)
{
    Block *block = Find(memory);
    return block ? block->requested : RealHeapSize(heap, flags, memory);
}

static BOOL WINAPI HookHeapValidate(HANDLE heap, DWORD flags, LPCVOID memory)
{
    if (memory && Find(memory))
        return TRUE;
    return RealHeapValidate(heap, flags, memory);
}

static void PatchImport(HMODULE module, const char *name, void *replacement)
{
    unsigned char *image = (unsigned char *)module;
    IMAGE_NT_HEADERS *nt = (IMAGE_NT_HEADERS *)(image + ((IMAGE_DOS_HEADER *)image)->e_lfanew);
    IMAGE_DATA_DIRECTORY dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    for (IMAGE_IMPORT_DESCRIPTOR *desc = (IMAGE_IMPORT_DESCRIPTOR *)(image + dir.VirtualAddress); desc->Name; ++desc)
    {
        if (_stricmp((const char *)(image + desc->Name), "KERNEL32.dll") != 0)
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
        }
    }
}

static LONG CALLBACK FaultHandler(EXCEPTION_POINTERS *info)
{
    if (info->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION)
        return EXCEPTION_CONTINUE_SEARCH;
    CONTEXT *c = info->ContextRecord;
    ULONG_PTR address = info->ExceptionRecord->ExceptionInformation[1];
    MEMORY_BASIC_INFORMATION mbi;
    VirtualQuery((void *)(ULONG_PTR)c->Eip, &mbi, sizeof(mbi));
    char modulename[MAX_PATH] = "?";
    GetModuleFileNameA((HMODULE)mbi.AllocationBase, modulename, MAX_PATH);
    const char *shortname = strrchr(modulename, '\\') ? strrchr(modulename, '\\') + 1 : modulename;
    printf("FAULT eip=%08lx %s+%#lx address=%08lx\n", (unsigned long)c->Eip, shortname,
           (unsigned long)(c->Eip - (ULONG_PTR)mbi.AllocationBase), (unsigned long)address);
    printf("      eax=%08lx ecx=%08lx edx=%08lx esi=%08lx edi=%08lx ebp=%08lx\n",
           (unsigned long)c->Eax, (unsigned long)c->Ecx, (unsigned long)c->Edx,
           (unsigned long)c->Esi, (unsigned long)c->Edi, (unsigned long)c->Ebp);
    Block *block = FindByGuard(address);
    if (block)
        printf("      past heap block %p (HeapAlloc size %#lx) at block offset %#lx\n", block->user,
               (unsigned long)block->requested, (unsigned long)(address - (ULONG_PTR)block->user));
    fflush(stdout);
    ExitProcess(3);
    return EXCEPTION_CONTINUE_SEARCH;
}

static void Install()
{
    static bool installed;
    if (!installed)
        AddVectoredExceptionHandler(1, FaultHandler);
    installed = true;
}

static void HookHeap(HMODULE module, SIZE_T pad)
{
    HMODULE kernel = GetModuleHandleA("kernel32.dll");
    if (!RealHeapFree)
    {
        RealHeapFree = (BOOL(WINAPI *)(HANDLE, DWORD, LPVOID))GetProcAddress(kernel, "HeapFree");
        RealHeapReAlloc = (LPVOID(WINAPI *)(HANDLE, DWORD, LPVOID, SIZE_T))GetProcAddress(kernel, "HeapReAlloc");
        RealHeapSize = (SIZE_T(WINAPI *)(HANDLE, DWORD, LPCVOID))GetProcAddress(kernel, "HeapSize");
        RealHeapValidate = (BOOL(WINAPI *)(HANDLE, DWORD, LPCVOID))GetProcAddress(kernel, "HeapValidate");
    }
    padding = pad;
    PatchImport(module, "HeapAlloc", (void *)HookHeapAlloc);
    PatchImport(module, "HeapFree", (void *)HookHeapFree);
    PatchImport(module, "HeapReAlloc", (void *)HookHeapReAlloc);
    PatchImport(module, "HeapSize", (void *)HookHeapSize);
    PatchImport(module, "HeapValidate", (void *)HookHeapValidate);
    Install();
}
}

#endif

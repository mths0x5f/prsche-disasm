// Run 430 runtime: runs the lowered Porsche.exe functions against the original image.
//
// - The original image is mapped at its own VAs (0x00400000) from local/game/Porsche.exe
//   at start-up; its code sections stay readable data but are never executable.
// - Guest code runs on the real thread stack; this host code runs on a side stack, so the
//   TEB stack bounds and the fs:[0] chain stay those of the guest.
// - A call from lowered code to an address outside the image is a native call made on
//   the guest stack (forward bridge). Native code calling into the image faults on the
//   non-executable page; the vectored handler redirects it to the lowered body
//   (reverse bridge).
// - Two kernel32 imports are shimmed because the host EXE is the loaded module:
//   GetModuleHandleA(NULL) returns 0x00400000 and GetModuleFileNameA names the original.
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "machine257.h"

struct LoweredEntry430 { U va; void (*fn)(Machine257&); };
extern const unsigned lowered_count430;
extern const LoweredEntry430 lowered_table430[];
extern "C" char reserve430[];  // reserve_430.asm, at 0x00401000

namespace {

const U kBase = 0x00400000u;
U g_image_end;
U g_code_lo, g_code_hi;
void (**g_entries)(Machine257&);
char g_original_path[MAX_PATH];
U g_entry_va;
const U kReserveBytes = 0x2e2000u;  // must match reserve_430.asm

__declspec(thread) U t_host_sp;      // host stack to resume on while native code runs
__declspec(thread) U t_side_top;     // side stack of a thread first entered from native code
__declspec(thread) Machine257* t_current;

void fatal(const char* what, const Machine257* s, U extra)
{
    fprintf(stderr, "[430] %s pc=%08x extra=%08x", what, s ? s->pc : 0u, extra);
    if (s)
        fprintf(stderr, " eax=%08x ecx=%08x edx=%08x ebx=%08x esp=%08x ebp=%08x esi=%08x edi=%08x stop=%u",
                s->r[0], s->r[1], s->r[2], s->r[3], s->r[4], s->r[5], s->r[6], s->r[7], static_cast<U>(s->stop));
    fprintf(stderr, "\n");
    fflush(stderr);
    TerminateProcess(GetCurrentProcess(), 0x430);
}

void reset_machine(Machine257& m)
{
    memset(&m, 0, sizeof m);
    m.stop = Stop257::Running;
    m.fpu_cw = 0x037fu;
    m.mxcsr = 0x1f80u;
    m.flags = 0x202u;
}

// ---- forward bridge -------------------------------------------------------------------
struct Fwd { U eax, ecx, edx, esp, target, host_esp; };

__declspec(naked) void __cdecl forward_asm(Fwd*)
{
    __asm {
        mov eax, [esp + 4]
        push ebx
        push esi
        push edi
        push ebp
        mov esi, eax
        mov [esi + 20], esp
        mov esp, [esi + 12]
        mov eax, [esi + 0]
        mov ecx, [esi + 4]
        mov edx, [esi + 8]
        cld
        call dword ptr [esi + 16]
        mov [esi + 0], eax
        mov [esi + 4], ecx
        mov [esi + 8], edx
        mov [esi + 12], esp
        mov esp, [esi + 20]
        pop ebp
        pop edi
        pop esi
        pop ebx
        ret
    }
}

void native_call(Machine257& s, U target)
{
    U return_pc = read257(s.r[4], 4u);
    Fwd f{ s.r[0], s.r[1], s.r[2], s.r[4] + 4u, target, 0u };
    U saved = t_host_sp;
    char here;
    t_host_sp = (reinterpret_cast<U>(&here) - 0x1000u) & ~15u;
    forward_asm(&f);
    t_host_sp = saved;
    t_current = &s;
    s.r[0] = f.eax; s.r[1] = f.ecx; s.r[2] = f.edx; s.r[4] = f.esp;
    s.pc = return_pc;
    s.stop = Stop257::Returned;
}

// ---- reverse bridge -------------------------------------------------------------------
struct Resume { U edi, esi, ebp, esp, ebx, edx, ecx, eax, pc; };
__declspec(thread) Resume t_resume;

extern "C" U __cdecl pick_host_stack430()
{
    if (t_host_sp)
        return t_host_sp;
    if (!t_side_top) {
        const SIZE_T size = 64u << 20;
        void* p = VirtualAlloc(nullptr, size, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
        if (!p) fatal("side stack allocation failed", nullptr, 0);
        t_side_top = reinterpret_cast<U>(p) + static_cast<U>(size) - 64u;
    }
    return t_side_top;
}

extern "C" Resume* __cdecl reverse_entry430(U* block)
{
    // block: pushad image (edi esi ebp esp ebx edx ecx eax), then the target VA, then the
    // native return address.
    Machine257 m;
    reset_machine(m);
    m.r[7] = block[0]; m.r[6] = block[1]; m.r[5] = block[2];
    m.r[3] = block[4]; m.r[2] = block[5]; m.r[1] = block[6]; m.r[0] = block[7];
    U target = block[8];
    m.r[4] = reinterpret_cast<U>(block + 9);
    Machine257* outer = t_current;
    t_current = &m;
    dispatch257(m, target);
    if (m.stop != Stop257::Returned)
        fatal("reverse entry did not return", &m, target);
    t_current = outer;
    Resume& r = t_resume;
    r.edi = m.r[7]; r.esi = m.r[6]; r.ebp = m.r[5]; r.esp = m.r[4];
    r.ebx = m.r[3]; r.edx = m.r[2]; r.ecx = m.r[1]; r.eax = m.r[0]; r.pc = m.pc;
    return &r;
}

__declspec(naked) void reverse_asm()
{
    __asm {
        pushad
        mov ebx, esp
        call pick_host_stack430
        mov esp, eax
        push ebx
        call reverse_entry430
        mov esp, [eax + 12]
        push dword ptr [eax + 32]
        mov edi, [eax + 0]
        mov esi, [eax + 4]
        mov ebp, [eax + 8]
        mov ebx, [eax + 16]
        mov edx, [eax + 20]
        mov ecx, [eax + 24]
        mov eax, [eax + 28]
        ret
    }
}

LONG CALLBACK vectored430(EXCEPTION_POINTERS* info)
{
    EXCEPTION_RECORD* e = info->ExceptionRecord;
    CONTEXT* c = info->ContextRecord;
    if (e->ExceptionCode == EXCEPTION_ACCESS_VIOLATION && e->ExceptionInformation[0] == 8 &&
        c->Eip >= g_code_lo && c->Eip < g_code_hi) {
        c->Esp -= 4;
        *reinterpret_cast<U*>(c->Esp) = c->Eip;
        c->Eip = reinterpret_cast<U>(&reverse_asm);
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    if (e->ExceptionCode == EXCEPTION_ACCESS_VIOLATION || e->ExceptionCode == EXCEPTION_INT_DIVIDE_BY_ZERO ||
        e->ExceptionCode == EXCEPTION_STACK_OVERFLOW || e->ExceptionCode == EXCEPTION_ILLEGAL_INSTRUCTION) {
        fprintf(stderr, "[430] exception %08lx at host eip=%08lx addr=%08lx\n", e->ExceptionCode, c->Eip,
                e->NumberParameters > 1 ? static_cast<unsigned long>(e->ExceptionInformation[1]) : 0ul);
        fatal("fault while running", t_current, c->Eip);
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

// ---- image ----------------------------------------------------------------------------
HMODULE WINAPI shim_GetModuleHandleA(LPCSTR name)
{
    return name ? GetModuleHandleA(name) : reinterpret_cast<HMODULE>(kBase);
}

DWORD WINAPI shim_GetModuleFileNameA(HMODULE module, LPSTR out, DWORD size)
{
    if (module && module != reinterpret_cast<HMODULE>(kBase))
        return GetModuleFileNameA(module, out, size);
    DWORD n = static_cast<DWORD>(strlen(g_original_path));
    if (!size) return 0;
    DWORD copy = n < size ? n : size - 1;
    memcpy(out, g_original_path, copy);
    out[copy] = 0;
    return copy;
}

void map_image(const char* path)
{
    HANDLE f = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
    if (f == INVALID_HANDLE_VALUE) fatal("cannot open original image", nullptr, GetLastError());
    DWORD size = GetFileSize(f, nullptr), got = 0;
    BYTE* file = static_cast<BYTE*>(VirtualAlloc(nullptr, size, MEM_COMMIT, PAGE_READWRITE));
    ReadFile(f, file, size, &got, nullptr);
    CloseHandle(f);
    auto* nt = reinterpret_cast<IMAGE_NT_HEADERS32*>(file + reinterpret_cast<IMAGE_DOS_HEADER*>(file)->e_lfanew);
    if (nt->OptionalHeader.ImageBase != kBase) fatal("unexpected image base", nullptr, nt->OptionalHeader.ImageBase);
    U image_size = nt->OptionalHeader.SizeOfImage;
    // The host EXE is based at 0x00400000 and reserve_430.asm fills its first pages, so the
    // original sections land at their own VAs inside this module.
    if (reinterpret_cast<U>(&reserve430) != kBase + 0x1000u || image_size - 0x1000u > kReserveBytes)
        fatal("reserve does not cover the original image", nullptr, reinterpret_cast<U>(&reserve430));
    BYTE* img = reinterpret_cast<BYTE*>(kBase);
    DWORD old = 0;
    if (!VirtualProtect(img + 0x1000, image_size - 0x1000u, PAGE_READWRITE, &old))
        fatal("cannot unprotect the reserve", nullptr, GetLastError());
    g_image_end = kBase + image_size;
    g_entry_va = kBase + nt->OptionalHeader.AddressOfEntryPoint;
    // Our own headers stay; only the resource directory is pointed at the original's.
    auto* own = reinterpret_cast<IMAGE_NT_HEADERS32*>(img + reinterpret_cast<IMAGE_DOS_HEADER*>(img)->e_lfanew);
    VirtualProtect(img, 0x1000, PAGE_READWRITE, &old);
    own->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_RESOURCE] =
        nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_RESOURCE];
    VirtualProtect(img, 0x1000, old, &old);
    IMAGE_SECTION_HEADER* sec = IMAGE_FIRST_SECTION(nt);
    g_code_lo = 0xffffffffu; g_code_hi = 0;
    for (U i = 0; i < nt->FileHeader.NumberOfSections; ++i) {
        U raw = sec[i].SizeOfRawData < sec[i].Misc.VirtualSize ? sec[i].SizeOfRawData : sec[i].Misc.VirtualSize;
        memcpy(img + sec[i].VirtualAddress, file + sec[i].PointerToRawData, raw);
        if (sec[i].Characteristics & IMAGE_SCN_MEM_EXECUTE) {
            U lo = kBase + sec[i].VirtualAddress, hi = lo + sec[i].Misc.VirtualSize;
            if (lo < g_code_lo) g_code_lo = lo;
            if (hi > g_code_hi) g_code_hi = hi;
        }
    }
    const U import_rva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
    VirtualFree(file, 0, MEM_RELEASE);
    for (auto* d = reinterpret_cast<IMAGE_IMPORT_DESCRIPTOR*>(img + import_rva); d->Name; ++d) {
        const char* dll = reinterpret_cast<const char*>(img + d->Name);
        HMODULE h = LoadLibraryA(dll);
        if (!h) { fprintf(stderr, "[430] missing DLL %s\n", dll); continue; }
        auto* names = reinterpret_cast<U*>(img + (d->OriginalFirstThunk ? d->OriginalFirstThunk : d->FirstThunk));
        auto* iat = reinterpret_cast<U*>(img + d->FirstThunk);
        for (; *names; ++names, ++iat) {
            const char* fn = (*names & 0x80000000u) ? reinterpret_cast<const char*>(static_cast<ULONG_PTR>(*names & 0xffffu))
                                                     : reinterpret_cast<const char*>(img + *names + 2);
            FARPROC p = GetProcAddress(h, fn);
            if (!(*names & 0x80000000u)) {
                if (!strcmp(fn, "GetModuleHandleA")) p = reinterpret_cast<FARPROC>(&shim_GetModuleHandleA);
                if (!strcmp(fn, "GetModuleFileNameA")) p = reinterpret_cast<FARPROC>(&shim_GetModuleFileNameA);
            }
            if (!p) fprintf(stderr, "[430] unresolved import %s!%s\n", dll,
                            (*names & 0x80000000u) ? "#ordinal" : fn);
            *iat = reinterpret_cast<U>(p);
        }
    }
    g_entries = static_cast<void (**)(Machine257&)>(
        VirtualAlloc(nullptr, (g_code_hi - g_code_lo) * sizeof(void*), MEM_COMMIT, PAGE_READWRITE));
    for (U i = 0; i < lowered_count430; ++i)
        g_entries[lowered_table430[i].va - g_code_lo] = lowered_table430[i].fn;
}

void __cdecl run_guest(U guest_esp)
{
    Machine257 m;
    reset_machine(m);
    m.r[4] = guest_esp - 4u;
    write257(m.r[4], 4u, 0xfffffff0u);
    t_current = &m;
    dispatch257(m, g_entry_va);
    fatal(m.stop == Stop257::Returned ? "entry returned" : "entry stopped", &m, g_entry_va);
}

__declspec(naked) void __cdecl switch_to_side(U, void (__cdecl*)(U))
{
    __asm {
        mov eax, esp
        mov ecx, [esp + 4]
        mov edx, [esp + 8]
        mov esp, ecx
        sub eax, 0x10000
        and eax, 0xfffffff0
        push eax
        call edx
        int 3
    }
}

}  // namespace

void repne_scasb_down430(Machine257& s)
{
    U al = s.r[0] & 0xffu;
    while (s.r[1] != 0u) {
        U b = read257(s.r[7], 1u);
        s.r[7] -= 1u;
        s.r[1] -= 1u;
        subtract257(s, al, b, 0u, 8u);
        if (al == b) break;
    }
}

void unlowered430(Machine257& s)
{
    fatal("unlowered instruction reached (3DNow!/FPU environment image)", &s, s.pc);
}

void dispatch257(Machine257& s, U target)
{
    if (target >= g_code_lo && target < g_code_hi) {
        if (auto fn = g_entries[target - g_code_lo]) {
            s.pc = target;  // selects the entry of a multi-entry range
            fn(s);
            return;
        }
        s.pc = target;
        s.stop = Stop257::MissingEntry;
        fatal("no lowered body", &s, target);
    }
    if (target >= kBase && target < g_image_end) {
        s.stop = Stop257::MissingEntry;
        fatal("jump into non-code image range", &s, target);
    }
    native_call(s, target);
}

int main(int argc, char** argv)
{
    const char* path = argc > 1 ? argv[1] : "Porsche.exe";
    if (!GetFullPathNameA(path, MAX_PATH, g_original_path, nullptr)) return 2;
    map_image(g_original_path);
    AddVectoredExceptionHandler(1, &vectored430);
    fprintf(stderr, "[430] image mapped, %u lowered bodies, entry %08x\n", lowered_count430, g_entry_va);
    char* side = static_cast<char*>(VirtualAlloc(nullptr, 64u << 20, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
    switch_to_side(reinterpret_cast<U>(side) + (64u << 20) - 64u, &run_guest);
    return 0;
}

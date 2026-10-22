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
#include <stdlib.h>
#pragma comment(lib, "winmm.lib")
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
DWORD g_t0;                         // start time for trace timestamps
HANDLE g_main_thread;

__declspec(thread) U t_host_sp;      // host stack to resume on while native code runs
__declspec(thread) U t_side_top;     // side stack of a thread first entered from native code
__declspec(thread) Machine257* t_current;
Machine257* volatile g_last;      // diagnostics: last machine that changed hands
volatile U g_native_calls, g_last_native;

void fatal(const char* what, const Machine257* s, U extra)
{
    fprintf(stderr, "[430] %s pc=%08x extra=%08x", what, s ? s->pc : 0u, extra);
    if (s)
        fprintf(stderr, " eax=%08x ecx=%08x edx=%08x ebx=%08x esp=%08x ebp=%08x esi=%08x edi=%08x stop=%u",
                s->r[0], s->r[1], s->r[2], s->r[3], s->r[4], s->r[5], s->r[6], s->r[7], static_cast<U>(s->stop));
    fprintf(stderr, "\n");
    if (s) {
        // Memory each register points at, and the guest stack, for post-mortem analysis.
        static const char* names[8] = {"eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"};
        for (U k = 0; k < 8; ++k) {
            MEMORY_BASIC_INFORMATION mb;
            U a = s->r[k] & ~3u;
            if (k == 4) a = s->r[4];
            if (a < 0x10000u || !VirtualQuery(reinterpret_cast<void*>(a), &mb, sizeof mb) ||
                mb.State != MEM_COMMIT || (mb.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
                continue;
            U n = k == 4 ? 24u : 8u;
            U end = reinterpret_cast<U>(mb.BaseAddress) + static_cast<U>(mb.RegionSize);
            fprintf(stderr, "[430]   [%s=%08x]", names[k], a);
            for (U j = 0; j < n && a + 4 * j + 4 <= end; ++j)
                fprintf(stderr, " %08x", *reinterpret_cast<const U*>(a + 4 * j));
            fprintf(stderr, "\n");
        }
    }
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

// ---- import trace (PORSCHE430_TRACE=<max lines>) -------------------------------------
struct ImportName {
    U address;
    U iat_slot;
    char name[64];
    signed char traced;  // trace filter result: 0 unknown, 1 yes, -1 no
    U callback_arg;      // 1-based stack argument that carries a callback, or 0
};
const U kMaxImports = 2048;
ImportName g_imports[kMaxImports];
U g_import_count;
U g_import_hash[8192];  // address -> index + 1
long g_trace_left;

// Native functions that receive a callback pointer of the game as a plain argument. The
// pointer is swapped for an executable stub, so the native side enters the lowered body
// without a DEP fault (Thrash calls its state callback ~20k times per second).
struct CallbackArg { const char* name; U arg; };
const CallbackArg kCallbackArgs[] = {
    { "proc!_THRASH_setstate@8", 2 },
    { "WINMM.dll!timeSetEvent", 3 },
};

U import_hash(U address) { return (address * 2654435761u) >> 19; }

ImportName* find_import(U address)
{
    for (U k = import_hash(address), probes = 0; probes < 8192; k = (k + 1) & 8191, ++probes) {
        U i = g_import_hash[k];
        if (!i) return nullptr;
        if (g_imports[i - 1].address == address) return &g_imports[i - 1];
    }
    return nullptr;
}

void add_import(U address, U iat_slot, const char* fmt, const char* a, const char* b)
{
    if (g_import_count >= kMaxImports || find_import(address)) return;
    ImportName& im = g_imports[g_import_count];
    im.address = address;
    im.iat_slot = iat_slot;
    _snprintf(im.name, sizeof im.name, fmt, a, b);
    for (const CallbackArg& c : kCallbackArgs)
        if (!strcmp(im.name, c.name)) im.callback_arg = c.arg;
    U k = import_hash(address);
    while (g_import_hash[k]) k = (k + 1) & 8191;
    g_import_hash[k] = ++g_import_count;
}

const char* import_name(U target)
{
    ImportName* im = find_import(target);
    return im ? im->name : nullptr;
}

// ---- callback stubs: `push va; jmp reverse_asm` in executable memory ------------------
void reverse_asm();
CRITICAL_SECTION g_stub_lock;
BYTE* g_stub_pool;
U g_stub_used;
U g_stub_keys[1024], g_stub_values[1024];

U stub_for(U va)
{
    EnterCriticalSection(&g_stub_lock);
    U k = (va * 2654435761u) >> 22;
    while (g_stub_keys[k] && g_stub_keys[k] != va) k = (k + 1) & 1023;
    if (!g_stub_keys[k] && g_stub_used + 10u <= 0x10000u) {
        if (!g_stub_pool)
            g_stub_pool = static_cast<BYTE*>(VirtualAlloc(nullptr, 0x10000, MEM_COMMIT, PAGE_EXECUTE_READWRITE));
        BYTE* p = g_stub_pool + g_stub_used;
        p[0] = 0x68; *reinterpret_cast<U*>(p + 1) = va;
        p[5] = 0xe9; *reinterpret_cast<U*>(p + 6) = reinterpret_cast<U>(&reverse_asm) - reinterpret_cast<U>(p + 10);
        FlushInstructionCache(GetCurrentProcess(), p, 10);
        g_stub_keys[k] = va;
        g_stub_values[k] = reinterpret_cast<U>(p);
        g_stub_used += 10u;
    }
    U stub = g_stub_keys[k] == va ? g_stub_values[k] : va;
    LeaveCriticalSection(&g_stub_lock);
    return stub;
}

const char* g_trace_filter;  // ';'-separated substrings of import names, or null for all

int format_arg(char* out, int room, U v)
{
    // A stack argument, shown as text when it points at a printable string.
    MEMORY_BASIC_INFORMATION mi;
    if (v >= 0x10000u && VirtualQuery(reinterpret_cast<void*>(v), &mi, sizeof mi) && mi.State == MEM_COMMIT &&
        !(mi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) {
        const char* p = reinterpret_cast<const char*>(v);
        int n = 0;
        while (n < 80 && p[n] >= 0x20 && p[n] < 0x7f) ++n;
        if (n >= 2 && (p[n] == 0 || n == 80)) return _snprintf(out, room, " \"%.*s\"", n, p);
    }
    return _snprintf(out, room, " %08x", v);
}

bool trace_matches(const char* name)
{
    if (!g_trace_filter) return true;
    for (const char* f = g_trace_filter; *f;) {
        const char* end = strchr(f, ';');
        size_t n = end ? static_cast<size_t>(end - f) : strlen(f);
        for (const char* p = name; *p; ++p)
            if (n && !_strnicmp(p, f, n)) return true;
        if (!end) break;
        f = end + 1;
    }
    return false;
}

// Formats the call into `line`; returns false when the call is not traced.
bool trace_native(const Machine257& s, ImportName* found, char* line, int room)
{
    if (g_trace_left <= 0 || !found) return false;
    ImportName& im = *found;
    const char* name = im.name;
    if (!im.traced) im.traced = trace_matches(name) ? 1 : -1;
    if (im.traced < 0) return false;
    --g_trace_left;
    int n = _snprintf(line, room, "[430] +%lums t%lu %s from %08x:", GetTickCount() - g_t0, GetCurrentThreadId(), name,
                      read257(s.r[4], 4u));
    for (U k = 1; k <= 4 && n > 0 && n < room; ++k) n += format_arg(line + n, room - n, read257(s.r[4] + 4u * k, 4u));
    return true;
}

void native_call(Machine257& s, U target)
{
    char line[512];
    ImportName* im = find_import(target);
    bool traced = trace_native(s, im, line, sizeof line - 32);
    if (im && im->callback_arg) {
        U slot = s.r[4] + 4u * im->callback_arg;
        U cb = read257(slot, 4u);
        if (cb >= g_code_lo && cb < g_code_hi && g_entries[cb - g_code_lo])
            write257(slot, 4u, stub_for(cb));
    }
    U return_pc = read257(s.r[4], 4u);
    Fwd f{ s.r[0], s.r[1], s.r[2], s.r[4] + 4u, target, 0u };
    ++g_native_calls;
    g_last_native = target;
    U saved = t_host_sp;
    char here;
    t_host_sp = (reinterpret_cast<U>(&here) - 0x1000u) & ~15u;
    forward_asm(&f);
    t_host_sp = saved;
    t_current = &s;
    g_last = &s;
    s.r[0] = f.eax; s.r[1] = f.ecx; s.r[2] = f.edx; s.r[4] = f.esp;
    if (traced) fprintf(stderr, "%s -> %08x\n", line, f.eax);
    if (f.eax && im && im->iat_slot && !strcmp(im->name, "KERNEL32.dll!GetProcAddress")) {
        // Name pointers returned by GetProcAddress: traced by name, callback args known.
        U proc = read257(f.esp - 4u, 4u);  // stdcall popped (module, name): name was at esp-4
        if (proc >= 0x10000u)
            add_import(f.eax, 0, "proc!%s%s", reinterpret_cast<const char*>(proc), "");
    }
    s.pc = return_pc;
    s.stop = Stop257::Returned;
}

// ---- reverse bridge -------------------------------------------------------------------
struct Resume { U edi, esi, ebp, esp, ebx, edx, ecx, eax, pc; };
__declspec(thread) Resume t_resume;

// Reverse-entry counts by target (open addressing), dumped with the profile.
struct ReverseCount { volatile LONG va; volatile LONG n; };
ReverseCount g_reverse_counts[1024];

void count_reverse(U va)
{
    for (U k = (va * 2654435761u) >> 22, probes = 0; probes < 1024; k = (k + 1) & 1023, ++probes) {
        LONG seen = InterlockedCompareExchange(&g_reverse_counts[k].va, static_cast<LONG>(va), 0);
        if (seen == 0 || seen == static_cast<LONG>(va)) { InterlockedIncrement(&g_reverse_counts[k].n); return; }
    }
}

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
    count_reverse(target);
    m.r[4] = reinterpret_cast<U>(block + 9);
    Machine257* outer = t_current;
    t_current = &m;
    g_last = &m;
    dispatch257(m, target);
    if (m.stop != Stop257::Returned)
        fatal("reverse entry did not return", &m, target);
    t_current = outer;
    g_last = outer;
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
        // Module + offset of the faulting EIP, and the host registers (native code, e.g. a DLL).
        HMODULE mod = nullptr;
        char path[MAX_PATH] = "?";
        if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                               reinterpret_cast<LPCSTR>(static_cast<ULONG_PTR>(c->Eip)), &mod))
            GetModuleFileNameA(mod, path, MAX_PATH);
        fprintf(stderr, "[430]   in %s base=%08lx +%08lx; eax=%08lx ecx=%08lx edx=%08lx ebx=%08lx esp=%08lx ebp=%08lx esi=%08lx edi=%08lx\n",
                path, static_cast<unsigned long>(reinterpret_cast<ULONG_PTR>(mod)),
                static_cast<unsigned long>(c->Eip - reinterpret_cast<ULONG_PTR>(mod)),
                c->Eax, c->Ecx, c->Edx, c->Ebx, c->Esp, c->Ebp, c->Esi, c->Edi);
        for (U k = 0; k < 16; ++k) {
            U a = c->Esp + 4 * k;
            MEMORY_BASIC_INFORMATION mb;
            if (!VirtualQuery(reinterpret_cast<void*>(a), &mb, sizeof mb) || mb.State != MEM_COMMIT) break;
            fprintf(stderr, k ? " %08x" : "[430]   stack %08x", *reinterpret_cast<const U*>(a));
        }
        fprintf(stderr, "\n");
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
            if (p)
                add_import(reinterpret_cast<U>(p), reinterpret_cast<U>(iat), "%s!%s", dll,
                           (*names & 0x80000000u) ? "#ordinal" : fn);
        }
    }
    g_entries = static_cast<void (**)(Machine257&)>(
        VirtualAlloc(nullptr, (g_code_hi - g_code_lo) * sizeof(void*), MEM_COMMIT, PAGE_READWRITE));
    for (U i = 0; i < lowered_count430; ++i)
        g_entries[lowered_table430[i].va - g_code_lo] = lowered_table430[i].fn;
}

// Sampling profiler (PORSCHE430_PROFILE=<seconds>, PORSCHE430_PROFILE_OUT=<file>): samples
// the main thread's EIP every millisecond. Host-image samples are written as raw addresses
// (symbolized afterwards with the linker map); other samples are grouped by module.
DWORD WINAPI profile430(void* arg)
{
    const DWORD seconds = static_cast<DWORD>(reinterpret_cast<ULONG_PTR>(arg));
    if (const char* delay = getenv("PORSCHE430_PROFILE_DELAY"))
        Sleep(static_cast<DWORD>(atol(delay)) * 1000u);
    auto* own = reinterpret_cast<IMAGE_NT_HEADERS32*>(kBase + reinterpret_cast<IMAGE_DOS_HEADER*>(kBase)->e_lfanew);
    const U host_end = kBase + own->OptionalHeader.SizeOfImage;
    U* hits = static_cast<U*>(VirtualAlloc(nullptr, (host_end - kBase) / 4u * sizeof(U), MEM_COMMIT, PAGE_READWRITE));
    const U kMaxNative = 1u << 20;
    U* native = static_cast<U*>(VirtualAlloc(nullptr, kMaxNative * sizeof(U), MEM_COMMIT, PAGE_READWRITE));
    U total = 0, native_n = 0;
    static LONG reverse_before[1024];
    for (U k = 0; k < 1024; ++k) reverse_before[k] = g_reverse_counts[k].n;
    const DWORD end = GetTickCount() + seconds * 1000u;
    timeBeginPeriod(1);
    while (GetTickCount() < end) {
        Sleep(1);
        if (SuspendThread(g_main_thread) == static_cast<DWORD>(-1)) break;
        CONTEXT c;
        c.ContextFlags = CONTEXT_CONTROL;
        BOOL ok = GetThreadContext(g_main_thread, &c);
        ResumeThread(g_main_thread);
        if (!ok) continue;
        ++total;
        if (c.Eip >= kBase && c.Eip < host_end) ++hits[(c.Eip - kBase) / 4u];
        else if (native_n < kMaxNative) native[native_n++] = c.Eip;
    }
    timeEndPeriod(1);
    const char* path = getenv("PORSCHE430_PROFILE_OUT");
    FILE* out = fopen(path ? path : "profile430.txt", "w");
    if (!out) return 0;
    fprintf(out, "total %u\n", total);
    for (U k = 0; k < 1024; ++k)
        if (g_reverse_counts[k].n - reverse_before[k])
            fprintf(out, "reverse %08lx %ld\n", g_reverse_counts[k].va, g_reverse_counts[k].n - reverse_before[k]);
    for (U i = 0; i < (host_end - kBase) / 4u; ++i)
        if (hits[i]) fprintf(out, "host %08x %u\n", kBase + 4u * i, hits[i]);
    for (U i = 0; i < native_n; ++i) {
        HMODULE m = nullptr;
        char name[MAX_PATH] = "?";
        if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                               reinterpret_cast<LPCSTR>(static_cast<ULONG_PTR>(native[i])), &m) && m)
            GetModuleFileNameA(m, name, MAX_PATH);
        const char* base = strrchr(name, '\\');
        fprintf(out, "native %s %08x\n", base ? base + 1 : name, native[i]);
    }
    fclose(out);
    fprintf(stderr, "[430] profile: %u samples written\n", total);
    fflush(stderr);
    return 0;
}

DWORD WINAPI watchdog430(void*)
{
    for (;;) {
        Sleep(3000);
        Machine257* m = g_last;
        fprintf(stderr, "[430] watchdog pc=%08x native_calls=%u last_native=%08x\n", m ? m->pc : 0u,
                g_native_calls, g_last_native);
        fflush(stderr);
    }
}

void __cdecl run_guest(U guest_esp)
{
    Machine257 m;
    reset_machine(m);
    m.r[4] = guest_esp - 4u;
    write257(m.r[4], 4u, 0xfffffff0u);
    t_current = &m;
    g_last = &m;
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

// ---- native reference mode (PORSCHE430_NATIVE=1) --------------------------------------
// Runs the original machine code itself in the same image and environment, with every IAT
// entry routed through a logging trampoline, so its import trace can be diffed with the
// lowered build's trace line by line.
extern "C" void __cdecl import_hook_log430(U* slot)
{
    // slot[0]: import index (replaced by the real target), slot[1]: return address, args.
    ImportName& im = g_imports[slot[0]];
    slot[0] = im.address;
    if (g_trace_left <= 0) return;
    if (!im.traced) im.traced = trace_matches(im.name) ? 1 : -1;
    if (im.traced < 0) return;
    --g_trace_left;
    char line[512];
    int n = _snprintf(line, sizeof line - 32, "[430] +%lums t%lu %s from %08x:", GetTickCount() - g_t0,
                      GetCurrentThreadId(), im.name, slot[1]);
    for (U k = 2; k <= 5 && n > 0 && n < 480; ++k) n += format_arg(line + n, 480 - n, slot[k]);
    fprintf(stderr, "%s\n", line);
}

__declspec(naked) void import_hook_common430()
{
    __asm {
        pushad
        pushfd
        lea eax, [esp + 36]
        push eax
        call import_hook_log430
        add esp, 4
        popfd
        popad
        ret
    }
}

void run_native()
{
    // Code becomes executable again; IAT entries go through `push index; jmp common`.
    DWORD old = 0;
    VirtualProtect(reinterpret_cast<void*>(g_code_lo), g_code_hi - g_code_lo, PAGE_EXECUTE_READWRITE, &old);
    auto* stubs = static_cast<BYTE*>(VirtualAlloc(nullptr, g_import_count * 10u, MEM_COMMIT, PAGE_EXECUTE_READWRITE));
    auto* nt = reinterpret_cast<IMAGE_NT_HEADERS32*>(
        reinterpret_cast<BYTE*>(kBase) + reinterpret_cast<IMAGE_DOS_HEADER*>(kBase)->e_lfanew);
    (void)nt;
    for (U i = 0; i < g_import_count; ++i) {
        BYTE* p = stubs + 10u * i;
        p[0] = 0x68; *reinterpret_cast<U*>(p + 1) = i;
        p[5] = 0xe9;
        *reinterpret_cast<U*>(p + 6) = reinterpret_cast<U>(&import_hook_common430) - reinterpret_cast<U>(p + 10);
    }
    for (U i = 0; i < g_import_count; ++i)
        if (g_imports[i].iat_slot) *reinterpret_cast<U*>(g_imports[i].iat_slot) = reinterpret_cast<U>(stubs + 10u * i);
    reinterpret_cast<void (*)()>(g_entry_va)();
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
    g_t0 = GetTickCount();
    InitializeCriticalSection(&g_stub_lock);
    DuplicateHandle(GetCurrentProcess(), GetCurrentThread(), GetCurrentProcess(), &g_main_thread, 0, FALSE,
                    DUPLICATE_SAME_ACCESS);
    map_image(g_original_path);
    if (const char* p = getenv("PORSCHE430_PROFILE"))
        CreateThread(nullptr, 0, &profile430, reinterpret_cast<void*>(static_cast<ULONG_PTR>(atol(p))), 0, nullptr);
    AddVectoredExceptionHandler(1, &vectored430);
    if (const char* t = getenv("PORSCHE430_TRACE"))
        g_trace_left = atol(t);
    g_trace_filter = getenv("PORSCHE430_TRACE_FILTER");
    if (getenv("PORSCHE430_WATCHDOG"))
        CreateThread(nullptr, 0, &watchdog430, nullptr, 0, nullptr);
    if (getenv("PORSCHE430_NATIVE")) {
        fprintf(stderr, "[430] image mapped, NATIVE reference mode, entry %08x\n", g_entry_va);
        run_native();
        return 0;
    }
    fprintf(stderr, "[430] image mapped, %u lowered bodies, entry %08x\n", lowered_count430, g_entry_va);
    char* side = static_cast<char*>(VirtualAlloc(nullptr, 64u << 20, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE));
    switch_to_side(reinterpret_cast<U>(side) + (64u << 20) - 64u, &run_guest);
    return 0;
}

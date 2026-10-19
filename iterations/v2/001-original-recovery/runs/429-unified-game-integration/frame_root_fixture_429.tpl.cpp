// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Run 429 differential fixture TEMPLATE for the corrected frame root lifecycle
// (00471b70, 00471c40). experiment-v2-frame-root-429.py fills in the original
// bytes, the operand sites and the original .rdata strings from the PE, so no
// game bytes are versioned here. The real frame_root_block_429.obj is linked:
// the original code and the C++ both write the same 00628940..00628a64 block.
// Not part of the game graph.
#include <cstdarg>
#include <cstdint>

#include "frame_root_lifecycle_419.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_heap_init.hpp"
#include "porsche/formatter_entry.hpp"
#include "porsche/formatter_stdio.hpp"

using U = std::uint32_t;
extern "C" void* __stdcall VirtualAlloc(void*, U, U, U);
extern "C" void __stdcall ExitProcess(U);
extern "C" void* __stdcall GetStdHandle(U);
extern "C" int __stdcall WriteFile(void*, const void*, U, U*, void*);
extern "C" int _fltused = 0;   // no CRT in the fixture; the float-returning callee needs it

namespace {

const std::uint8_t kInit[/*@INIT_SIZE@*/] = { /*@INIT_BYTES@*/ };
const std::uint8_t kTeardown[/*@TEARDOWN_SIZE@*/] = { /*@TEARDOWN_BYTES@*/ };
struct Site { U body; U offset; U rel32; U target; };
const Site kSites[] = {
/*@SITES@*/
};
// Original string literals (in .data) referenced by the bodies (VA, text).
struct OriginalString { U va; const char* text; };
const OriginalString kStrings[] = {
/*@STRINGS@*/
};

U g_failures = 0;
void put(const char* s) { U n = 0, w = 0; while (s[n]) ++n; WriteFile(GetStdHandle(static_cast<U>(-11)), s, n, &w, nullptr); }
void check(bool ok, const char* what) { put(what); put(ok ? " OK\n" : " FAIL\n"); if (!ok) ++g_failures; }

U fnv(const char* s) { U h = 2166136261u; while (*s) { h ^= static_cast<std::uint8_t>(*s++); h *= 16777619u; } return h; }

struct Event { U kind, a, b, c; };
struct Trace { U count; Event ev[32]; } g_trace;
void rec(U kind, U a = 0, U b = 0, U c = 0) { if (g_trace.count < 32u) g_trace.ev[g_trace.count++] = Event{kind, a, b, c}; }

// Mock state.
std::uint8_t g_root_object[0x3c];
U g_alloc_null = 0;
std::uint8_t g_load_ok = 1;
U g_bworld_fields[16];

} // namespace

// ---- Unrecovered externals the bodies read (same objects for both paths) ----
extern "C" {
char g_track_source_name_00657444[64];
const char* g_path_prefix_0065b2b8 = "gamedata\\tracks\\";
void* g_bworld_context_00628bc0 = g_bworld_fields;
void __cdecl error_log_0059fd90(const char* format, const char* name) { rec(14, fnv(format), fnv(name)); }
float __cdecl bworld_init_subsystem_005323a0(void* p1, void* p2) {
    rec(15, reinterpret_cast<U>(p1), reinterpret_cast<U>(p2));
    return 1.5f;   // leaves a value in ST0, as the original callee does
}
}

namespace porsche {
char application_object_heap_name_005e8e50[32] = ".crk";
void* __cdecl startup_network_allocate_0059ef90(std::uint32_t bytes) {
    rec(10, bytes);
    return g_alloc_null ? nullptr : g_root_object;
}
std::uint32_t __cdecl application_release_0059f050(void* address) { rec(18, reinterpret_cast<U>(address)); return 0; }
std::int32_t __cdecl formatter_entry_005a0fbf(char* output, const char* format, ...) {
    va_list ap;
    va_start(ap, format);
    const char* a = va_arg(ap, const char*);
    const char* b = va_arg(ap, const char*);
    const char* c = va_arg(ap, const char*);
    va_end(ap);
    rec(12, reinterpret_cast<U>(output), fnv(format), reinterpret_cast<U>(b));
    char* d = output;
    const char* parts[3] = {a, b, c};
    for (U i = 0; i < 3; ++i) for (const char* s = parts[i]; *s; ) *d++ = *s++;
    *d = 0;
    return static_cast<std::int32_t>(d - output);
}
int __cdecl formatter_stdio_printf_005a177b(const char* format, ...) { rec(16, fnv(format)); return 0; }
void* __thiscall FrameServiceObjectProxy::construct_004874a0() { rec(11, reinterpret_cast<U>(this)); return this; }
std::uint8_t __thiscall FrameServiceObjectProxy::load_track_004876e0(const char* path) {
    rec(13, reinterpret_cast<U>(this), reinterpret_cast<U>(path), fnv(path));
    return g_load_ok;
}
void __thiscall FrameServiceObjectProxy::destruct_00487590() { rec(17, reinterpret_cast<U>(this)); }
} // namespace porsche

namespace {

template <class M> U member_address(M m) { union { M m; U u; } x; x.m = m; return x.u; }

U resolve(U va) {
    using namespace porsche;
    switch (va) {
    case 0x00657444u: return reinterpret_cast<U>(g_track_source_name_00657444);
    case 0x00628940u: return reinterpret_cast<U>(g_frame_root_track_name_00628940);
    case 0x00628960u: return reinterpret_cast<U>(&frame_service_root_00628960);
    case 0x00628964u: return reinterpret_cast<U>(g_frame_root_formatted_path_00628964);
    case 0x0065b2b8u: return reinterpret_cast<U>(&g_path_prefix_0065b2b8);
    case 0x005e8e50u: return reinterpret_cast<U>(application_object_heap_name_005e8e50);
    case 0x00628bc0u: return reinterpret_cast<U>(&g_bworld_context_00628bc0);
    case 0x0059ef90u: return reinterpret_cast<U>(&startup_network_allocate_0059ef90);
    case 0x004874a0u: return member_address(&FrameServiceObjectProxy::construct_004874a0);
    case 0x005a0fbfu: return reinterpret_cast<U>(static_cast<std::int32_t(__cdecl*)(char*, const char*, ...)>(&formatter_entry_005a0fbf));
    case 0x004876e0u: return member_address(&FrameServiceObjectProxy::load_track_004876e0);
    case 0x0059fd90u: return reinterpret_cast<U>(&error_log_0059fd90);
    case 0x005323a0u: return reinterpret_cast<U>(&bworld_init_subsystem_005323a0);
    case 0x005a177bu: return reinterpret_cast<U>(&formatter_stdio_printf_005a177b);
    case 0x00487590u: return member_address(&FrameServiceObjectProxy::destruct_00487590);
    case 0x0059f050u: return reinterpret_cast<U>(&application_release_0059f050);
    }
    for (const auto& s : kStrings) if (s.va == va) return reinterpret_cast<U>(s.text);
    ++g_failures;
    put("unresolved operand\n");
    return 0;
}

std::uint8_t* g_slab[2];

void load_slabs() {
    const std::uint8_t* src[2] = {kInit, kTeardown};
    const U size[2] = {sizeof(kInit), sizeof(kTeardown)};
    for (U b = 0; b < 2; ++b) {
        g_slab[b] = static_cast<std::uint8_t*>(VirtualAlloc(nullptr, 4096, 0x3000, 0x40));
        for (U i = 0; i < size[b]; ++i) g_slab[b][i] = src[b][i];
    }
    for (const auto& s : kSites) {
        std::uint8_t* at = g_slab[s.body] + s.offset;
        U v = resolve(s.target);
        if (s.rel32) v -= reinterpret_cast<U>(at + 4);
        for (U k = 0; k < 4; ++k) at[k] = static_cast<std::uint8_t>(v >> (8 * k));
    }
}

U g_target, g_sp, g_bp, g_bx, g_si, g_di, g_seen_sp, g_entry_sp, g_seen_bx, g_seen_si, g_seen_di, g_seen_bp;
unsigned short g_fpu_status;
__declspec(naked) void invoke() {
    __asm {
        mov g_sp, esp
        mov g_bp, ebp
        mov g_bx, ebx
        mov g_si, esi
        mov g_di, edi
        mov ebx, 2468ace0h
        mov esi, 89abcdefh
        mov edi, 0fedcba98h
        mov ebp, 13579bdfh
        fninit
        mov eax, esp
        sub eax, 4
        mov g_entry_sp, eax
        cld
        call dword ptr g_target
        mov g_seen_sp, esp
        mov g_seen_bx, ebx
        mov g_seen_si, esi
        mov g_seen_di, edi
        mov g_seen_bp, ebp
        fnstsw g_fpu_status
        fninit
        mov esp, g_sp
        mov ebp, g_bp
        mov ebx, g_bx
        mov esi, g_si
        mov edi, g_di
        ret
    }
}

struct Snapshot {
    Trace trace;
    std::uint8_t block[0x124];
    U fpu_top;
    bool abi_ok;
};

void run(U target, Snapshot& s) {
    g_trace.count = 0;
    g_target = target;
    invoke();
    s.trace = g_trace;
    const std::uint8_t* blk = reinterpret_cast<const std::uint8_t*>(porsche::g_frame_root_track_name_00628940);
    for (U i = 0; i < sizeof(s.block); ++i) s.block[i] = blk[i];
    s.fpu_top = (g_fpu_status >> 11) & 7u;
    s.abi_ok = g_seen_sp == g_entry_sp + 4 && g_seen_bx == 0x2468ace0u && g_seen_si == 0x89abcdefu &&
               g_seen_di == 0xfedcba98u && g_seen_bp == 0x13579bdfu;
}

void setup(const char* track, U alloc_null, std::uint8_t load_ok, U root, U field0, U field3) {
    std::uint8_t* blk = reinterpret_cast<std::uint8_t*>(porsche::g_frame_root_track_name_00628940);
    for (U i = 0; i < 0x124; ++i) blk[i] = static_cast<std::uint8_t>(0xa5 ^ i);
    U n = 0;
    for (; track[n]; ++n) g_track_source_name_00657444[n] = track[n];
    g_track_source_name_00657444[n] = 0;
    porsche::frame_service_root_00628960 = root;
    g_alloc_null = alloc_null;
    g_load_ok = load_ok;
    g_bworld_fields[0] = field0;
    g_bworld_fields[3] = field3;
}

bool same(const Snapshot& a, const Snapshot& b) {
    const std::uint8_t* pa = reinterpret_cast<const std::uint8_t*>(&a);
    const std::uint8_t* pb = reinterpret_cast<const std::uint8_t*>(&b);
    for (U i = 0; i < sizeof(Snapshot); ++i) if (pa[i] != pb[i]) return false;
    return a.abi_ok;
}

Snapshot g_orig, g_cpp;

void differential(const char* name, U body, const char* track, U alloc_null, std::uint8_t load_ok, U root, U f0, U f3) {
    for (U i = 0; i < sizeof(Snapshot); ++i) { reinterpret_cast<std::uint8_t*>(&g_orig)[i] = 0; reinterpret_cast<std::uint8_t*>(&g_cpp)[i] = 0; }
    setup(track, alloc_null, load_ok, root, f0, f3);
    run(reinterpret_cast<U>(g_slab[body]), g_orig);
    setup(track, alloc_null, load_ok, root, f0, f3);
    run(body == 0 ? reinterpret_cast<U>(&porsche::frame_root_init_00471b70)
                  : reinterpret_cast<U>(&porsche::frame_root_teardown_00471c40), g_cpp);
    check(same(g_orig, g_cpp), name);
}

} // namespace

extern "C" void __cdecl entry() {
    using porsche::g_frame_root_track_name_00628940;
    // Layout of the linked block: root 32 bytes after the name, path 4 after the root.
    const char* name = g_frame_root_track_name_00628940;
    check(reinterpret_cast<const char*>(&porsche::frame_service_root_00628960) - name == 32, "root at name+32");
    check(porsche::g_frame_root_formatted_path_00628964 - name == 36, "path at name+36");
    load_slabs();
    differential("init load ok", 0, "corsica", 0, 1, 0, 2, 0x100);
    differential("init load fails", 0, "unknown_trk", 0, 0, 0, 1, 0x80);
    differential("init alloc fails", 0, "monaco", 1, 1, 0x11112222u, 3, 0x40);
    differential("init 31-char name", 0, "1234567890123456789012345678901", 0, 1, 0, 3, 0x140);
    differential("init 40-char name reaches root and path", 0, "AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDD", 0, 1, 0, 5, 0x200);
    differential("teardown with root", 1, "x", 0, 1, 0x00c0ffeeu, 0, 0);
    differential("teardown without root", 1, "x", 0, 1, 0, 0, 0);
    put(g_failures ? "RESULT FAIL\n" : "RESULT PASS\n");
    ExitProcess(g_failures ? 1u : 0u);
}

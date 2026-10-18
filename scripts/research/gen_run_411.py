"""Generate complete Run 411 fixture and experiment files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIXTURE_CPP = r"""#include "app_main_ui_screen_handlers_411.hpp"
#include <windows.h>
#include <cstdint>
#include <cstddef>

extern "C" int _fltused = 0x9876;
#pragma function(memcpy, memset)
extern "C" void* memcpy(void* dst, const void* src, size_t count) {
    auto d = static_cast<unsigned char*>(dst);
    auto s = static_cast<const unsigned char*>(src);
    for (size_t i = 0; i < count; ++i) d[i] = s[i];
    return dst;
}
extern "C" void* memset(void* dst, int val, size_t count) {
    auto d = static_cast<unsigned char*>(dst);
    for (size_t i = 0; i < count; ++i) d[i] = static_cast<unsigned char>(val);
    return dst;
}

namespace porsche {

using U = std::uint32_t;

struct CallTrace {
    U count;
    U tag[512];
    U arg1[512];
    U arg2[512];
    U arg3[512];
    void* this_ptr[512];
};

static CallTrace g_trace;
static CallTrace s_trace_orig;
static CallTrace s_trace_cpp;

static void record_call(U tag, void* self = nullptr, U a1 = 0, U a2 = 0, U a3 = 0) {
    if (g_trace.count < 512) {
        g_trace.tag[g_trace.count] = tag;
        g_trace.this_ptr[g_trace.count] = self;
        g_trace.arg1[g_trace.count] = a1;
        g_trace.arg2[g_trace.count] = a2;
        g_trace.arg3[g_trace.count] = a3;
        g_trace.count++;
    }
}

static std::uint8_t s_mem_pool[65536];
static std::size_t s_mem_pos = 0;

static void* mock_alloc(std::size_t sz) {
    sz = (sz + 7) & ~static_cast<std::size_t>(7);
    if (s_mem_pos + sz > sizeof(s_mem_pool)) {
        s_mem_pos = 0;
    }
    void* p = &s_mem_pool[s_mem_pos];
    s_mem_pos += sz;
    memset(p, 0, sz);
    return p;
}

static U s_mock_timer_val = 12345;
static U CALL_STDCALL mock_timer_query() {
    record_call(0x5b2080);
    return s_mock_timer_val;
}

// Direct C hooks invoked by C++ recovered implementation
extern "C" {
    void hook_0048c870(void* self, U a1, U a2, U a3, U a4, U a5) {
        (void)a4; (void)a5;
        record_call(0x48c870, self, a1, a2, a3);
    }
    void CALL_CDECL sub_0048da60(std::int32_t a1, std::int32_t a2) {
        record_call(0x48da60, nullptr, static_cast<U>(a1), static_cast<U>(a2));
    }
    void hook_0048d350(void* self, U a1, std::int32_t a2, std::int32_t a3, U a4) {
        (void)a4;
        record_call(0x48d350, self, a1, static_cast<U>(a2), static_cast<U>(a3));
    }
    void hook_0048dbe0(void* self) {
        record_call(0x48dbe0, self);
    }
    void hook_0048e9c0(void* self) {
        record_call(0x48e9c0, self);
    }
    void hook_0048dbb0(void* self) {
        record_call(0x48dbb0, self);
    }
    void hook_0048aa10(void* self, U a1, void* a2, void* a3, const char* a4, void* a5, const char* a6, void* a7, U a8) {
        (void)a4; (void)a5; (void)a6; (void)a7; (void)a8;
        record_call(0x48aa10, self, a1, reinterpret_cast<U>(a2), reinterpret_cast<U>(a3));
    }
    void hook_00491cd0(void* self, U a1, void* a2, void* a3, U a4, U a5, std::int32_t a6) {
        (void)a4; (void)a5; (void)a6;
        record_call(0x491cd0, self, a1, reinterpret_cast<U>(a2), reinterpret_cast<U>(a3));
    }
    void* hook_004931c0(void* self, void* a1) {
        record_call(0x4931c0, self, reinterpret_cast<U>(a1));
        return self;
    }
    void hook_0048ac70(void* self, void* a1) {
        record_call(0x48ac70, self, reinterpret_cast<U>(a1));
    }
    void hook_0048ac50(void* self) {
        record_call(0x48ac50, self);
    }
    void hook_0048ac90(void* self, void* a1, U a2) {
        record_call(0x48ac90, self, reinterpret_cast<U>(a1), a2);
    }
    void hook_0048c840(void* self, U a1, U a2) {
        record_call(0x48c840, self, a1, a2);
    }
    void* hook_00529050(void* self, void* a1) {
        record_call(0x529050, self, reinterpret_cast<U>(a1));
        return self;
    }
    void hook_0050e140(void* self, void* a1) {
        record_call(0x50e140, self, reinterpret_cast<U>(a1));
    }
    void hook_004937f0(void* self, void* a1) {
        record_call(0x4937f0, self, reinterpret_cast<U>(a1));
    }

    void CALL_CDECL sub_0055ec50(U a1, const char* str) {
        U h = 0;
        if (str) {
            for (const char* p = str; *p; ++p) h = h * 31 + static_cast<std::uint8_t>(*p);
        }
        record_call(0x55ec50, nullptr, a1, h);
    }
    void CALL_CDECL sub_004a4a70(std::int32_t a1) {
        record_call(0x4a4a70, nullptr, static_cast<U>(a1));
    }
    static U s_mock_key = 0;
    U CALL_CDECL sub_0055ff60() {
        record_call(0x55ff60);
        return s_mock_key;
    }
    void CALL_CDECL sub_0055f740(U a1) {
        record_call(0x55f740, nullptr, a1);
    }
    void CALL_CDECL sub_005366e0(U a1) {
        record_call(0x5366e0, nullptr, a1);
    }
    void CALL_CDECL sub_005322b0(void* a1) {
        record_call(0x5322b0, nullptr, reinterpret_cast<U>(a1));
    }
    void CALL_CDECL sub_005322c0(void* a1) {
        record_call(0x5322c0, nullptr, reinterpret_cast<U>(a1));
    }
    U CALL_CDECL sub_0055eb70(U a1) {
        record_call(0x55eb70, nullptr, a1);
        return 1;
    }
    void* CALL_CDECL sub_0053c290(void* dst, int val, std::size_t sz) {
        record_call(0x53c290, nullptr, reinterpret_cast<U>(dst), static_cast<U>(val), static_cast<U>(sz));
        return memset(dst, val, sz);
    }
    char* CALL_CDECL sub_005a28a0(char* dst, const char* src, std::size_t sz) {
        record_call(0x5a28a0, nullptr, reinterpret_cast<U>(dst), reinterpret_cast<U>(src), static_cast<U>(sz));
        if (sz > 0) {
            std::size_t i = 0;
            for (; i < sz && src[i]; ++i) dst[i] = src[i];
            for (; i < sz; ++i) dst[i] = 0;
        }
        return dst;
    }
    void* CALL_CDECL sub_005323e0(void* dst, const void* src, std::size_t sz) {
        record_call(0x5323e0, nullptr, reinterpret_cast<U>(dst), reinterpret_cast<U>(src), static_cast<U>(sz));
        return memcpy(dst, src, sz);
    }
    U CALL_CDECL sub_0055aaa0(U a1, U a2, U a3, void* a4, U a5, U a6, U a7) {
        record_call(0x55aaa0, nullptr, a1, a2, a3);
        (void)a4; (void)a5; (void)a6; (void)a7;
        return 42;
    }
    void CALL_CDECL sub_0055bfd0(U a1) {
        record_call(0x55bfd0, nullptr, a1);
    }
    void CALL_CDECL sub_0048c4d0() {
        record_call(0x48c4d0);
    }
    void* CALL_CDECL sub_0059ef90(std::size_t sz) {
        record_call(0x59ef90, nullptr, static_cast<U>(sz));
        return mock_alloc(sz);
    }
    U CALL_CDECL sub_0048a9a0() {
        record_call(0x48a9a0);
        return 4;
    }
    void CALL_CDECL sub_00560140(void* a1) {
        record_call(0x560140, nullptr, reinterpret_cast<U>(a1));
    }
}

// Naked thiscall thunks for physical slab execution of PE code
extern "C" {
    __declspec(naked) void thunk_0048c870() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x18]
            push [ebp + 0x14]
            push [ebp + 0x10]
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_0048c870
            add esp, 24
            pop ebp
            ret 20
        }
    }
    __declspec(naked) void thunk_0048d350() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x14]
            push [ebp + 0x10]
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_0048d350
            add esp, 20
            pop ebp
            ret 16
        }
    }
    __declspec(naked) void thunk_0048dbe0() {
        __asm {
            push ecx
            call hook_0048dbe0
            add esp, 4
            ret
        }
    }
    __declspec(naked) void thunk_0048e9c0() {
        __asm {
            push ecx
            call hook_0048e9c0
            add esp, 4
            ret
        }
    }
    __declspec(naked) void thunk_0048dbb0() {
        __asm {
            push ecx
            call hook_0048dbb0
            add esp, 4
            ret
        }
    }
    __declspec(naked) void thunk_0048aa10() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x24]
            push [ebp + 0x20]
            push [ebp + 0x1c]
            push [ebp + 0x18]
            push [ebp + 0x14]
            push [ebp + 0x10]
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_0048aa10
            add esp, 36
            pop ebp
            ret 32
        }
    }
    __declspec(naked) void thunk_00491cd0() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x1c]
            push [ebp + 0x18]
            push [ebp + 0x14]
            push [ebp + 0x10]
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_00491cd0
            add esp, 28
            pop ebp
            ret 24
        }
    }
    __declspec(naked) void thunk_004931c0() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x08]
            push ecx
            call hook_004931c0
            add esp, 8
            mov eax, ecx
            pop ebp
            ret 4
        }
    }
    __declspec(naked) void thunk_0048ac70() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x08]
            push ecx
            call hook_0048ac70
            add esp, 8
            pop ebp
            ret 4
        }
    }
    __declspec(naked) void thunk_0048ac50() {
        __asm {
            push ecx
            call hook_0048ac50
            add esp, 4
            ret
        }
    }
    __declspec(naked) void thunk_0048ac90() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_0048ac90
            add esp, 12
            pop ebp
            ret 8
        }
    }
    __declspec(naked) void thunk_0048c840() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x0c]
            push [ebp + 0x08]
            push ecx
            call hook_0048c840
            add esp, 12
            pop ebp
            ret 8
        }
    }
    __declspec(naked) void thunk_00529050() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x08]
            push ecx
            call hook_00529050
            add esp, 8
            mov eax, ecx
            pop ebp
            ret 4
        }
    }
    __declspec(naked) void thunk_0050e140() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x08]
            push ecx
            call hook_0050e140
            add esp, 8
            pop ebp
            ret 4
        }
    }
    __declspec(naked) void thunk_004937f0() {
        __asm {
            push ebp
            mov ebp, esp
            push [ebp + 0x08]
            push ecx
            call hook_004937f0
            add esp, 8
            pop ebp
            ret 12
        }
    }
}

static std::uint8_t* s_slab = nullptr;

static std::uint8_t call_orig_draw_screen_tree(UiScreenContext* self) {
    U pfn = reinterpret_cast<U>(s_slab + 0x0000);
    U res = 0;
    __asm {
        mov ecx, self
        call pfn
        movzx eax, al
        mov res, eax
    }
    return static_cast<std::uint8_t>(res);
}

static void call_orig_screen_refresh(UiScreenContext* self, const char* title, U param2) {
    U pfn = reinterpret_cast<U>(s_slab + 0x0600);
    __asm {
        push param2
        push title
        mov ecx, self
        call pfn
    }
}

static void call_orig_screen_render_present(UiScreenContext* self, U mode, U id, const char* title) {
    U pfn = reinterpret_cast<U>(s_slab + 0x0c00);
    __asm {
        push title
        push id
        push mode
        mov ecx, self
        call pfn
    }
}

static void patch_rel_call(std::uint8_t* call_ins_addr, void* target_fn) {
    auto rel = static_cast<std::int32_t>(reinterpret_cast<std::uintptr_t>(target_fn) - (reinterpret_cast<std::uintptr_t>(call_ins_addr) + 5));
    *reinterpret_cast<std::int32_t*>(call_ins_addr + 1) = rel;
}

static const char* const s_str_high1 = "Wait to go high1\n";
static const char* const s_str_high2 = "Wait to go high2\n";
static const char* const s_str_low1  = "Wait to go low1\n";
static const char* const s_str_low2  = "Wait to go low2\n";
static const char* const s_str_abort = "Abort\n";
static const char* const s_str_nfsnet = "NfsNet";
static const char* const s_str_game   = "Game";
static const char* const s_str_tilde  = "~";
static const char* const s_str_00     = "0.0";
static const char* const s_str_c      = "c";

static bool init_slab() {
    HANDLE hFile = CreateFileA("Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        hFile = CreateFileA("../../game/Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    }
    if (hFile == INVALID_HANDLE_VALUE) {
        hFile = CreateFileA("D:\\projetos\\prsche-disasm\\local\\game\\Porsche.exe", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    }
    if (hFile == INVALID_HANDLE_VALUE) return false;

    DWORD size = GetFileSize(hFile, NULL);
    auto pe_buf = static_cast<std::uint8_t*>(VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    if (!pe_buf) { CloseHandle(hFile); return false; }

    DWORD read = 0;
    ReadFile(hFile, pe_buf, size, &read, NULL);
    CloseHandle(hFile);

    s_slab = static_cast<std::uint8_t*>(VirtualAlloc(NULL, 16384, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
    if (!s_slab) return false;

    std::uint8_t* p_48cdf0 = s_slab + 0x0000;
    std::uint8_t* p_48dcb0 = s_slab + 0x0600;
    std::uint8_t* p_48e1a0 = s_slab + 0x0c00;

    memcpy(p_48cdf0, pe_buf + (0x0048cdf0 - 0x400000), 1364);
    memcpy(p_48dcb0, pe_buf + (0x0048dcb0 - 0x400000), 1250);
    memcpy(p_48e1a0, pe_buf + (0x0048e1a0 - 0x400000), 1357);

    VirtualFree(pe_buf, 0, MEM_RELEASE);

    // Patch function 1: 0048cdf0
    const U r_48cdf0_node[] = {
        0x1, 0x3d, 0xc2, 0x112, 0x123, 0x13c, 0x175, 0x1f7,
        0x230, 0x240, 0x259, 0x28f, 0x30e, 0x35f, 0x36c, 0x377,
        0x3a5, 0x3c0, 0x3dd, 0x416, 0x497, 0x4e0, 0x4ec, 0x4f7,
        0x519, 0x534
    };
    for (U off : r_48cdf0_node) {
        *reinterpret_cast<void**>(p_48cdf0 + off) = &g_ui_screen_node_00628c70;
    }
    *reinterpret_cast<const char**>(p_48cdf0 + 0x27) = s_str_high1;
    *reinterpret_cast<const char**>(p_48cdf0 + 0xb6) = s_str_abort;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x15f) = s_str_high2;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x1eb) = s_str_abort;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x279) = s_str_low1;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x302) = s_str_abort;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x400) = s_str_low2;
    *reinterpret_cast<const char**>(p_48cdf0 + 0x48b) = s_str_abort;

    patch_rel_call(p_48cdf0 + 0x21, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48cdf0 + 0x2d, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x37, reinterpret_cast<void*>(sub_004a4a70));
    patch_rel_call(p_48cdf0 + 0x7f, reinterpret_cast<void*>(sub_0055ff60));
    patch_rel_call(p_48cdf0 + 0x8b, reinterpret_cast<void*>(sub_0055f740));
    patch_rel_call(p_48cdf0 + 0x91, reinterpret_cast<void*>(sub_005366e0));
    patch_rel_call(p_48cdf0 + 0xbc, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x12d, reinterpret_cast<void*>(sub_0048da60));

    patch_rel_call(p_48cdf0 + 0x159, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48cdf0 + 0x165, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x16f, reinterpret_cast<void*>(sub_004a4a70));
    patch_rel_call(p_48cdf0 + 0x1b7, reinterpret_cast<void*>(sub_0055ff60));
    patch_rel_call(p_48cdf0 + 0x1c3, reinterpret_cast<void*>(sub_0055f740));
    patch_rel_call(p_48cdf0 + 0x1c9, reinterpret_cast<void*>(sub_005366e0));
    patch_rel_call(p_48cdf0 + 0x1f1, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x24a, reinterpret_cast<void*>(sub_0048da60));

    patch_rel_call(p_48cdf0 + 0x273, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48cdf0 + 0x27f, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x289, reinterpret_cast<void*>(sub_004a4a70));
    patch_rel_call(p_48cdf0 + 0x2d1, reinterpret_cast<void*>(sub_0055ff60));
    patch_rel_call(p_48cdf0 + 0x2dd, reinterpret_cast<void*>(sub_0055f740));
    patch_rel_call(p_48cdf0 + 0x2e3, reinterpret_cast<void*>(sub_005366e0));
    patch_rel_call(p_48cdf0 + 0x308, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x39e, reinterpret_cast<void*>(sub_005322b0));
    patch_rel_call(p_48cdf0 + 0x3b9, reinterpret_cast<void*>(thunk_0048d350));
    patch_rel_call(p_48cdf0 + 0x3ce, reinterpret_cast<void*>(sub_005322c0));

    patch_rel_call(p_48cdf0 + 0x3fa, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48cdf0 + 0x406, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x410, reinterpret_cast<void*>(sub_004a4a70));
    patch_rel_call(p_48cdf0 + 0x458, reinterpret_cast<void*>(sub_0055ff60));
    patch_rel_call(p_48cdf0 + 0x464, reinterpret_cast<void*>(sub_0055f740));
    patch_rel_call(p_48cdf0 + 0x46a, reinterpret_cast<void*>(sub_005366e0));
    patch_rel_call(p_48cdf0 + 0x491, reinterpret_cast<void*>(sub_0055ec50));
    patch_rel_call(p_48cdf0 + 0x512, reinterpret_cast<void*>(sub_005322b0));
    patch_rel_call(p_48cdf0 + 0x52e, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48cdf0 + 0x542, reinterpret_cast<void*>(sub_005322c0));

    // Patch function 2: 0048dcb0
    const U r_48dcb0_node[] = { 0xe, 0x105, 0x13f, 0x1eb, 0x20b, 0x3af };
    for (U off : r_48dcb0_node) {
        *reinterpret_cast<void**>(p_48dcb0 + off) = &g_ui_screen_node_00628c70;
    }
    *reinterpret_cast<const char**>(p_48dcb0 + 0x7b) = s_str_nfsnet;
    *reinterpret_cast<const char**>(p_48dcb0 + 0xba) = s_str_game;
    *reinterpret_cast<const char**>(p_48dcb0 + 0xde) = s_str_tilde;
    *reinterpret_cast<const char**>(p_48dcb0 + 0x118) = s_str_00;
    *reinterpret_cast<std::uint8_t**>(p_48dcb0 + 0x2d0) = &g_byte_005d0728;
    *reinterpret_cast<std::uint8_t**>(p_48dcb0 + 0x2e6) = &g_byte_005d0728;
    *reinterpret_cast<const char**>(p_48dcb0 + 0x2fe) = s_str_nfsnet;
    *reinterpret_cast<U**>(p_48dcb0 + 0x342) = &g_dword_005b4980;
    *reinterpret_cast<U**>(p_48dcb0 + 0x348) = &g_dword_00508e70;
    *reinterpret_cast<U**>(p_48dcb0 + 0x366) = &g_dword_005b4990;
    *reinterpret_cast<const char**>(p_48dcb0 + 0x3bb) = s_str_00;
    *reinterpret_cast<void**>(p_48dcb0 + 0x3c1) = reinterpret_cast<void*>(0x005e8e50);
    *reinterpret_cast<const char**>(p_48dcb0 + 0x3ce) = s_str_c;
    *reinterpret_cast<void**>(p_48dcb0 + 0x3d4) = reinterpret_cast<void*>(0x0048f040);
    *reinterpret_cast<void**>(p_48dcb0 + 0x447) = reinterpret_cast<void*>(0x0048ee90);
    *reinterpret_cast<U**>(p_48dcb0 + 0x45e) = &g_dword_00628c74;
    *reinterpret_cast<U**>(p_48dcb0 + 0x49b) = &g_dword_00657aa4;

    patch_rel_call(p_48dcb0 + 0x45, reinterpret_cast<void*>(sub_0055eb70));
    patch_rel_call(p_48dcb0 + 0x57, reinterpret_cast<void*>(thunk_0048dbe0));
    patch_rel_call(p_48dcb0 + 0x6f, reinterpret_cast<void*>(sub_0053c290));
    patch_rel_call(p_48dcb0 + 0x80, reinterpret_cast<void*>(sub_005a28a0));
    patch_rel_call(p_48dcb0 + 0x9f, reinterpret_cast<void*>(sub_005323e0));
    patch_rel_call(p_48dcb0 + 0x184, reinterpret_cast<void*>(sub_0053c290));
    patch_rel_call(p_48dcb0 + 0x195, reinterpret_cast<void*>(sub_005323e0));
    patch_rel_call(p_48dcb0 + 0x1e4, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48dcb0 + 0x1f6, reinterpret_cast<void*>(p_48e1a0));
    patch_rel_call(p_48dcb0 + 0x204, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48dcb0 + 0x217, reinterpret_cast<void*>(p_48e1a0));
    patch_rel_call(p_48dcb0 + 0x22a, reinterpret_cast<void*>(thunk_0048dbb0));
    patch_rel_call(p_48dcb0 + 0x243, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48dcb0 + 0x24a, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48dcb0 + 0x270, reinterpret_cast<void*>(sub_0053c290));
    patch_rel_call(p_48dcb0 + 0x281, reinterpret_cast<void*>(sub_005323e0));
    patch_rel_call(p_48dcb0 + 0x2ea, reinterpret_cast<void*>(sub_0053c290));
    patch_rel_call(p_48dcb0 + 0x32d, reinterpret_cast<void*>(sub_005323e0));
    patch_rel_call(p_48dcb0 + 0x34c, reinterpret_cast<void*>(sub_0055aaa0));
    patch_rel_call(p_48dcb0 + 0x352, reinterpret_cast<void*>(sub_0055bfd0));
    patch_rel_call(p_48dcb0 + 0x389, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48dcb0 + 0x393, reinterpret_cast<void*>(sub_0048c4d0));
    patch_rel_call(p_48dcb0 + 0x3a1, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48dcb0 + 0x3dc, reinterpret_cast<void*>(thunk_0048aa10));
    patch_rel_call(p_48dcb0 + 0x3ea, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48dcb0 + 0x43e, reinterpret_cast<void*>(sub_0048a9a0));
    patch_rel_call(p_48dcb0 + 0x44e, reinterpret_cast<void*>(sub_00560140));
    patch_rel_call(p_48dcb0 + 0x46e, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48dcb0 + 0x48e, reinterpret_cast<void*>(thunk_00491cd0));
    patch_rel_call(p_48dcb0 + 0x4ad, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48dcb0 + 0x4bf, reinterpret_cast<void*>(thunk_004931c0));

    // Patch function 3: 0048e1a0
    const U r_48e1a0_node[] = { 0x2, 0xe1, 0x1c6, 0x27f, 0x45c };
    for (U off : r_48e1a0_node) {
        *reinterpret_cast<void**>(p_48e1a0 + off) = &g_ui_screen_node_00628c70;
    }
    *reinterpret_cast<const char**>(p_48e1a0 + 0xef) = s_str_00;
    *reinterpret_cast<void**>(p_48e1a0 + 0xf7) = reinterpret_cast<void*>(0x005e8e50);
    *reinterpret_cast<const char**>(p_48e1a0 + 0x104) = s_str_c;
    *reinterpret_cast<void**>(p_48e1a0 + 0x10a) = reinterpret_cast<void*>(0x0048f040);
    *reinterpret_cast<void**>(p_48e1a0 + 0x171) = reinterpret_cast<void*>(0x0048ee90);
    *reinterpret_cast<void**>(p_48e1a0 + 0x194) = &g_pfn_005b2080;
    *reinterpret_cast<U**>(p_48e1a0 + 0x215) = &g_dword_00657aa4;
    *reinterpret_cast<const char**>(p_48e1a0 + 0x28d) = s_str_00;
    *reinterpret_cast<void**>(p_48e1a0 + 0x2aa) = reinterpret_cast<void*>(0x0048f040);
    *reinterpret_cast<void**>(p_48e1a0 + 0x30d) = reinterpret_cast<void*>(0x0048ee90);
    *reinterpret_cast<U**>(p_48e1a0 + 0x32e) = &g_dword_005b4990;
    *reinterpret_cast<U**>(p_48e1a0 + 0x33b) = &g_dword_00657aa4;
    *reinterpret_cast<const char**>(p_48e1a0 + 0x46a) = s_str_00;
    *reinterpret_cast<void**>(p_48e1a0 + 0x470) = reinterpret_cast<void*>(0x005e8e50);
    *reinterpret_cast<const char**>(p_48e1a0 + 0x47d) = s_str_c;
    *reinterpret_cast<void**>(p_48e1a0 + 0x483) = reinterpret_cast<void*>(0x0048f040);
    *reinterpret_cast<void**>(p_48e1a0 + 0x4e7) = reinterpret_cast<void*>(0x0048ee90);
    *reinterpret_cast<U**>(p_48e1a0 + 0x510) = &g_dword_00657aa4;

    patch_rel_call(p_48e1a0 + 0x4b, reinterpret_cast<void*>(sub_0055eb70));
    patch_rel_call(p_48e1a0 + 0x5d, reinterpret_cast<void*>(thunk_0048dbe0));
    patch_rel_call(p_48e1a0 + 0xb5, reinterpret_cast<void*>(thunk_0048ac70));
    patch_rel_call(p_48e1a0 + 0xc1, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48e1a0 + 0xcc, reinterpret_cast<void*>(sub_005322b0));
    patch_rel_call(p_48e1a0 + 0xd3, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x111, reinterpret_cast<void*>(thunk_0048aa10));
    patch_rel_call(p_48e1a0 + 0x11f, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x168, reinterpret_cast<void*>(sub_0048a9a0));
    patch_rel_call(p_48e1a0 + 0x17b, reinterpret_cast<void*>(sub_00560140));
    patch_rel_call(p_48e1a0 + 0x18d, reinterpret_cast<void*>(thunk_0048ac50));
    patch_rel_call(p_48e1a0 + 0x1a1, reinterpret_cast<void*>(sub_005322c0));
    patch_rel_call(p_48e1a0 + 0x207, reinterpret_cast<void*>(thunk_0048c870));
    patch_rel_call(p_48e1a0 + 0x22a, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x240, reinterpret_cast<void*>(thunk_004931c0));
    patch_rel_call(p_48e1a0 + 0x252, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48e1a0 + 0x25e, reinterpret_cast<void*>(sub_005322b0));
    patch_rel_call(p_48e1a0 + 0x263, reinterpret_cast<void*>(sub_0048c4d0));
    patch_rel_call(p_48e1a0 + 0x271, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x2b1, reinterpret_cast<void*>(thunk_0048aa10));
    patch_rel_call(p_48e1a0 + 0x2bf, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x304, reinterpret_cast<void*>(sub_0048a9a0));
    patch_rel_call(p_48e1a0 + 0x31b, reinterpret_cast<void*>(sub_00560140));
    patch_rel_call(p_48e1a0 + 0x334, reinterpret_cast<void*>(thunk_0048ac90));
    patch_rel_call(p_48e1a0 + 0x349, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x35b, reinterpret_cast<void*>(thunk_004931c0));
    patch_rel_call(p_48e1a0 + 0x367, reinterpret_cast<void*>(sub_005322c0));
    patch_rel_call(p_48e1a0 + 0x380, reinterpret_cast<void*>(sub_005322c0));
    patch_rel_call(p_48e1a0 + 0x3a7, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48e1a0 + 0x3b1, reinterpret_cast<void*>(sub_0055eb70));
    patch_rel_call(p_48e1a0 + 0x3c1, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x3da, reinterpret_cast<void*>(thunk_0048c840));
    patch_rel_call(p_48e1a0 + 0x3fb, reinterpret_cast<void*>(thunk_00529050));
    patch_rel_call(p_48e1a0 + 0x404, reinterpret_cast<void*>(thunk_0050e140));
    patch_rel_call(p_48e1a0 + 0x410, reinterpret_cast<void*>(thunk_004937f0));
    patch_rel_call(p_48e1a0 + 0x41f, reinterpret_cast<void*>(sub_0055eb70));
    patch_rel_call(p_48e1a0 + 0x43c, reinterpret_cast<void*>(thunk_0048e9c0));
    patch_rel_call(p_48e1a0 + 0x44a, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x48b, reinterpret_cast<void*>(thunk_0048aa10));
    patch_rel_call(p_48e1a0 + 0x499, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x4de, reinterpret_cast<void*>(sub_0048a9a0));
    patch_rel_call(p_48e1a0 + 0x4f5, reinterpret_cast<void*>(sub_00560140));
    patch_rel_call(p_48e1a0 + 0x509, reinterpret_cast<void*>(thunk_0048ac90));
    patch_rel_call(p_48e1a0 + 0x51e, reinterpret_cast<void*>(sub_0059ef90));
    patch_rel_call(p_48e1a0 + 0x530, reinterpret_cast<void*>(thunk_004931c0));

    return true;
}

static bool is_ptr_arg(U tag, int arg_idx) {
    if (tag == 0x53c290 && arg_idx == 1) return true;
    if (tag == 0x5a28a0 && (arg_idx == 1 || arg_idx == 2)) return true;
    if (tag == 0x5323e0 && (arg_idx == 1 || arg_idx == 2)) return true;
    if (tag == 0x491cd0 && arg_idx == 2) return true;
    if (tag == 0x48ac90 && arg_idx == 1) return true;
    return false;
}

static bool traces_equal(const CallTrace& a, const CallTrace& b) {
    if (a.count != b.count) return false;
    for (U i = 0; i < a.count; ++i) {
        if (a.tag[i] != b.tag[i]) return false;
        if (is_ptr_arg(a.tag[i], 1)) {
            if ((a.arg1[i] != 0) != (b.arg1[i] != 0)) return false;
        } else {
            if (a.arg1[i] != b.arg1[i]) return false;
        }
        if (is_ptr_arg(a.tag[i], 2)) {
            if ((a.arg2[i] != 0) != (b.arg2[i] != 0)) return false;
        } else {
            if (a.arg2[i] != b.arg2[i]) return false;
        }
    }
    return true;
}

static void log_str(const char* s) {
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD written = 0;
    int len = 0;
    while (s[len]) len++;
    WriteFile(hOut, s, len, &written, NULL);
}

static void log_diff(int case_idx, U res_orig, U res_cpp, const CallTrace& a, const CallTrace& b) {
    char dbg[256];
    wsprintfA(dbg, "TC %d diff: res_orig=%d res_cpp=%d count_orig=%d count_cpp=%d\\n",
        case_idx, res_orig, res_cpp, a.count, b.count);
    log_str(dbg);
    U m = a.count > b.count ? a.count : b.count;
    for (U i = 0; i < m && i < 20; ++i) {
        wsprintfA(dbg, "  [%d] orig: tag=0x%x a1=0x%x a2=0x%x | cpp: tag=0x%x a1=0x%x a2=0x%x\\n",
            i, a.tag[i], a.arg1[i], a.arg2[i],
               b.tag[i], b.arg1[i], b.arg2[i]);
        log_str(dbg);
    }
}

#define require(cond) do { if (!(cond)) ExitProcess(static_cast<unsigned long>(__LINE__)); } while(0)

bool run_test_case(int case_idx) {
    s_mock_key = (case_idx == 3) ? 0x1b : 0;
    g_pfn_005b2080 = mock_timer_query;
    g_dword_00628c74 = 0;
    g_dword_00657aa4 = 1;
    g_byte_005d0728 = 0;
    g_dword_005b4980 = 0x1111;
    g_dword_005b4990 = 0x2222;
    g_dword_00508e70 = 0x3333;

    UiScreenNode node_orig, node_cpp;
    memset(&node_orig, 0, sizeof(node_orig));
    memset(&node_cpp, 0, sizeof(node_cpp));

    UiScreenContext ctx_orig, ctx_cpp;
    memset(&ctx_orig, 0, sizeof(ctx_orig));
    memset(&ctx_cpp, 0, sizeof(ctx_cpp));

    bool pass = true;

    switch (case_idx) {
        case 1: {
            node_orig.field_dc = 123;
            node_orig.active_element = nullptr;
            node_cpp = node_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_orig = call_orig_draw_screen_tree(&ctx_orig);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_cpp = ctx_cpp.ui_draw_screen_tree_0048cdf0();
            s_trace_cpp = g_trace;

            if (res_orig != res_cpp || !traces_equal(s_trace_orig, s_trace_cpp)) {
                log_diff(case_idx, res_orig, res_cpp, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 2: {
            node_orig.active_element = nullptr;
            node_cpp.active_element = nullptr;
            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_orig = call_orig_draw_screen_tree(&ctx_orig);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_cpp = ctx_cpp.ui_draw_screen_tree_0048cdf0();
            s_trace_cpp = g_trace;

            if (res_orig != res_cpp || !traces_equal(s_trace_orig, s_trace_cpp)) {
                pass = false;
            }
            break;
        }
        case 3: {
            node_orig.active_element = reinterpret_cast<void*>(0x1234);
            node_orig.field_be = 1;
            node_orig.field_dc = 10;
            node_orig.field_c5 = 0;
            node_cpp = node_orig;

            ctx_orig.field_e5 = 1;
            ctx_orig.field_e6 = 0;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_orig = call_orig_draw_screen_tree(&ctx_orig);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_cpp = ctx_cpp.ui_draw_screen_tree_0048cdf0();
            s_trace_cpp = g_trace;

            if (res_orig != res_cpp || !traces_equal(s_trace_orig, s_trace_cpp) || node_orig.field_c5 != node_cpp.field_c5) {
                pass = false;
            }
            break;
        }
        case 4: {
            node_orig.active_element = reinterpret_cast<void*>(0x1234);
            node_orig.field_be = 1;
            node_orig.field_dc = 10;
            node_cpp = node_orig;

            ctx_orig.field_e5 = 0;
            ctx_orig.field_e6 = 0;
            ctx_orig.field_e7 = 0;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_orig = call_orig_draw_screen_tree(&ctx_orig);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            U res_cpp = ctx_cpp.ui_draw_screen_tree_0048cdf0();
            s_trace_cpp = g_trace;

            if (res_orig != res_cpp || !traces_equal(s_trace_orig, s_trace_cpp)) {
                pass = false;
            }
            break;
        }
        case 5: {
            g_ui_screen_node_00628c70 = nullptr;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_refresh(&ctx_orig, "TestScreen", 0);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = nullptr;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_refresh_0048dcb0("TestScreen", 0);
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp)) {
                pass = false;
            }
            break;
        }
        case 6: {
            node_orig.mode_0_flag = 1;
            for (int k = 0; k < 12; ++k) node_orig.name[k] = "TrackSelect"[k];
            node_cpp = node_orig;

            ctx_orig.field_28 = 0;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_refresh(&ctx_orig, nullptr, 0);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_refresh_0048dcb0(nullptr, 0);
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp) || ctx_orig.field_c1 != ctx_cpp.field_c1 || ctx_orig.field_106 != ctx_cpp.field_106) {
                log_diff(case_idx, 0, 0, s_trace_orig, s_trace_cpp);
                char dbg[128];
                wsprintfA(dbg, "TC6 fields: orig(c1=%d 106=%d) cpp(c1=%d 106=%d)\\n",
                    ctx_orig.field_c1, ctx_orig.field_106, ctx_cpp.field_c1, ctx_cpp.field_106);
                log_str(dbg);
                pass = false;
            }
            break;
        }
        case 7: {
            node_orig.mode_1_flag = 1;
            for (int k = 0; k < 7; ++k) node_orig.name[k] = "Garage"[k];
            node_cpp = node_orig;

            ctx_orig.field_28 = 1;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_refresh(&ctx_orig, "CustomGarage", 0);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_refresh_0048dcb0("CustomGarage", 0);
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp) || ctx_orig.field_c7 != ctx_cpp.field_c7) {
                log_diff(case_idx, 0, 0, s_trace_orig, s_trace_cpp);
                char dbg[128];
                wsprintfA(dbg, "TC7 fields: orig(c7=%d) cpp(c7=%d)\\n",
                    ctx_orig.field_c7, ctx_cpp.field_c7);
                log_str(dbg);
                pass = false;
            }
            break;
        }
        case 8: {
            g_ui_screen_node_00628c70 = nullptr;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_render_present(&ctx_orig, 0, 0, nullptr);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = nullptr;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_render_present_0048e1a0(0, 0, nullptr);
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp)) {
                log_diff(case_idx, 0, 0, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 9: {
            node_orig.mode_0_flag = 1;
            for (int k = 0; k < 9; ++k) node_orig.name[k] = "MainMenu"[k];
            node_cpp = node_orig;

            void* dummy_cont = reinterpret_cast<void*>(0x8888);
            void* cont_ptr = &dummy_cont;
            ctx_orig.field_10 = cont_ptr;
            ctx_orig.field_0 = 100;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_render_present(&ctx_orig, 0, 0, nullptr);
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_render_present_0048e1a0(0, 0, nullptr);
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp) || ctx_orig.field_148 != ctx_cpp.field_148) {
                log_diff(case_idx, 0, 0, s_trace_orig, s_trace_cpp);
                char dbg[128];
                wsprintfA(dbg, "TC9 fields: orig(148=%d) cpp(148=%d)\\n",
                    ctx_orig.field_148, ctx_cpp.field_148);
                log_str(dbg);
                pass = false;
            }
            break;
        }
        case 10: {
            node_orig.mode_1_flag = 1;
            for (int k = 0; k < 12; ++k) node_orig.name[k] = "CarShowroom"[k];
            node_cpp = node_orig;

            void* dummy_cont = reinterpret_cast<void*>(0x8888);
            void* cont_ptr = &dummy_cont;
            ctx_orig.field_10 = cont_ptr;
            ctx_orig.field_4 = 200;
            ctx_cpp = ctx_orig;

            g_ui_screen_node_00628c70 = &node_orig;
            g_trace.count = 0;
            s_mem_pos = 0;
            call_orig_screen_render_present(&ctx_orig, 1, 5, "Porsche911");
            s_trace_orig = g_trace;

            g_ui_screen_node_00628c70 = &node_cpp;
            g_trace.count = 0;
            s_mem_pos = 0;
            ctx_cpp.ui_screen_render_present_0048e1a0(1, 5, "Porsche911");
            s_trace_cpp = g_trace;

            if (!traces_equal(s_trace_orig, s_trace_cpp) || ctx_orig.field_c7 != ctx_cpp.field_c7) {
                log_diff(case_idx, 0, 0, s_trace_orig, s_trace_cpp);
                char dbg[128];
                wsprintfA(dbg, "TC10 fields: orig(c7=%d) cpp(c7=%d)\\n",
                    ctx_orig.field_c7, ctx_cpp.field_c7);
                log_str(dbg);
                pass = false;
            }
            break;
        }
        default:
            return false;
    }

    return pass;
}

} // namespace porsche

extern "C" void entry() {
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD written = 0;
    if (!porsche::init_slab()) {
        WriteFile(hOut, "init_slab failed\n", 17, &written, NULL);
        ExitProcess(1);
    }

    int passed = 0;
    for (int i = 1; i <= 10; ++i) {
        char buf[64];
        int len = wsprintfA(buf, "TC %d...\\n", i);
        WriteFile(hOut, buf, len, &written, NULL);
        if (porsche::run_test_case(i)) {
            passed++;
            int len2 = wsprintfA(buf, "TC %d OK\\n", i);
            WriteFile(hOut, buf, len2, &written, NULL);
        } else {
            int len2 = wsprintfA(buf, "TC %d FAILED\\n", i);
            WriteFile(hOut, buf, len2, &written, NULL);
        }
    }

    if (passed != 10) ExitProcess(2);
    ExitProcess(0);
}
"""

def main():
    exp_dir = ROOT / "local/experiments/v2-app-main-411"
    exp_dir.mkdir(parents=True, exist_ok=True)
    fix_path = exp_dir / "app_main_fixture.cpp"
    fix_path.write_bytes((FIXTURE_CPP).replace("\r\n", "\n").encode("utf-8"))
    print(f"Generated {fix_path}")

if __name__ == "__main__":
    main()

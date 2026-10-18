"""Generate complete Run 412 fixture and experiment files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIXTURE_CPP = r"""#include "app_main_frame_event_pump_412.hpp"
#include <windows.h>
#include <cstdint>
#include <cstddef>

extern "C" int _fltused = 0x9876;
#pragma function(memcpy, memset, memcmp)
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
extern "C" int memcmp(const void* s1, const void* s2, size_t n) {
    const auto p1 = static_cast<const unsigned char*>(s1);
    const auto p2 = static_cast<const unsigned char*>(s2);
    for (size_t i = 0; i < n; ++i) {
        if (p1[i] != p2[i]) return static_cast<int>(p1[i]) - static_cast<int>(p2[i]);
    }
    return 0;
}
extern "C" void __cdecl _chkstk() {}


namespace porsche {

using U = std::uint32_t;

struct CallTrace {
    U count;
    U tag[1024];
    U arg1[1024];
    U arg2[1024];
    U arg3[1024];
};

static CallTrace g_trace;
static CallTrace s_trace_orig;
static CallTrace s_trace_cpp;

static void record_call(U tag, U a1 = 0, U a2 = 0, U a3 = 0) {
    if (g_trace.count < 1024) {
        g_trace.tag[g_trace.count] = tag;
        g_trace.arg1[g_trace.count] = a1;
        g_trace.arg2[g_trace.count] = a2;
        g_trace.arg3[g_trace.count] = a3;
        g_trace.count++;
    }
}

// Deterministic PRNG for rand() matching
static std::uint32_t s_prng_state = 0x12345678;
static char s_mock_ui_active = 0;

static std::int32_t s_mock_screen_mode = 0;
static std::uint32_t s_mock_state_7c98 = 0;
static std::uint32_t s_mock_state_7c94 = 0;
static std::uint32_t s_mock_state_7ca0 = 0;
static std::uint32_t s_mock_state_7ca4 = 0;

extern "C" {
    UiScreenNode* g_ui_screen_node_00628c70 = nullptr;
    std::uint8_t g_screen_buffer_006573e8[0x3e24];
    const char g_str_unknown_005d638c[] = "Unknown";
    std::uint32_t g_input_flag_005d1734 = 0;
    std::uint32_t g_input_out_005d1740 = 0;
    std::uint32_t g_input_out_005d1744 = 0;
    std::uint32_t g_input_out_005d1748 = 0;
    std::uint32_t g_input_out_005d174c = 0;
    std::uint32_t g_input_out_005d1750 = 0;

    void CALL_CDECL hook_00412e00() {
        record_call(0x412e00);
        *reinterpret_cast<std::int32_t*>(&g_screen_buffer_006573e8[0]) = s_mock_screen_mode;
        if (s_mock_state_7c98 != 0) *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b0]) = s_mock_state_7c98;
        if (s_mock_state_7c94 != 0) *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8ac]) = s_mock_state_7c94;
        if (s_mock_state_7ca0 != 0) *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8b8]) = s_mock_state_7ca0;
        if (s_mock_state_7ca4 != 0) *reinterpret_cast<std::uint32_t*>(&g_screen_buffer_006573e8[0x8bc]) = s_mock_state_7ca4;
    }
    void CALL_CDECL hook_004b6560(std::int32_t* stream) {
        record_call(0x4b6560, stream ? static_cast<U>(*stream) : 0);
    }
    void CALL_CDECL hook_004b6600(std::int32_t* stream) {
        record_call(0x4b6600, stream ? static_cast<U>(*stream) : 0);
    }
    void CALL_CDECL hook_004b4b80(const std::uint32_t* packet) {
        record_call(0x4b4b80, packet ? packet[0] : 0, packet ? packet[1] : 0);
    }
    std::int32_t CALL_CDECL hook_004b4cd0(const std::uint32_t* packet) {
        record_call(0x4b4cd0, packet ? packet[0] : 0);
        if (!packet) return 2;
        std::uint32_t op = packet[0];
        if (op >= 0x21e) return 3;
        if (op >= 0x14e) return 2;
        if (op >= 0x142) {
            const std::uint32_t* cur = (op >= 0x147) ? packet + 1 : packet;
            std::uint32_t count = cur[1];
            return static_cast<std::int32_t>((cur + count + 2) - packet);
        }
        if (op >= 0x10e) {
            const std::uint32_t* cur = (op >= 0x13a) ? packet + 1 : packet;
            const char* s = reinterpret_cast<const char*>(cur + 1);
            while (*s != '\0') s++;
            std::uintptr_t end_addr = (reinterpret_cast<std::uintptr_t>(s) + 4) & ~3;
            return static_cast<std::int32_t>((reinterpret_cast<const std::uint32_t*>(end_addr) + 1) - packet);
        }
        return 2;
    }
    void CALL_CDECL hook_0048d3d0() {
        record_call(0x48d3d0);
    }
    char CALL_CDECL hook_0048caa0() {
        record_call(0x48caa0, static_cast<U>(s_mock_ui_active));
        return s_mock_ui_active;
    }
    void CALL_CDECL hook_0048d490(const std::int32_t* packet) {
        record_call(0x48d490, packet ? static_cast<U>(packet[0]) : 0, packet ? static_cast<U>(packet[1]) : 0, packet ? static_cast<U>(packet[2]) : 0);
    }
    void CALL_CDECL hook_0048d440() {
        record_call(0x48d440);
    }
    void CALL_CDECL hook_0048d6a0() {
        record_call(0x48d6a0);
    }
    void CALL_CDECL hook_0053c380(std::int32_t ms) {
        record_call(0x53c380, static_cast<U>(ms));
    }
    void CALL_CDECL hook_00411760() {
        record_call(0x411760);
    }
    int CALL_CDECL hook_005a17c9() {
        s_prng_state = s_prng_state * 214013L + 2531011L;
        int res = (s_prng_state >> 16) & 0x7fff;
        record_call(0x5a17c9, static_cast<U>(res));
        return res;
    }
}

static std::uint8_t* s_slab = nullptr;

static void patch_rel_call(std::uint8_t* site, void* target) {
    auto diff = static_cast<std::int32_t>(reinterpret_cast<std::uint8_t*>(target) - (site + 5));
    *reinterpret_cast<std::int32_t*>(site + 1) = diff;
}

bool init_slab() {
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

    std::uint8_t* p_4b4da0 = s_slab + 0x0000;
    memcpy(p_4b4da0, pe_buf + (0x004b4da0 - 0x400000), 1078);
    VirtualFree(pe_buf, 0, MEM_RELEASE);

    // Patch 39 HIGHLOW relocations
    const U r_screen_buf[] = { 0x0012, 0x0076 };
    for (U off : r_screen_buf) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0];
    }
    *reinterpret_cast<void**>(p_4b4da0 + 0x001d) = &g_screen_buffer_006573e8[0x9c8]; // 00657db0
    *reinterpret_cast<void**>(p_4b4da0 + 0x0027) = &g_screen_buffer_006573e8[0x9c0]; // 00657da8
    *reinterpret_cast<void**>(p_4b4da0 + 0x0031) = &g_screen_buffer_006573e8[0x9c4]; // 00657dac

    const U r_node[] = { 0x008e, 0x030e };
    for (U off : r_node) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_ui_screen_node_00628c70;
    }

    *reinterpret_cast<void**>(p_4b4da0 + 0x02c1) = &g_screen_buffer_006573e8[0x34];  // 0065741c
    const U r_8080[] = { 0x02bb, 0x02d5 };
    for (U off : r_8080) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0xc98]; // 00658080
    }
    const U r_8084[] = { 0x02db, 0x02f6 };
    for (U off : r_8084) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0xc9c]; // 00658084
    }
    const U r_8088[] = { 0x02c7, 0x02fc };
    for (U off : r_8088) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0xca0]; // 00658088
    }
    *reinterpret_cast<void**>(p_4b4da0 + 0x02ee) = &g_screen_buffer_006573e8[0xe18];  // 00658200

    const U r_name[] = { 0x035e, 0x037b };
    for (U off : r_name) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x69c]; // 00657a84
    }
    *reinterpret_cast<const char**>(p_4b4da0 + 0x0367) = g_str_unknown_005d638c;     // 005d638c

    *reinterpret_cast<void**>(p_4b4da0 + 0x0394) = &g_input_flag_005d1734;            // 005d1734

    const U r_7c98[] = { 0x03a7, 0x03bd };
    for (U off : r_7c98) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8b0]; // 00657c98
    }
    const U r_7c94[] = { 0x03b1, 0x03c6, 0x03d2 };
    for (U off : r_7c94) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8ac]; // 00657c94
    }
    const U r_7ca0[] = { 0x03da, 0x03f3 };
    for (U off : r_7ca0) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8b8]; // 00657ca0
    }
    const U r_7ca4[] = { 0x03df, 0x03f9 };
    for (U off : r_7ca4) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8bc]; // 00657ca4
    }
    const U r_7cac[] = { 0x03e4, 0x03ff };
    for (U off : r_7cac) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8c4]; // 00657cac
    }
    const U r_7ca8[] = { 0x03e9, 0x0409 };
    for (U off : r_7ca8) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8c0]; // 00657ca8
    }
    const U r_7cb0[] = { 0x03ee, 0x0415 };
    for (U off : r_7cb0) {
        *reinterpret_cast<void**>(p_4b4da0 + off) = &g_screen_buffer_006573e8[0x8c8]; // 00657cb0
    }

    *reinterpret_cast<void**>(p_4b4da0 + 0x0404) = &g_input_out_005d1740;            // 005d1740
    *reinterpret_cast<void**>(p_4b4da0 + 0x040f) = &g_input_out_005d1744;            // 005d1744
    *reinterpret_cast<void**>(p_4b4da0 + 0x041b) = &g_input_out_005d174c;            // 005d174c
    *reinterpret_cast<void**>(p_4b4da0 + 0x0420) = &g_input_out_005d1748;            // 005d1748
    *reinterpret_cast<void**>(p_4b4da0 + 0x0426) = &g_input_out_005d1750;            // 005d1750

    // Patch 21 relative CALL instructions
    patch_rel_call(p_4b4da0 + 0x0016, reinterpret_cast<void*>(memset));
    patch_rel_call(p_4b4da0 + 0x0039, reinterpret_cast<void*>(hook_00412e00));
    patch_rel_call(p_4b4da0 + 0x0046, reinterpret_cast<void*>(hook_004b6560));
    patch_rel_call(p_4b4da0 + 0x004c, reinterpret_cast<void*>(hook_004b6600));
    patch_rel_call(p_4b4da0 + 0x005e, reinterpret_cast<void*>(hook_004b4b80));
    patch_rel_call(p_4b4da0 + 0x0064, reinterpret_cast<void*>(hook_004b4cd0));
    patch_rel_call(p_4b4da0 + 0x0088, reinterpret_cast<void*>(hook_0048d3d0));
    patch_rel_call(p_4b4da0 + 0x018a, reinterpret_cast<void*>(hook_0048caa0));
    patch_rel_call(p_4b4da0 + 0x019a, reinterpret_cast<void*>(hook_004b4cd0));
    patch_rel_call(p_4b4da0 + 0x01a9, reinterpret_cast<void*>(memcpy));
    patch_rel_call(p_4b4da0 + 0x01f9, reinterpret_cast<void*>(hook_004b4b80));
    patch_rel_call(p_4b4da0 + 0x0200, reinterpret_cast<void*>(hook_0048caa0));
    patch_rel_call(p_4b4da0 + 0x020a, reinterpret_cast<void*>(hook_0048d490));
    patch_rel_call(p_4b4da0 + 0x0213, reinterpret_cast<void*>(hook_004b4cd0));
    patch_rel_call(p_4b4da0 + 0x0227, reinterpret_cast<void*>(hook_0048caa0));
    patch_rel_call(p_4b4da0 + 0x0268, reinterpret_cast<void*>(hook_005a17c9));
    patch_rel_call(p_4b4da0 + 0x0284, reinterpret_cast<void*>(hook_0048d490));
    patch_rel_call(p_4b4da0 + 0x02ac, reinterpret_cast<void*>(hook_0048d440));
    patch_rel_call(p_4b4da0 + 0x02b1, reinterpret_cast<void*>(hook_0048d6a0));
    patch_rel_call(p_4b4da0 + 0x038d, reinterpret_cast<void*>(hook_0053c380));
    patch_rel_call(p_4b4da0 + 0x042a, reinterpret_cast<void*>(hook_00411760));

    return true;
}

static void call_orig_frame_event_pump(std::int32_t* stream) {
    using FuncType = void(CALL_CDECL*)(std::int32_t*);
    auto fn = reinterpret_cast<FuncType>(s_slab);
    fn(stream);
}

static bool traces_equal(const CallTrace& a, const CallTrace& b) {
    if (a.count != b.count) return false;
    for (U i = 0; i < a.count; ++i) {
        if (a.tag[i] != b.tag[i]) return false;
        if (a.arg1[i] != b.arg1[i]) return false;
        if (a.arg2[i] != b.arg2[i]) return false;
        if (a.arg3[i] != b.arg3[i]) return false;
    }
    return true;
}

static void log_str(const char* s) {
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD written = 0;
    while (*s) {
        WriteFile(hOut, s, 1, &written, NULL);
        s++;
    }
}

static void log_diff(int case_idx, const CallTrace& orig, const CallTrace& cpp) {
    char buf[128];
    wsprintfA(buf, "DIFF Case %d: orig_count=%d cpp_count=%d\n", case_idx, orig.count, cpp.count);
    log_str(buf);
    U min_c = orig.count < cpp.count ? orig.count : cpp.count;
    for (U i = 0; i < min_c; ++i) {
        if (orig.tag[i] != cpp.tag[i] || orig.arg1[i] != cpp.arg1[i] || orig.arg2[i] != cpp.arg2[i] || orig.arg3[i] != cpp.arg3[i]) {
            wsprintfA(buf, "  [%d] orig(tag=%x a1=%x a2=%x a3=%x) vs cpp(tag=%x a1=%x a2=%x a3=%x)\n",
                i, orig.tag[i], orig.arg1[i], orig.arg2[i], orig.arg3[i],
                cpp.tag[i], cpp.arg1[i], cpp.arg2[i], cpp.arg3[i]);
            log_str(buf);
            break;
        }
    }
}

struct Snapshot {
    std::uint8_t screen_buf[0x3e24];
    std::uint32_t in_40, in_44, in_48, in_4c, in_50;
};

static void take_snapshot(Snapshot& snap) {
    memcpy(snap.screen_buf, g_screen_buffer_006573e8, sizeof(snap.screen_buf));
    snap.in_40 = g_input_out_005d1740;
    snap.in_44 = g_input_out_005d1744;
    snap.in_48 = g_input_out_005d1748;
    snap.in_4c = g_input_out_005d174c;
    snap.in_50 = g_input_out_005d1750;
}

static bool snapshots_equal(const Snapshot& a, const Snapshot& b) {
    if (memcmp(a.screen_buf, b.screen_buf, sizeof(a.screen_buf)) != 0) return false;
    if (a.in_40 != b.in_40 || a.in_44 != b.in_44 || a.in_48 != b.in_48 || a.in_4c != b.in_4c || a.in_50 != b.in_50) return false;
    return true;
}

bool run_test_case(int case_idx) {
    bool pass = true;

    // Reset fixtures
    s_mock_ui_active = 0;
    s_mock_screen_mode = 0;
    s_mock_state_7c98 = 0;
    s_mock_state_7c94 = 0;
    s_mock_state_7ca0 = 0;
    s_mock_state_7ca4 = 0;
    s_prng_state = 0x12345678;
    g_ui_screen_node_00628c70 = nullptr;
    memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
    g_input_flag_005d1734 = 0;
    g_input_out_005d1740 = 0;
    g_input_out_005d1744 = 0;
    g_input_out_005d1748 = 0;
    g_input_out_005d174c = 0;
    g_input_out_005d1750 = 0;

    static Snapshot snap_orig, snap_cpp;
    memset(&snap_orig, 0, sizeof(snap_orig));
    memset(&snap_cpp, 0, sizeof(snap_cpp));

    switch (case_idx) {
        case 1: {
            // Case 1: Empty event stream, mode != 3, input_flag = 0
            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[] = { 0 };

            g_trace.count = 0;
            s_prng_state = 0x12345678;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_input_flag_005d1734 = 0;
            g_trace.count = 0;
            s_prng_state = 0x12345678;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 2: {
            // Case 2: Non-empty stream with 2 events, mode remains 0
            std::int32_t stream_orig[] = { 0x220, 1, 10, 0x225, 2, 20, 0 };
            std::int32_t stream_cpp[]  = { 0x220, 1, 10, 0x225, 2, 20, 0 };

            g_trace.count = 0;
            s_prng_state = 0x55aa3311;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_input_flag_005d1734 = 0;
            g_trace.count = 0;
            s_prng_state = 0x55aa3311;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 3: {
            // Case 3: input_flag = 1, screen_state_7c98 pre-set to 3
            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[]  = { 0 };

            g_input_flag_005d1734 = 1;
            s_mock_state_7c98 = 3;
            s_mock_state_7ca0 = 99;

            g_trace.count = 0;
            s_prng_state = 0x11223344;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_input_flag_005d1734 = 1;
            g_trace.count = 0;
            s_prng_state = 0x11223344;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 4: {
            // Case 4: input_flag = 1, state_7c98 = 0, state_7c94 = 1
            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[]  = { 0 };

            g_input_flag_005d1734 = 1;
            s_mock_state_7c98 = 0;
            s_mock_state_7c94 = 1;
            s_mock_state_7ca0 = 42;

            g_trace.count = 0;
            s_prng_state = 0x11223344;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_input_flag_005d1734 = 1;
            g_trace.count = 0;
            s_prng_state = 0x11223344;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 5: {
            // Case 5: input_flag = 1, state_7c98 = 0, state_7c94 = 0 (ca0..cb0 preserved)
            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[]  = { 0 };

            g_input_flag_005d1734 = 1;
            s_mock_state_7c98 = 0;
            s_mock_state_7c94 = 0;
            s_mock_state_7ca0 = 777;
            s_mock_state_7ca4 = 888;

            g_trace.count = 0;
            s_prng_state = 0x11223344;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_input_flag_005d1734 = 1;
            g_trace.count = 0;
            s_prng_state = 0x11223344;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 6: {
            // Case 6: Screen mode = 3, but g_ui_screen_node_00628c70 == nullptr
            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[]  = { 0 };

            s_mock_screen_mode = 3;
            g_ui_screen_node_00628c70 = nullptr;

            g_trace.count = 0;
            s_prng_state = 0x99887766;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_ui_screen_node_00628c70 = nullptr;
            g_trace.count = 0;
            s_prng_state = 0x99887766;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 7: {
            // Case 7: Mode = 3, node exists but field_be = 0 (abort/not ready)
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 0;
            node.field_bf = 0;
            node.field_dc = 1;

            std::int32_t stream_orig[] = { 0 };
            std::int32_t stream_cpp[]  = { 0 };

            s_mock_screen_mode = 3;
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x12344321;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x12344321;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 8: {
            // Case 8: Mode = 3, ready, child list has 3 items, target_dc matched
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 1;
            node.field_bf = 0;
            node.field_dc = 2; // target ID 2
            node.field_e5 = 0x07; // bits 0, 1, 2 set (3 matches)

            UiElementData item1{}, item2{}, item3{};
            item1.element_id = 0;
            item2.element_id = 1;
            item3.element_id = 2;

            UiElementNode n_head{}, n1{}, n2{}, n3{};
            n_head.next = &n1;
            n_head.prev = &n3;
            n1.next = &n2;
            n1.prev = &n_head;
            n1.element_data = &item1;
            n2.next = &n3;
            n2.prev = &n1;
            n2.element_data = &item2;
            n3.next = &n_head;
            n3.prev = &n2;
            n3.element_data = &item3;

            node.child_list_head = &n_head;

            std::int32_t stream_orig[] = { 0x220, 2, 50, 0 };
            std::int32_t stream_cpp[]  = { 0x220, 2, 50, 0 };

            s_mock_screen_mode = 3;
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x77665544;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x77665544;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 9: {
            // Case 9: Mode = 3, UI active (s_mock_ui_active = 1), shuffle execution
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 1;
            node.field_bf = 0;
            node.field_dc = 1;
            node.field_e5 = 0x03; // bits 0, 1 (2 matches)

            UiElementData item1{}, item2{};
            item1.element_id = 0;
            item2.element_id = 1;

            UiElementNode n_head{}, n1{}, n2{};
            n_head.next = &n1;
            n_head.prev = &n2;
            n1.next = &n2;
            n1.prev = &n_head;
            n1.element_data = &item1;
            n2.next = &n_head;
            n2.prev = &n1;
            n2.element_data = &item2;

            node.child_list_head = &n_head;

            std::int32_t stream_orig[] = { 0x220, 1, 100, 0 };
            std::int32_t stream_cpp[]  = { 0x220, 1, 100, 0 };

            s_mock_ui_active = 1;
            s_mock_screen_mode = 3;
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0xabcdef01;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0xabcdef01;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 10: {
            // Case 10: Mixed event stream (ranges < 0x2f, >= 0x146, 0x247 skipped, >= 0x21e)
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 1;
            node.field_bf = 0;
            node.field_dc = 0;
            node.field_e5 = 0x05; // bits 0 and 2 (2 matches)

            UiElementData item1{}, item2{}, item3{};
            item1.element_id = 0;
            item2.element_id = 1; // not in bitmask
            item3.element_id = 2;

            UiElementNode n_head{}, n1{}, n2{}, n3{};
            n_head.next = &n1;
            n_head.prev = &n3;
            n1.next = &n2;
            n1.prev = &n_head;
            n1.element_data = &item1;
            n2.next = &n3;
            n2.prev = &n1;
            n2.element_data = &item2;
            n3.next = &n_head;
            n3.prev = &n2;
            n3.element_data = &item3;

            node.child_list_head = &n_head;

            std::int32_t stream_orig[] = {
                0x220, 0, 10,       // >= 0x21e, matches target_dc=0
                0x247, 0, 0,        // 0x247, skipped
                0x150, 5,           // 0x14e <= op < 0x21e, fe_apply
                0x10,  20,          // < 0x2f, sub_0048d490
                0
            };
            std::int32_t stream_cpp[] = {
                0x220, 0, 10,
                0x247, 0, 0,
                0x150, 5,
                0x10,  20,
                0
            };

            s_mock_ui_active = 1;
            s_mock_screen_mode = 3;
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x13579bdf;
            call_orig_frame_event_pump(stream_orig);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            memset(g_screen_buffer_006573e8, 0, sizeof(g_screen_buffer_006573e8));
            g_ui_screen_node_00628c70 = &node;
            g_trace.count = 0;
            s_prng_state = 0x13579bdf;
            frame_event_pump_004b4da0(stream_cpp);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
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
        int len = wsprintfA(buf, "TC %d...\n", i);
        WriteFile(hOut, buf, len, &written, NULL);
        if (porsche::run_test_case(i)) {
            passed++;
            int len2 = wsprintfA(buf, "TC %d OK\n", i);
            WriteFile(hOut, buf, len2, &written, NULL);
        } else {
            int len2 = wsprintfA(buf, "TC %d FAILED\n", i);
            WriteFile(hOut, buf, len2, &written, NULL);
        }
    }

    if (passed != 10) ExitProcess(2);
    ExitProcess(0);
}
"""

def main():
    exp_dir = ROOT / "local/experiments/v2-app-main-412"
    exp_dir.mkdir(parents=True, exist_ok=True)
    fix_path = exp_dir / "app_main_fixture.cpp"
    fix_path.write_bytes((FIXTURE_CPP).replace("\r\n", "\n").encode("utf-8"))
    print(f"Generated {fix_path}")

if __name__ == "__main__":
    main()

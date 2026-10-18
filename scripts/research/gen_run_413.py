"""Generate complete Run 413 fixture and experiment files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIXTURE_CPP = r"""#include "app_main_render_screen_driver_413.hpp"
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

// CRT _ftol implementation
extern "C" __declspec(naked) void _ftol() {
    __asm {
        push    ebp
        mov     ebp, esp
        add     esp, -12
        wait
        fnstcw  word ptr [ebp - 2]
        wait
        mov     ax, word ptr [ebp - 2]
        or      ah, 0x0c
        mov     word ptr [ebp - 4], ax
        fldcw   word ptr [ebp - 4]
        fistp   qword ptr [ebp - 12]
        fldcw   word ptr [ebp - 2]
        mov     eax, dword ptr [ebp - 12]
        mov     edx, dword ptr [ebp - 8]
        leave
        ret
    }
}

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

static float s_float_12_4 = 12.4f;
static float s_float_54_0 = 54.0f;
static float s_float_1_0 = 1.0f;

static const char s_str_car_fsh_fmt_005cccc8[] = "%s%s.fsh";
static const char s_str_era_fsh_fmt_005d10c0[] = "%sera%d.fsh";
static const char s_str_eradtr_fsh_fmt_005d10b0[] = "%seradtr.fsh";
static const char s_str_mloading_fsh_fmt_005d10a0[] = "%sMLoading.fsh";
static const char s_str_loadtext_fsh_fmt_005d1090[] = "%sloadtext.fsh";

static std::uint8_t s_mock_canvas_buf[128];
static std::uint8_t s_mock_bg_fsh[1024];
static std::uint8_t s_mock_car_fsh[1024];
static std::uint8_t s_mock_load_fsh[1024];
static std::uint8_t s_mock_text_fsh[1024];
static std::uint8_t s_mock_elem[64];
static std::uint8_t s_mock_graphic[64];

static std::int32_t s_mock_time_target = 100;
static std::int32_t s_mock_time_current = 100;
static std::int32_t s_mock_theme = 0x20a;
static char s_mock_visible = 1;

extern "C" {
    char g_render_enabled_00655a28 = 0;
    void* g_render_canvas_00655a24 = nullptr;
    std::int32_t g_display_format_005dead0 = 0;
    UiScreenNode* g_ui_screen_node_00628c70 = nullptr;
    std::int32_t g_screen_matched_index_0065741c = 0;
    std::int32_t g_skip_render_00657440 = 0;
    std::int32_t g_screen_mode_006573e8 = 0;
    const char* g_fsh_path_0065b350 = "art/cars/";
    char g_screen_suffix_00657444 = 0;
    const char* g_fsh_dir_0065b334 = "art/fe/";
    std::int32_t g_blend_flag_0065742c = 0;
    std::int32_t g_alt_flag_00657430 = 0;
    std::int32_t g_loadtext_idx_00657c84 = 0;
    std::int32_t g_slot_count_00658084 = 0;
    std::uint8_t g_slot_table_00658200[0x580 * 16];
    std::int32_t g_screen_width_005deac8 = 640;
    std::int32_t g_screen_height_005deacc = 480;

    static void CALL_STDCALL mock_driver_fn1(std::int32_t a) { record_call(0x6bd9b0, static_cast<U>(a)); }
    static void CALL_STDCALL mock_driver_fn2() { record_call(0x6bd91c); }
    static void CALL_STDCALL mock_driver_fn3(std::int32_t a) { record_call(0x6bd978, static_cast<U>(a)); }
    static void CALL_STDCALL mock_driver_fn4() { record_call(0x6bd948); }

    void (CALL_STDCALL *g_driver_fn_006bd9b0)(std::int32_t) = mock_driver_fn1;
    void (CALL_STDCALL *g_driver_fn_006bd91c)() = mock_driver_fn2;
    void (CALL_STDCALL *g_driver_fn_006bd978)(std::int32_t) = mock_driver_fn3;
    void (CALL_STDCALL *g_driver_fn_006bd948)() = mock_driver_fn4;

    void* CALL_CDECL hook_00535950(std::int32_t w, std::int32_t h, std::int32_t format, std::int32_t bpp) {
        record_call(0x535950, static_cast<U>(w), static_cast<U>(h), static_cast<U>(format));
        (void)bpp;
        return s_mock_canvas_buf;
    }
    void CALL_CDECL hook_004edc00(std::int32_t opcode, void** p_stream, std::int32_t id, std::int32_t step) {
        record_call(0x4edc00, static_cast<U>(opcode), static_cast<U>(id), static_cast<U>(step));
        if (p_stream && *p_stream) {
            auto p = reinterpret_cast<std::int32_t*>(*p_stream);
            *p++ = opcode;
            *p++ = id;
            *p++ = step;
            *p_stream = p;
        }
    }
    void CALL_CDECL hook_0048d550(const std::int32_t* packet) {
        record_call(0x48d550, packet ? static_cast<U>(packet[0]) : 0, packet ? static_cast<U>(packet[1]) : 0);
    }
    std::int32_t CALL_CDECL hook_004ad670() {
        record_call(0x4ad670);
        return s_mock_time_target;
    }
    std::int32_t CALL_CDECL hook_004ad6c0() {
        record_call(0x4ad6c0);
        return s_mock_time_current;
    }
    void CALL_CDECL hook_005366e0(std::int32_t a1) {
        record_call(0x5366e0, static_cast<U>(a1));
        s_mock_time_current = s_mock_time_target;
    }
    void CALL_CDECL hook_00534480(void* canvas) {
        record_call(0x534480, canvas ? 1 : 0);
    }
    std::int32_t CALL_CDECL hook_0059dc30(const char* filename) {
        record_call(0x59dc30, filename ? static_cast<U>(filename[0]) : 0);
        return 1;
    }
    std::uint8_t* CALL_CDECL hook_0059d8e0(const char* filename, std::int32_t mode) {
        record_call(0x59d8e0, filename ? static_cast<U>(filename[0]) : 0, static_cast<U>(mode));
        if (filename && filename[0] == 'a' && filename[4] == 'c') return s_mock_car_fsh;
        if (filename && filename[0] == 'a' && filename[7] == 'M') return s_mock_load_fsh;
        if (filename && filename[0] == 'a' && filename[7] == 'l') return s_mock_text_fsh;
        return s_mock_bg_fsh;
    }
    std::int32_t CALL_CDECL hook_005032d0() {
        record_call(0x5032d0);
        return s_mock_theme;
    }
    void CALL_CDECL hook_00563440(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h) {
        (void)chunk; (void)w; (void)h;
        record_call(0x563440, static_cast<U>(x), static_cast<U>(y));
    }
    void CALL_CDECL hook_00563320(void* chunk) {
        (void)chunk;
        record_call(0x563320);
    }
    void CALL_CDECL hook_00563160(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h) {
        (void)chunk; (void)w; (void)h;
        record_call(0x563160, static_cast<U>(x), static_cast<U>(y));
    }
    void CALL_CDECL hook_00531f90(void* ptr) {
        record_call(0x531f90, ptr ? 1 : 0);
    }
    void CALL_CDECL hook_00562810(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h) {
        (void)chunk; (void)w; (void)h;
        record_call(0x562810, static_cast<U>(x), static_cast<U>(y));
    }
    void CALL_CDECL hook_00562680(std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h, std::uint32_t color) {
        (void)h; (void)color;
        record_call(0x562680, static_cast<U>(x), static_cast<U>(y), static_cast<U>(w));
    }
    void CALL_CDECL hook_005322b0(void* container) {
        (void)container;
        record_call(0x5322b0);
    }
    std::uint8_t* CALL_CDECL hook_0048d720(std::int32_t index) {
        record_call(0x48d720, static_cast<U>(index));
        return s_mock_elem;
    }
    char CALL_THISCALL UiElement::is_visible_00490390() {
        record_call(0x490390, static_cast<U>(s_mock_visible));
        return s_mock_visible;
    }
    std::uint8_t* CALL_THISCALL UiElement::get_graphic_004903f0(std::int32_t a1) {
        record_call(0x4903f0, static_cast<U>(a1));
        return s_mock_graphic;
    }
    void CALL_CDECL hook_005322c0(void* container) {
        (void)container;
        record_call(0x5322c0);
    }
    void CALL_CDECL hook_004b0d70() {
        record_call(0x4b0d70);
    }
    void CALL_CDECL hook_00534540() {
        record_call(0x534540);
    }
    void CALL_CDECL hook_0053d570(void* surf, std::int32_t x, std::int32_t y) {
        (void)surf;
        record_call(0x53d570, static_cast<U>(x), static_cast<U>(y));
    }
    void CALL_CDECL hook_00534550() {
        record_call(0x534550);
    }
    void CALL_CDECL hook_00533f80(void* canvas) {
        record_call(0x533f80, canvas ? 1 : 0);
    }
    int CALL_CDECL hook_005a0fbf(char* dst, const char* fmt, ...) {
        record_call(0x5a0fbf, fmt ? static_cast<U>(fmt[0]) : 0);
        if (dst && fmt) {
            for (int i = 0; i < 32 && fmt[i]; ++i) dst[i] = fmt[i];
            dst[31] = 0;
        }
        return 1;
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

    std::uint8_t* p_4a4a70 = s_slab + 0x0000;
    memcpy(p_4a4a70, pe_buf + (0x004a4a70 - 0x400000), 2424);
    VirtualFree(pe_buf, 0, MEM_RELEASE);

    // Patch 52 HIGHLOW relocations
    const U r_render_en[] = { 0x0014, 0x0022, 0x0030, 0x0097, 0x0718 };
    for (U off : r_render_en) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_render_enabled_00655a28;

    const U r_canvas[] = { 0x003d, 0x0060, 0x0123, 0x0927, 0x0955, 0x0968 };
    for (U off : r_canvas) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_render_canvas_00655a24;

    *reinterpret_cast<void**>(p_4a4a70 + 0x0046) = &g_display_format_005dead0;

    const U r_node[] = { 0x0065, 0x04f0, 0x05e7, 0x06a0, 0x06d2, 0x0734, 0x08cc };
    for (U off : r_node) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_ui_screen_node_00628c70;

    *reinterpret_cast<void**>(p_4a4a70 + 0x00a1) = &g_screen_matched_index_0065741c;
    *reinterpret_cast<void**>(p_4a4a70 + 0x00e9) = &g_skip_render_00657440;
    *reinterpret_cast<void**>(p_4a4a70 + 0x012f) = &g_screen_mode_006573e8;
    *reinterpret_cast<void**>(p_4a4a70 + 0x015c) = &g_fsh_path_0065b350;
    *reinterpret_cast<void**>(p_4a4a70 + 0x0161) = &g_screen_suffix_00657444;
    *reinterpret_cast<const char**>(p_4a4a70 + 0x016e) = s_str_car_fsh_fmt_005cccc8;

    const U r_dir[] = { 0x01d1, 0x01e4, 0x0546, 0x0612 };
    for (U off : r_dir) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_fsh_dir_0065b334;

    *reinterpret_cast<const char**>(p_4a4a70 + 0x01db) = s_str_era_fsh_fmt_005d10c0;
    *reinterpret_cast<const char**>(p_4a4a70 + 0x01ee) = s_str_eradtr_fsh_fmt_005d10b0;

    const U r_blend[] = { 0x039b, 0x03d9, 0x045d };
    for (U off : r_blend) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_blend_flag_0065742c;

    *reinterpret_cast<void**>(p_4a4a70 + 0x0431) = &g_alt_flag_00657430;
    *reinterpret_cast<const char**>(p_4a4a70 + 0x055c) = s_str_mloading_fsh_fmt_005d10a0;

    const U r_loadtext[] = { 0x0603, 0x0648 };
    for (U off : r_loadtext) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_loadtext_idx_00657c84;

    *reinterpret_cast<const char**>(p_4a4a70 + 0x061c) = s_str_loadtext_fsh_fmt_005d1090;
    *reinterpret_cast<void**>(p_4a4a70 + 0x06b8) = &s_float_12_4;

    const U r_slots[] = { 0x073d, 0x08b8 };
    for (U off : r_slots) *reinterpret_cast<void**>(p_4a4a70 + off) = &g_slot_count_00658084;

    *reinterpret_cast<void**>(p_4a4a70 + 0x074c) = &g_slot_table_00658200[0x408];
    *reinterpret_cast<void**>(p_4a4a70 + 0x0803) = &s_float_54_0;

    const U r_f1[] = { 0x0825, 0x0873 };
    for (U off : r_f1) *reinterpret_cast<void**>(p_4a4a70 + off) = &s_float_1_0;

    *reinterpret_cast<void**>(p_4a4a70 + 0x08ef) = &g_driver_fn_006bd9b0;
    *reinterpret_cast<void**>(p_4a4a70 + 0x08f5) = &g_driver_fn_006bd91c;
    *reinterpret_cast<void**>(p_4a4a70 + 0x08fd) = &g_driver_fn_006bd978;
    *reinterpret_cast<void**>(p_4a4a70 + 0x0907) = &g_screen_height_005deacc;
    *reinterpret_cast<void**>(p_4a4a70 + 0x090d) = &g_screen_width_005deac8;
    *reinterpret_cast<void**>(p_4a4a70 + 0x0941) = &g_driver_fn_006bd948;

    // Patch CALL instructions
    patch_rel_call(p_4a4a70 + 0x0057, reinterpret_cast<void*>(hook_00535950));
    patch_rel_call(p_4a4a70 + 0x00b9, reinterpret_cast<void*>(hook_004edc00));
    patch_rel_call(p_4a4a70 + 0x00df, reinterpret_cast<void*>(hook_0048d550));
    patch_rel_call(p_4a4a70 + 0x00f7, reinterpret_cast<void*>(hook_004ad670));
    patch_rel_call(p_4a4a70 + 0x00fe, reinterpret_cast<void*>(hook_004ad6c0));
    patch_rel_call(p_4a4a70 + 0x0109, reinterpret_cast<void*>(hook_005366e0));
    patch_rel_call(p_4a4a70 + 0x0111, reinterpret_cast<void*>(hook_004ad670));
    patch_rel_call(p_4a4a70 + 0x0118, reinterpret_cast<void*>(hook_004ad6c0));
    patch_rel_call(p_4a4a70 + 0x0128, reinterpret_cast<void*>(hook_00534480));
    patch_rel_call(p_4a4a70 + 0x0173, reinterpret_cast<void*>(hook_005a0fbf));
    patch_rel_call(p_4a4a70 + 0x0180, reinterpret_cast<void*>(hook_0059dc30));
    patch_rel_call(p_4a4a70 + 0x0195, reinterpret_cast<void*>(hook_0059d8e0));
    patch_rel_call(p_4a4a70 + 0x01a6, reinterpret_cast<void*>(hook_005032d0));
    patch_rel_call(p_4a4a70 + 0x01f3, reinterpret_cast<void*>(hook_005a0fbf));
    patch_rel_call(p_4a4a70 + 0x0202, reinterpret_cast<void*>(hook_0059d8e0));

    // _ftol calls (0x5a0f98)
    const U r_ftol[] = {
        0x021f, 0x025b, 0x029d, 0x02e7, 0x032f, 0x03c2, 0x03cc, 0x040d,
        0x0424, 0x04c4, 0x04ca, 0x066f, 0x0683, 0x06bc, 0x07b9, 0x080d,
        0x0830, 0x0843, 0x0855, 0x087e, 0x08a9
    };
    for (U off : r_ftol) patch_rel_call(p_4a4a70 + off, reinterpret_cast<void*>(_ftol));

    patch_rel_call(p_4a4a70 + 0x022b, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x0267, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x02ab, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x02f3, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x033b, reinterpret_cast<void*>(hook_00563440));

    patch_rel_call(p_4a4a70 + 0x03ac, reinterpret_cast<void*>(hook_00563320));
    patch_rel_call(p_4a4a70 + 0x03d3, reinterpret_cast<void*>(hook_00563160));
    patch_rel_call(p_4a4a70 + 0x03e5, reinterpret_cast<void*>(hook_00563320));
    patch_rel_call(p_4a4a70 + 0x042b, reinterpret_cast<void*>(hook_00563160));
    patch_rel_call(p_4a4a70 + 0x0471, reinterpret_cast<void*>(hook_00563320));
    patch_rel_call(p_4a4a70 + 0x04d1, reinterpret_cast<void*>(hook_00563160));

    patch_rel_call(p_4a4a70 + 0x04da, reinterpret_cast<void*>(hook_00531f90));
    patch_rel_call(p_4a4a70 + 0x04e7, reinterpret_cast<void*>(hook_00531f90));

    patch_rel_call(p_4a4a70 + 0x0566, reinterpret_cast<void*>(hook_005a0fbf));
    patch_rel_call(p_4a4a70 + 0x0572, reinterpret_cast<void*>(hook_0059d8e0));
    patch_rel_call(p_4a4a70 + 0x0591, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x05b1, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x05d1, reinterpret_cast<void*>(hook_00563440));
    patch_rel_call(p_4a4a70 + 0x05de, reinterpret_cast<void*>(hook_00531f90));

    patch_rel_call(p_4a4a70 + 0x0621, reinterpret_cast<void*>(hook_005a0fbf));
    patch_rel_call(p_4a4a70 + 0x062b, reinterpret_cast<void*>(hook_0059dc30));
    patch_rel_call(p_4a4a70 + 0x063d, reinterpret_cast<void*>(hook_0059d8e0));
    patch_rel_call(p_4a4a70 + 0x068a, reinterpret_cast<void*>(hook_00562810));
    patch_rel_call(p_4a4a70 + 0x0697, reinterpret_cast<void*>(hook_00531f90));

    patch_rel_call(p_4a4a70 + 0x06cc, reinterpret_cast<void*>(hook_00562680));
    patch_rel_call(p_4a4a70 + 0x072e, reinterpret_cast<void*>(hook_005322b0));
    patch_rel_call(p_4a4a70 + 0x0757, reinterpret_cast<void*>(hook_0048d720));
    auto p_visible = &UiElement::is_visible_00490390;
    auto p_graphic = &UiElement::get_graphic_004903f0;
    void* fn_visible = *reinterpret_cast<void**>(&p_visible);
    void* fn_graphic = *reinterpret_cast<void**>(&p_graphic);
    patch_rel_call(p_4a4a70 + 0x076b, fn_visible);
    patch_rel_call(p_4a4a70 + 0x077c, fn_graphic);
    patch_rel_call(p_4a4a70 + 0x07d1, reinterpret_cast<void*>(hook_00562810));
    patch_rel_call(p_4a4a70 + 0x0849, reinterpret_cast<void*>(hook_00562680));
    patch_rel_call(p_4a4a70 + 0x08af, reinterpret_cast<void*>(hook_00562680));

    patch_rel_call(p_4a4a70 + 0x08de, reinterpret_cast<void*>(hook_005322c0));
    patch_rel_call(p_4a4a70 + 0x08e6, reinterpret_cast<void*>(hook_004b0d70));
    patch_rel_call(p_4a4a70 + 0x0901, reinterpret_cast<void*>(hook_00534540));
    patch_rel_call(p_4a4a70 + 0x0932, reinterpret_cast<void*>(hook_0053d570));
    patch_rel_call(p_4a4a70 + 0x093a, reinterpret_cast<void*>(hook_00534550));
    patch_rel_call(p_4a4a70 + 0x095e, reinterpret_cast<void*>(hook_00533f80));

    return true;
}

static void call_orig_render_screen_driver(std::int32_t step) {
    using FuncType = void(CALL_CDECL*)(std::int32_t);
    auto fn = reinterpret_cast<FuncType>(s_slab);
    fn(step);
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

struct DriverSnapshot {
    char render_en;
    void* canvas;
    std::int32_t mode;
    std::int32_t blend;
    std::int32_t alt;
    std::int32_t text_idx;
};

static void take_snapshot(DriverSnapshot& s) {
    s.render_en = g_render_enabled_00655a28;
    s.canvas = g_render_canvas_00655a24;
    s.mode = g_screen_mode_006573e8;
    s.blend = g_blend_flag_0065742c;
    s.alt = g_alt_flag_00657430;
    s.text_idx = g_loadtext_idx_00657c84;
}

static bool snapshots_equal(const DriverSnapshot& a, const DriverSnapshot& b) {
    return a.render_en == b.render_en &&
           (a.canvas != nullptr) == (b.canvas != nullptr) &&
           a.mode == b.mode &&
           a.blend == b.blend &&
           a.alt == b.alt &&
           a.text_idx == b.text_idx;
}

static void init_mock_structures() {
    // Canvas surface offset 0x28
    *reinterpret_cast<void**>(&s_mock_canvas_buf[0x28]) = reinterpret_cast<void*>(0x8888);

    // Mock FSH file headers
    // BG FSH chunks: 0x14, 0xb4, 0x104, 0x12c, 0x154
    for (int i = 0x14; i <= 0x170; i += 4) {
        *reinterpret_cast<std::int32_t*>(&s_mock_bg_fsh[i]) = 0x200;
    }
    // Car FSH chunks: 0x14, 0x1c, 0x24, 0x2c
    *reinterpret_cast<std::int32_t*>(&s_mock_car_fsh[0x14]) = 0x200;
    *reinterpret_cast<std::int32_t*>(&s_mock_car_fsh[0x1c]) = 0x240;
    *reinterpret_cast<std::int32_t*>(&s_mock_car_fsh[0x24]) = 0x280;
    *reinterpret_cast<std::int32_t*>(&s_mock_car_fsh[0x2c]) = 0x2c0;

    // Load FSH chunks: 0x14, 0x1c, 0x24, 0x2c, 0x34
    for (int i = 0x14; i <= 0x40; i += 4) {
        *reinterpret_cast<std::int32_t*>(&s_mock_load_fsh[i]) = 0x200;
    }

    // Text FSH chunks: 0xc + idx * 8
    for (int i = 0xc; i <= 0x50; i += 8) {
        *reinterpret_cast<std::int32_t*>(&s_mock_text_fsh[i]) = 0x200;
    }

    // Mock graphic at 0x4903f0: offset 4 = chunk, 8 = 10, 0xc = 10
    *reinterpret_cast<std::int32_t*>(&s_mock_graphic[4]) = reinterpret_cast<std::int32_t>(s_mock_car_fsh);
    *reinterpret_cast<std::int32_t*>(&s_mock_graphic[8]) = 10;
    *reinterpret_cast<std::int32_t*>(&s_mock_graphic[0xc]) = 10;
}

bool run_test_case(int case_idx) {
    bool pass = true;

    init_mock_structures();

    g_render_enabled_00655a28 = 0;
    g_render_canvas_00655a24 = nullptr;
    g_display_format_005dead0 = 0;
    g_ui_screen_node_00628c70 = nullptr;
    g_screen_matched_index_0065741c = 0;
    g_skip_render_00657440 = 0;
    g_screen_mode_006573e8 = 0;
    g_screen_suffix_00657444 = 0;
    g_blend_flag_0065742c = 0;
    g_alt_flag_00657430 = 0;
    g_loadtext_idx_00657c84 = 0;
    g_slot_count_00658084 = 0;
    g_screen_width_005deac8 = 640;
    g_screen_height_005deacc = 480;

    s_mock_time_target = 100;
    s_mock_time_current = 100;
    s_mock_theme = 0x20a;
    s_mock_visible = 1;

    static DriverSnapshot snap_orig, snap_cpp;

    switch (case_idx) {
        case 1: {
            // Case 1: step = 0 (first step, creates canvas, sets render_en=1, draws bg)
            g_trace.count = 0;
            call_orig_render_screen_driver(0);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 0;
            g_render_canvas_00655a24 = nullptr;
            g_trace.count = 0;
            render_screen_driver_004a4a70(0);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 2: {
            // Case 2: step = 10 (finalization, frees canvas, render_en=0)
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;

            g_trace.count = 0;
            call_orig_render_screen_driver(10);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_trace.count = 0;
            render_screen_driver_004a4a70(10);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 3: {
            // Case 3: step = 1, render_enabled = 0 (early exit)
            g_render_enabled_00655a28 = 0;
            g_trace.count = 0;
            call_orig_render_screen_driver(1);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 0;
            g_trace.count = 0;
            render_screen_driver_004a4a70(1);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 4: {
            // Case 4: step = 1, render_enabled = 1, skip_render = 1
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_skip_render_00657440 = 1;

            g_trace.count = 0;
            call_orig_render_screen_driver(1);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_skip_render_00657440 = 1;
            g_trace.count = 0;
            render_screen_driver_004a4a70(1);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 5: {
            // Case 5: step = 5, mode = 4 (car showroom era selection), car overlay
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_mode_006573e8 = 4;
            s_mock_theme = 0x20a; // Era 2
            g_blend_flag_0065742c = 1;
            g_alt_flag_00657430 = 0;

            g_trace.count = 0;
            call_orig_render_screen_driver(5);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_mode_006573e8 = 4;
            s_mock_theme = 0x20a;
            g_blend_flag_0065742c = 1;
            g_alt_flag_00657430 = 0;
            g_trace.count = 0;
            render_screen_driver_004a4a70(5);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 6: {
            // Case 6: step = 5, mode = 9 (skips background rendering)
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_mode_006573e8 = 9;

            g_trace.count = 0;
            call_orig_render_screen_driver(5);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_mode_006573e8 = 9;
            g_trace.count = 0;
            render_screen_driver_004a4a70(5);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 7: {
            // Case 7: step = 0, loadtext_idx = 3
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_loadtext_idx_00657c84 = 3;

            g_trace.count = 0;
            call_orig_render_screen_driver(0);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_loadtext_idx_00657c84 = 3;
            g_trace.count = 0;
            render_screen_driver_004a4a70(0);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 8: {
            // Case 8: step = 2, UI screen node valid, 2 element slots (invisible)
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 1;
            node.field_bf = 0;
            node.field_dc = 0;

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_ui_screen_node_00628c70 = &node;
            g_slot_count_00658084 = 2;
            s_mock_visible = 0;

            *reinterpret_cast<std::int32_t*>(&g_slot_table_00658200[0]) = 0;
            *reinterpret_cast<std::int32_t*>(&g_slot_table_00658200[0x580]) = 1;

            g_trace.count = 0;
            call_orig_render_screen_driver(2);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_ui_screen_node_00628c70 = &node;
            g_slot_count_00658084 = 2;
            s_mock_visible = 0;
            g_trace.count = 0;
            render_screen_driver_004a4a70(2);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 9: {
            // Case 9: step = 3, UI screen node valid, 2 element slots (visible graphics)
            UiScreenNode node{};
            node.active_element = reinterpret_cast<void*>(0x1111);
            node.field_be = 1;
            node.field_bf = 0;
            node.field_dc = 1;

            void* dummy_cont = reinterpret_cast<void*>(0x7777);
            void* cont_ptr = &dummy_cont;
            node.container = reinterpret_cast<void**>(cont_ptr);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_ui_screen_node_00628c70 = &node;
            g_slot_count_00658084 = 2;
            s_mock_visible = 1;

            *reinterpret_cast<std::int32_t*>(&g_slot_table_00658200[0]) = 0;
            *reinterpret_cast<std::int32_t*>(&g_slot_table_00658200[0x580]) = 1;
            *reinterpret_cast<std::int32_t*>(&g_slot_table_00658200[0x408]) = 5;

            g_trace.count = 0;
            call_orig_render_screen_driver(3);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_ui_screen_node_00628c70 = &node;
            g_slot_count_00658084 = 2;
            s_mock_visible = 1;
            g_trace.count = 0;
            render_screen_driver_004a4a70(3);
            s_trace_cpp = g_trace;
            take_snapshot(snap_cpp);

            if (!traces_equal(s_trace_orig, s_trace_cpp) || !snapshots_equal(snap_orig, snap_cpp)) {
                log_diff(case_idx, s_trace_orig, s_trace_cpp);
                pass = false;
            }
            break;
        }
        case 10: {
            // Case 10: Full presentation with custom screen size (800x600)
            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_width_005deac8 = 800;
            g_screen_height_005deacc = 600;

            g_trace.count = 0;
            call_orig_render_screen_driver(1);
            s_trace_orig = g_trace;
            take_snapshot(snap_orig);

            g_render_enabled_00655a28 = 1;
            g_render_canvas_00655a24 = s_mock_canvas_buf;
            g_screen_width_005deac8 = 800;
            g_screen_height_005deacc = 600;
            g_trace.count = 0;
            render_screen_driver_004a4a70(1);
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
    exp_dir = ROOT / "local/experiments/v2-app-main-413"
    exp_dir.mkdir(parents=True, exist_ok=True)
    fix_path = exp_dir / "app_main_fixture.cpp"
    fix_path.write_bytes((FIXTURE_CPP).replace("\r\n", "\n").encode("utf-8"))
    print(f"Generated {fix_path}")

if __name__ == "__main__":
    main()

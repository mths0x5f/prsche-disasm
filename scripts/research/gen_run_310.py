"""Generate complete Run 310 files: HPP, CPP, and physical x86 native fixture for WinMain cluster."""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / 'local/game/Porsche.exe'
RUN_DIR = ROOT / 'iterations/v2/001-original-recovery/runs/310-winmain-entry'
EXP_DIR = ROOT / 'local/experiments/v2-app-main-310'

HPP_PATH = RUN_DIR / 'winmain_310.hpp'
CPP_PATH = RUN_DIR / 'winmain_310.cpp'
FIXTURE_PATH = EXP_DIR / 'fixture_310.cpp'


def get_pe_section_data():
    raw = EXE.read_bytes()
    e_lfanew = struct.unpack_from('<I', raw, 0x3c)[0]
    opt_hdr = e_lfanew + 24
    image_base = struct.unpack_from('<I', raw, opt_hdr + 28)[0]
    num_sections = struct.unpack_from('<H', raw, e_lfanew + 6)[0]
    sec_hdr_start = opt_hdr + struct.unpack_from('<H', raw, e_lfanew + 20)[0]
    sections = []
    for i in range(num_sections):
        sec = raw[sec_hdr_start + i * 40 : sec_hdr_start + (i + 1) * 40]
        vsize, vrva, rsize, rraw = struct.unpack_from('<IIII', sec, 8)
        sections.append((image_base + vrva, vsize, rraw, rsize))

    def va_to_raw(va):
        for s_va, s_vsize, rraw, rsize in sections:
            if s_va <= va < s_va + max(s_vsize, rsize):
                return rraw + (va - s_va)
        return None

    return raw, va_to_raw


def generate_hpp():
    content = """// Run 310 — WinMain and companion pre-WinMain initializers
// Original Porsche.exe:
//   004b66d0..004b66e4 (20 bytes)  winmain_set_heap_size_004b66d0
//   004b66f0..004b6703 (19 bytes)  winmain_compute_scale_004b66f0
//   004b6710..004b67a5 (149 bytes) winmain_004b6710
#ifndef PORSCHE_WINMAIN_310_HPP
#define PORSCHE_WINMAIN_310_HPP

#include <cstdint>

namespace porsche {

extern "C" {
    // 004b66d0 (20 bytes) — sets global heap buffer size (0x800000 = 8MB)
    void winmain_set_heap_size_004b66d0(void);

    // 004b66f0 (19 bytes) — computes float scale reciprocal 1.0f / *(float*)0x65b290
    void winmain_compute_scale_004b66f0(void);

    // 004b6710 (149 bytes) — WinMain standard entry point
    int __stdcall winmain_004b6710(void* hInstance, void* hPrevInstance, char* lpCmdLine, int nShowCmd);
}

} // namespace porsche

#endif // PORSCHE_WINMAIN_310_HPP
"""
    HPP_PATH.parent.mkdir(parents=True, exist_ok=True)
    HPP_PATH.write_text(content.replace('\r\n', '\n'), encoding='utf8', newline='\n')


def generate_cpp():
    content = """// Run 310 — WinMain and pre-WinMain initializers implementation
#include "winmain_310.hpp"

namespace porsche {

extern "C" {
    // Read-only literals
    extern const float g_float_one_005b24a8;       // 0x005b24a8 (1.0f)
    extern const char g_str_app_name_005d6e34[8];  // 0x005d6e34 ("AppName")

    // Mutable state
    extern char* g_argv_0065b20c[32];              // 0x0065b20c (argv pointer array)
    extern float g_float_scale_0065b28c;           // 0x0065b28c
    extern uint32_t g_heap_size_0065b290;          // 0x0065b290
    extern int g_argc_0065b294;                    // 0x0065b294

    // External callee
    int __cdecl app_main_004b6a50(int argc, char** argv);
}

// 004b66d0 (20 bytes)
// Emitted as: push ecx; mov [esp], 0x800000; mov eax, [esp]; mov [0x65b290], eax; pop ecx; ret
extern "C" void winmain_set_heap_size_004b66d0(void) {
    g_heap_size_0065b290 = 0x800000;
}

// 004b66f0 (19 bytes)
// Emitted as: fld [0x5b24a8]; fdiv [0x65b290]; fstp [0x65b28c]; ret
extern "C" void winmain_compute_scale_004b66f0(void) {
    g_float_scale_0065b28c = g_float_one_005b24a8 / *(const float*)&g_heap_size_0065b290;
}

// 004b6710 (149 bytes)
// Standard WinMain: initializes argv[0] with "AppName", parses lpCmdLine splitting by ' ',
// fills g_argv array and invokes app_main_004b6a50(g_argc, g_argv)
extern "C" int __stdcall winmain_004b6710(void* hInstance, void* hPrevInstance, char* lpCmdLine, int nShowCmd) {
    (void)hInstance;
    (void)hPrevInstance;
    (void)nShowCmd;

    char app_name_buf[8];
    *(uint32_t*)&app_name_buf[0] = *(const uint32_t*)&g_str_app_name_005d6e34[0];
    *(uint32_t*)&app_name_buf[4] = *(const uint32_t*)&g_str_app_name_005d6e34[4];

    g_argv_0065b20c[0] = app_name_buf;
    int argc = 1;
    g_argc_0065b294 = 1;

    char* p = lpCmdLine;
    if (p != nullptr && *p != '\\0') {
        while (argc < 32) {
            // Skip and clear leading spaces
            if (*p == ' ') {
                do {
                    *p = '\\0';
                    p++;
                } while (*p != '\\0' && *p == ' ');
            }

            if (*p != '\\0') {
                g_argv_0065b20c[argc] = p;
                argc++;
                g_argc_0065b294 = argc;
            }

            if (*p != '\\0' && *p != ' ') {
                do {
                    p++;
                } while (*p != '\\0' && *p != ' ');
            }

            if (*p == '\\0') {
                break;
            }
        }
    }

    return app_main_004b6a50(argc, g_argv_0065b20c);
}

} // namespace porsche
"""
    CPP_PATH.write_text(content.replace('\r\n', '\n'), encoding='utf8', newline='\n')


def generate_fixture():
    raw, va_to_raw = get_pe_section_data()

    # Raw bytes of the 3 functions
    code_66d0 = raw[va_to_raw(0x004b66d0) : va_to_raw(0x004b66d0) + 20]
    code_66f0 = raw[va_to_raw(0x004b66f0) : va_to_raw(0x004b66f0) + 19]
    code_6710 = raw[va_to_raw(0x004b6710) : va_to_raw(0x004b6710) + 149]

    fixture_content = f"""// Controlled native x86 differential fixture for Run 310 (WinMain cluster)
#include <windows.h>
#include <cstdint>
#include "winmain_310.hpp"

// Intrinsic replacements for MSVC /NODEFAULTLIB mode
extern "C" {{
    int _fltused = 0x9875;

    #pragma function(memset)
    void* memset(void* dst, int val, size_t count) {{
        volatile char* p = (volatile char*)dst;
        while (count--) {{
            *p++ = (char)val;
        }}
        return dst;
    }}

    #pragma function(memcpy)
    void* memcpy(void* dst, const void* src, size_t count) {{
        volatile char* d = (volatile char*)dst;
        const volatile char* s = (const volatile char*)src;
        while (count--) {{
            *d++ = *s++;
        }}
        return dst;
    }}
}}

static int my_memcmp(const void* a, const void* b, size_t n) {{
    const uint8_t* p1 = (const uint8_t*)a;
    const uint8_t* p2 = (const uint8_t*)b;
    for (size_t i = 0; i < n; ++i) {{
        if (p1[i] != p2[i]) return (int)p1[i] - (int)p2[i];
    }}
    return 0;
}}

static void my_strcpy(char* dst, const char* src) {{
    while ((*dst++ = *src++) != '\\0');
}}

static void my_strncpy(char* dst, const char* src, size_t max_len) {{
    size_t i = 0;
    while (i < max_len && src[i] != '\\0') {{
        dst[i] = src[i];
        i++;
    }}
    if (i < max_len) dst[i] = '\\0';
    else dst[max_len - 1] = '\\0';
}}

static int my_strcmp(const char* a, const char* b) {{
    while (*a && (*a == *b)) {{ a++; b++; }}
    return *(const unsigned char*)a - *(const unsigned char*)b;
}}

// Globals used by C++ implementation
extern "C" {{
    extern const float g_float_one_005b24a8 = 1.0f;
    extern const char g_str_app_name_005d6e34[8] = {{ 'A','p','p','N','a','m','e','\\0' }};

    char* g_argv_0065b20c[32];
    float g_float_scale_0065b28c = 0.0f;
    uint32_t g_heap_size_0065b290 = 0;
    int g_argc_0065b294 = 0;

    // Call logging for C++ execution
    int g_cpp_app_main_called = 0;
    int g_cpp_captured_argc = 0;
    char g_cpp_captured_argv[32][128];
    int g_mock_app_main_retval = 0x4242;

    int __cdecl app_main_004b6a50(int argc, char** argv) {{
        g_cpp_app_main_called++;
        g_cpp_captured_argc = argc;
        for (int i = 0; i < argc && i < 32; ++i) {{
            if (argv[i]) {{
                my_strncpy(g_cpp_captured_argv[i], argv[i], 127);
            }} else {{
                g_cpp_captured_argv[i][0] = '\\0';
            }}
        }}
        return g_mock_app_main_retval;
    }}
}}

// Mock memory environment for Original PE slab execution
namespace orig_env {{
    float s_float_one = 1.0f;
    char s_str_app_name[8] = {{ 'A','p','p','N','a','m','e','\\0' }};

    char* s_argv[32];
    float s_float_scale = 0.0f;
    uint32_t s_heap_size = 0;
    int s_argc = 0;

    int s_orig_app_main_called = 0;
    int s_orig_captured_argc = 0;
    char s_orig_captured_argv[32][128];

    extern "C" int __cdecl orig_mock_app_main(int argc, char** argv) {{
        s_orig_app_main_called++;
        s_orig_captured_argc = argc;
        for (int i = 0; i < argc && i < 32; ++i) {{
            if (argv[i]) {{
                my_strncpy(s_orig_captured_argv[i], argv[i], 127);
            }} else {{
                s_orig_captured_argv[i][0] = '\\0';
            }}
        }}
        return g_mock_app_main_retval;
    }}
}}

// Byte arrays for original PE functions
static const uint8_t s_orig_66d0[20] = {{ {', '.join(f'0x{b:02x}' for b in code_66d0)} }};
static const uint8_t s_orig_66f0[19] = {{ {', '.join(f'0x{b:02x}' for b in code_66f0)} }};
static const uint8_t s_orig_6710[149] = {{ {', '.join(f'0x{b:02x}' for b in code_6710)} }};

// Executable memory slab
static uint8_t* s_slab_66d0 = nullptr;
static uint8_t* s_slab_66f0 = nullptr;
static uint8_t* s_slab_6710 = nullptr;

static void setup_slabs() {{
    uint8_t* mem = (uint8_t*)VirtualAlloc(nullptr, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!mem) {{
        ExitProcess(101);
    }}

    s_slab_66d0 = mem;
    s_slab_66f0 = mem + 0x40;
    s_slab_6710 = mem + 0x80;

    memcpy(s_slab_66d0, s_orig_66d0, sizeof(s_orig_66d0));
    memcpy(s_slab_66f0, s_orig_66f0, sizeof(s_orig_66f0));
    memcpy(s_slab_6710, s_orig_6710, sizeof(s_orig_6710));

    // Relocate 66d0:
    // at off 0x0e: mov [0x65b290], eax -> patch to orig_env::s_heap_size
    *(uint32_t*)(s_slab_66d0 + 0x0e) = (uint32_t)&orig_env::s_heap_size;

    // Relocate 66f0:
    // at off 0x02: fld [0x5b24a8] -> &orig_env::s_float_one
    // at off 0x08: fdiv [0x65b290] -> &orig_env::s_heap_size
    // at off 0x0e: fstp [0x65b28c] -> &orig_env::s_float_scale
    *(uint32_t*)(s_slab_66f0 + 0x02) = (uint32_t)&orig_env::s_float_one;
    *(uint32_t*)(s_slab_66f0 + 0x08) = (uint32_t)&orig_env::s_heap_size;
    *(uint32_t*)(s_slab_66f0 + 0x0e) = (uint32_t)&orig_env::s_float_scale;

    // Relocate 6710:
    // 0x04: mov eax, [0x5d6e34] -> &orig_env::s_str_app_name[0]
    // 0x0a: mov ecx, [0x5d6e38] -> &orig_env::s_str_app_name[4]
    // 0x17: mov [0x65b20c], eax -> &orig_env::s_argv[0]
    // 0x2c: mov [0x65b294], edx -> &orig_env::s_argc
    // 0x56: mov edx, [0x65b294] -> &orig_env::s_argc
    // 0x61: mov [edx*4 + 0x65b20c], eax -> &orig_env::s_argv[0]
    // 0x68: mov [0x65b294], edx -> &orig_env::s_argc
    // 0x85: push 0x65b20c -> &orig_env::s_argv[0]
    // 0x8b: call 0x4b6a50 -> relative call to orig_env::orig_mock_app_main
    *(uint32_t*)(s_slab_6710 + 0x04) = (uint32_t)&orig_env::s_str_app_name[0];
    *(uint32_t*)(s_slab_6710 + 0x0a) = (uint32_t)&orig_env::s_str_app_name[4];
    *(uint32_t*)(s_slab_6710 + 0x17) = (uint32_t)&orig_env::s_argv[0];
    *(uint32_t*)(s_slab_6710 + 0x2c) = (uint32_t)&orig_env::s_argc;
    *(uint32_t*)(s_slab_6710 + 0x56) = (uint32_t)&orig_env::s_argc;
    *(uint32_t*)(s_slab_6710 + 0x61) = (uint32_t)&orig_env::s_argv[0];
    *(uint32_t*)(s_slab_6710 + 0x68) = (uint32_t)&orig_env::s_argc;
    *(uint32_t*)(s_slab_6710 + 0x85) = (uint32_t)&orig_env::s_argv[0];

    // CALL at 0x8a is 5 bytes: e8 <rel32>
    uint8_t* call_site = s_slab_6710 + 0x8a;
    uint32_t target = (uint32_t)&orig_env::orig_mock_app_main;
    uint32_t rel = target - ((uint32_t)call_site + 5);
    *(uint32_t*)(call_site + 1) = rel;
}}

typedef void (*fn_void_t)(void);
typedef int (__stdcall *fn_winmain_t)(void*, void*, char*, int);

static void test_66d0() {{
    orig_env::s_heap_size = 0x12345678;
    g_heap_size_0065b290 = 0x12345678;

    ((fn_void_t)s_slab_66d0)();
    porsche::winmain_set_heap_size_004b66d0();

    if (orig_env::s_heap_size != 0x800000 || g_heap_size_0065b290 != 0x800000) {{
        ExitProcess(1);
    }}
}}

static void test_66f0() {{
    orig_env::s_float_one = 1.0f;
    orig_env::s_heap_size = 0x800000;
    orig_env::s_float_scale = 0.0f;

    g_heap_size_0065b290 = 0x800000;
    g_float_scale_0065b28c = 0.0f;

    ((fn_void_t)s_slab_66f0)();
    porsche::winmain_compute_scale_004b66f0();

    if (my_memcmp(&orig_env::s_float_scale, &g_float_scale_0065b28c, sizeof(float)) != 0) {{
        ExitProcess(2);
    }}
}}

struct TestCase {{
    const char* cmdline;
    int expected_argc;
}};

static const TestCase s_cases[10] = {{
    {{ "", 1 }},
    {{ "   ", 1 }},
    {{ "-nomusic", 2 }},
    {{ "  -nomusic  ", 2 }},
    {{ "-nomusic -window -debug", 4 }},
    {{ "-car 911 -track 01 -laps 5 -opponents 7", 9 }},
    {{ "     -single", 2 }},
    {{ "test", 2 }},
    {{ "-a -b -c -d -e", 6 }},
    {{ "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35", 32 }},
}};

static void test_winmain_cases() {{
    for (int i = 0; i < 10; ++i) {{
        char orig_cmd[512];
        char cpp_cmd[512];
        memset(orig_cmd, 0, sizeof(orig_cmd));
        memset(cpp_cmd, 0, sizeof(cpp_cmd));
        my_strcpy(orig_cmd, s_cases[i].cmdline);
        my_strcpy(cpp_cmd, s_cases[i].cmdline);

        g_mock_app_main_retval = 0x1000 + i;

        orig_env::s_orig_app_main_called = 0;
        orig_env::s_orig_captured_argc = 0;
        memset(orig_env::s_orig_captured_argv, 0, sizeof(orig_env::s_orig_captured_argv));
        memset(orig_env::s_argv, 0, sizeof(orig_env::s_argv));
        orig_env::s_argc = 0;

        g_cpp_app_main_called = 0;
        g_cpp_captured_argc = 0;
        memset(g_cpp_captured_argv, 0, sizeof(g_cpp_captured_argv));
        memset(g_argv_0065b20c, 0, sizeof(g_argv_0065b20c));
        g_argc_0065b294 = 0;

        int orig_ret = ((fn_winmain_t)s_slab_6710)((void*)0x400000, nullptr, orig_cmd, 1);
        int cpp_ret = porsche::winmain_004b6710((void*)0x400000, nullptr, cpp_cmd, 1);

        if (orig_ret != cpp_ret || orig_ret != g_mock_app_main_retval) {{
            ExitProcess(10 + i);
        }}
        if (orig_env::s_orig_app_main_called != 1 || g_cpp_app_main_called != 1) {{
            ExitProcess(20 + i);
        }}
        if (orig_env::s_orig_captured_argc != g_cpp_captured_argc ||
            orig_env::s_orig_captured_argc != s_cases[i].expected_argc) {{
            ExitProcess(30 + i);
        }}
        if (orig_env::s_argc != g_argc_0065b294 || orig_env::s_argc != s_cases[i].expected_argc) {{
            ExitProcess(40 + i);
        }}
        for (int a = 0; a < s_cases[i].expected_argc; ++a) {{
            if (my_strcmp(orig_env::s_orig_captured_argv[a], g_cpp_captured_argv[a]) != 0) {{
                ExitProcess(50 + i);
            }}
        }}
        // Compare buffer modifications (spaces converted to '\\0')
        if (my_memcmp(orig_cmd, cpp_cmd, sizeof(orig_cmd)) != 0) {{
            ExitProcess(60 + i);
        }}
    }}
}}

extern "C" int entry(void) {{
    setup_slabs();
    test_66d0();
    test_66f0();
    test_winmain_cases();
    ExitProcess(0);
}}
"""
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(fixture_content.replace('\r\n', '\n'), encoding='utf8', newline='\n')


def main():
    generate_hpp()
    generate_cpp()
    generate_fixture()
    print('Generated HPP, CPP and FIXTURE for Run 310 successfully.')


if __name__ == '__main__':
    main()

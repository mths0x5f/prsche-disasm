// Run 415 — WinMain and pre-WinMain initializers implementation
#include "winmain_415.hpp"

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
    if (p != nullptr && *p != '\0') {
        while (argc < 32) {
            // Skip and clear leading spaces
            if (*p == ' ') {
                do {
                    *p = '\0';
                    p++;
                } while (*p != '\0' && *p == ' ');
            }

            if (*p != '\0') {
                g_argv_0065b20c[argc] = p;
                argc++;
                g_argc_0065b294 = argc;
            }

            if (*p != '\0' && *p != ' ') {
                do {
                    p++;
                } while (*p != '\0' && *p != ' ');
            }

            if (*p == '\0') {
                break;
            }
        }
    }

    return app_main_004b6a50(argc, g_argv_0065b20c);
}

} // namespace porsche

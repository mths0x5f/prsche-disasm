#ifndef PORSCHE_APP_MAIN_RENDER_SCREEN_DRIVER_413_HPP
#define PORSCHE_APP_MAIN_RENDER_SCREEN_DRIVER_413_HPP

#include <cstdint>
#include <cstddef>

#ifndef CALL_CDECL
#define CALL_CDECL __cdecl
#endif

#ifndef CALL_STDCALL
#define CALL_STDCALL __stdcall
#endif

#ifndef CALL_THISCALL
#define CALL_THISCALL __thiscall
#endif

#ifndef CALL_FASTCALL
#define CALL_FASTCALL __fastcall
#endif

namespace porsche {

#pragma pack(push, 1)

struct UiScreenNode {
    std::uint32_t mode_0_flag;     // 0x00
    std::uint32_t mode_1_flag;     // 0x04
    void* active_element;          // 0x08
    void* manager;                 // 0x0c
    void** container;              // 0x10
    std::uint8_t pad_14[0x18];     // 0x14..0x2b
    char name[32];                 // 0x2c..0x4b
    std::uint8_t pad_4c[0x70];     // 0x4c..0xbb
    std::uint8_t field_bc;         // 0xbc
    std::uint8_t field_bd;         // 0xbd
    std::uint8_t field_be;         // 0xbe
    std::uint8_t field_bf;         // 0xbf
    std::uint8_t pad_c0[4];        // 0xc0..0xc3
    std::uint8_t field_c4;         // 0xc4
    std::uint8_t field_c5;         // 0xc5
    std::uint8_t pad_c6[0x16];     // 0xc6..0xdb
    std::int32_t field_dc;         // 0xdc
};

#pragma pack(pop)

// 004a4a70 (2,424 bytes): Screen render driver, loading art presentation, background strips, and display flip
void CALL_CDECL render_screen_driver_004a4a70(std::int32_t step);

extern "C" {
    extern char g_render_enabled_00655a28;
    extern void* g_render_canvas_00655a24;
    extern std::int32_t g_display_format_005dead0;
    extern UiScreenNode* g_ui_screen_node_00628c70;
    extern std::int32_t g_screen_matched_index_0065741c;
    extern std::int32_t g_skip_render_00657440;
    extern std::int32_t g_screen_mode_006573e8;
    extern const char* g_fsh_path_0065b350;
    extern char g_screen_suffix_00657444;
    extern const char* g_fsh_dir_0065b334;
    extern std::int32_t g_blend_flag_0065742c;
    extern std::int32_t g_alt_flag_00657430;
    extern std::int32_t g_loadtext_idx_00657c84;
    extern std::int32_t g_slot_count_00658084;
    extern std::uint8_t g_slot_table_00658200[0x580 * 16];
    extern std::int32_t g_screen_width_005deac8;
    extern std::int32_t g_screen_height_005deacc;

    // Driver function pointers
    extern void (CALL_STDCALL *g_driver_fn_006bd9b0)(std::int32_t);
    extern void (CALL_STDCALL *g_driver_fn_006bd91c)();
    extern void (CALL_STDCALL *g_driver_fn_006bd978)(std::int32_t);
    extern void (CALL_STDCALL *g_driver_fn_006bd948)();

    // Subsystem calls
    void* CALL_CDECL hook_00535950(std::int32_t w, std::int32_t h, std::int32_t format, std::int32_t bpp);
    void CALL_CDECL hook_004edc00(std::int32_t opcode, void** p_stream, std::int32_t id, std::int32_t step);
    void CALL_CDECL hook_0048d550(const std::int32_t* packet);
    std::int32_t CALL_CDECL hook_004ad670();
    std::int32_t CALL_CDECL hook_004ad6c0();
    void CALL_CDECL hook_005366e0(std::int32_t a1);
    void CALL_CDECL hook_00534480(void* canvas);
    std::int32_t CALL_CDECL hook_0059dc30(const char* filename);
    std::uint8_t* CALL_CDECL hook_0059d8e0(const char* filename, std::int32_t mode);
    std::int32_t CALL_CDECL hook_005032d0();
    void CALL_CDECL hook_00563440(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h);
    void CALL_CDECL hook_00563320(void* chunk);
    void CALL_CDECL hook_00563160(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h);
    void CALL_CDECL hook_00531f90(void* ptr);
    void CALL_CDECL hook_00562810(void* chunk, std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h);
    void CALL_CDECL hook_00562680(std::int32_t x, std::int32_t y, std::int32_t w, std::int32_t h, std::uint32_t color);
    void CALL_CDECL hook_005322b0(void* container);
    std::uint8_t* CALL_CDECL hook_0048d720(std::int32_t index);
}

struct UiElement {
    char CALL_THISCALL is_visible_00490390();
    std::uint8_t* CALL_THISCALL get_graphic_004903f0(std::int32_t a1);
};

extern "C" {
    void CALL_CDECL hook_005322c0(void* container);
    void CALL_CDECL hook_004b0d70();
    void CALL_CDECL hook_00534540();
    void CALL_CDECL hook_0053d570(void* surf, std::int32_t x, std::int32_t y);
    void CALL_CDECL hook_00534550();
    void CALL_CDECL hook_00533f80(void* canvas);
    int CALL_CDECL hook_005a0fbf(char* dst, const char* fmt, ...);
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_RENDER_SCREEN_DRIVER_413_HPP

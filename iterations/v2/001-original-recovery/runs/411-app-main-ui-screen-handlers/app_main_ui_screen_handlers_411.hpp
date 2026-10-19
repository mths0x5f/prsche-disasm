#ifndef PORSCHE_APP_MAIN_UI_SCREEN_HANDLERS_411_HPP
#define PORSCHE_APP_MAIN_UI_SCREEN_HANDLERS_411_HPP

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

// =============================================================================
// UI Subsystem Structures
// =============================================================================

#pragma pack(push, 1)

struct UiScreenNode {
    std::uint32_t mode_0_flag;     // 0x00
    std::uint32_t mode_1_flag;     // 0x04
    void* active_element;          // 0x08
    void* manager;                 // 0x0c
    void* container;               // 0x10
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

struct UiScreenContext {
    std::uint32_t field_0;         // 0x00
    std::uint32_t field_4;         // 0x04
    void* field_8;                 // 0x08
    void* field_c;                 // 0x0c
    void* field_10;                // 0x10
    void* field_14;                // 0x14
    std::uint32_t field_18;        // 0x18
    std::uint32_t field_1c;        // 0x1c
    std::uint32_t pad_20;          // 0x20
    std::uint32_t field_24;        // 0x24
    std::uint32_t field_28;        // 0x28
    std::uint8_t pad_2c[0x2c];     // 0x2c..0x57
    char field_58[32];             // 0x58..0x77
    std::uint8_t pad_78[0x20];     // 0x78..0x97
    char field_98[16];             // 0x98..0xa7
    char field_a8[22];             // 0xa8..0xbd
    std::uint8_t field_be;         // 0xbe
    std::uint8_t field_bf;         // 0xbf
    std::uint8_t field_c0;         // 0xc0
    std::uint8_t field_c1;         // 0xc1
    std::uint8_t field_c2;         // 0xc2
    std::uint8_t pad_c3[3];        // 0xc3..0xc5
    std::uint8_t field_c6;         // 0xc6
    std::uint8_t field_c7;         // 0xc7
    std::uint8_t pad_c8[0x18];     // 0xc8..0xdf
    std::uint32_t field_e0;        // 0xe0
    std::uint8_t pad_e4;           // 0xe4
    std::uint8_t field_e5;         // 0xe5
    std::uint8_t field_e6;         // 0xe6
    std::uint8_t field_e7;         // 0xe7
    std::uint8_t pad_e8[0x1e];     // 0xe8..0x105
    std::uint8_t field_106;        // 0x106
    std::uint8_t pad_107[0x41];    // 0x107..0x147
    std::uint32_t field_148;       // 0x148
    std::uint8_t pad_14c[0x108];   // 0x14c..0x253
    void* field_254;               // 0x254
    std::uint32_t pad_258;         // 0x258
    void* field_25c;               // 0x25c

    // 0048cdf0 (1,364 bytes): UI screen tree draw and frame state advance
    std::uint8_t CALL_THISCALL ui_draw_screen_tree_0048cdf0();

    // 0048dcb0 (1,250 bytes): UI screen refresh and layout coordinator
    void CALL_THISCALL ui_screen_refresh_0048dcb0(const char* title, std::uint32_t param2);

    // 0048e1a0 (1,357 bytes): UI screen render, child list traversal & presentation
    void CALL_THISCALL ui_screen_render_present_0048e1a0(std::uint32_t mode, std::uint32_t id, const char* title);
};

struct MockCallees {
    void CALL_THISCALL sub_0048c870(std::uint32_t a1, std::uint32_t a2, std::uint32_t a3, std::uint32_t a4, std::uint32_t a5);
    void CALL_THISCALL sub_0048d350(std::uint32_t a1, std::int32_t a2, std::int32_t a3, std::uint32_t a4);
    void CALL_THISCALL sub_0048dbe0();
    void CALL_THISCALL sub_0048e9c0();
    void CALL_THISCALL sub_0048dbb0();
    void CALL_THISCALL sub_0048aa10(std::uint32_t a1, void* a2, void* a3, const char* a4, void* a5, const char* a6, void* a7, std::uint32_t a8);
    void CALL_THISCALL sub_00491cd0(std::uint32_t a1, void* a2, void* a3, std::uint32_t a4, std::uint32_t a5, std::int32_t a6);
    void* CALL_THISCALL sub_004931c0(void* a1);
    void CALL_THISCALL sub_0048ac70(void* a1);
    void CALL_THISCALL sub_0048ac50();
    void CALL_THISCALL sub_0048ac90(void* a1, std::uint32_t a2);
    void CALL_THISCALL sub_0048c840(std::uint32_t a1, std::uint32_t a2);
    void* CALL_THISCALL sub_00529050(void* a1);
    void CALL_THISCALL sub_0050e140(void* a1);
    void CALL_THISCALL sub_004937f0(void* a1);
};

#pragma pack(pop)

// =============================================================================
// Global Subsystem Variables
// =============================================================================
extern "C" {
    extern UiScreenNode* g_ui_screen_node_00628c70;
    extern std::uint32_t g_dword_00628c74;
    extern std::uint32_t g_dword_00657aa4;
    extern std::uint8_t  g_byte_005d0728;
    extern std::uint32_t g_dword_005b4980;
    extern std::uint32_t g_dword_005b4990;
    extern std::uint32_t g_dword_00508e70;
    extern std::uint32_t (CALL_STDCALL *g_pfn_005b2080)();
    void CALL_CDECL sub_0048da60(std::int32_t a1, std::int32_t a2);
}

// C wrapper functions for interoperability
extern "C" {
    inline std::uint8_t ui_draw_screen_tree_0048cdf0(UiScreenContext* self) {
        return self->ui_draw_screen_tree_0048cdf0();
    }
    inline void ui_screen_refresh_0048dcb0(UiScreenContext* self, const char* title, std::uint32_t param2) {
        self->ui_screen_refresh_0048dcb0(title, param2);
    }
    inline void ui_screen_render_present_0048e1a0(UiScreenContext* self, std::uint32_t mode, std::uint32_t id, const char* title) {
        self->ui_screen_render_present_0048e1a0(mode, id, title);
    }
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_UI_SCREEN_HANDLERS_411_HPP

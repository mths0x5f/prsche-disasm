#ifndef PORSCHE_APP_MAIN_FRAME_EVENT_PUMP_307_HPP
#define PORSCHE_APP_MAIN_FRAME_EVENT_PUMP_307_HPP

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

struct UiElementData {
    std::uint8_t pad_00[0x40];     // 0x00..0x3f
    std::int32_t element_id;       // 0x40
    std::uint8_t pad_44[8];        // 0x44..0x4b
    std::int32_t mapped_index;     // 0x4c
};

struct UiElementNode {
    UiElementNode* next;           // 0x00
    UiElementNode* prev;           // 0x04
    UiElementData* element_data;   // 0x08
};

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
    std::uint8_t pad_e0[5];        // 0xe0..0xe4
    std::uint8_t field_e5;         // 0xe5
    std::uint8_t pad_e6[0x17a];    // 0xe6..0x25f
    UiElementNode* child_list_head;// 0x260
};

#pragma pack(pop)

// 004b4da0 (1,078 bytes): Frame event pump, screen mode 3 tree traversal & event dispatch
void CALL_CDECL frame_event_pump_004b4da0(std::int32_t* event_stream);

// Global state referenced by 004b4da0
extern "C" {
    extern UiScreenNode* g_ui_screen_node_00628c70;
    extern std::uint8_t g_screen_buffer_006573e8[0x3e24];
    extern const char g_str_unknown_005d638c[];
    extern std::uint32_t g_input_flag_005d1734;
    extern std::uint32_t g_input_out_005d1740;
    extern std::uint32_t g_input_out_005d1744;
    extern std::uint32_t g_input_out_005d1748;
    extern std::uint32_t g_input_out_005d174c;
    extern std::uint32_t g_input_out_005d1750;

    // Subsystem functions called by 004b4da0
    void CALL_CDECL hook_00412e00();
    void CALL_CDECL hook_004b6560(std::int32_t* stream);
    void CALL_CDECL hook_004b6600(std::int32_t* stream);
    void CALL_CDECL hook_004b4b80(const std::uint32_t* packet);
    std::int32_t CALL_CDECL hook_004b4cd0(const std::uint32_t* packet);
    void CALL_CDECL hook_0048d3d0();
    char CALL_CDECL hook_0048caa0();
    void CALL_CDECL hook_0048d490(const std::int32_t* packet);
    void CALL_CDECL hook_0048d440();
    void CALL_CDECL hook_0048d6a0();
    void CALL_CDECL hook_0053c380(std::int32_t ms);
    void CALL_CDECL hook_00411760();
    int CALL_CDECL hook_005a17c9();
}

} // namespace porsche

#endif // PORSCHE_APP_MAIN_FRAME_EVENT_PUMP_307_HPP

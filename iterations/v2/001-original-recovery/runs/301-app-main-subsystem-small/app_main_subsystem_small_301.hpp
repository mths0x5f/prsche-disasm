#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// -----------------------------------------------------------------------------
// Function 1: 0048e6f0 (153 PE body bytes)
// Input device / event router poll and mode switch helper.
// -----------------------------------------------------------------------------
extern void* g_input_mgr_00628c70;

void __stdcall post_input_event_0048e1a0(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);
void* __cdecl operator_delete_0059f050(void* ptr);

struct SubObject_004935c0 {
    void __thiscall cleanup_004935c0();
};

struct InputHandle_0048c870 {
    void __thiscall dispatch_input_cmd_0048c870(std::uint32_t cmd, std::uint32_t p1, std::uint32_t p2, std::uint32_t p3, std::uint32_t p4);
};

struct InputDevice_0048e6f0 {
    std::uint8_t pad_00[0x0c];
    InputHandle_0048c870* handle_0c;      // offset 0x0c
    std::uint8_t pad_10[0x04];           // offset 0x10
    SubObject_004935c0* sub_object_14;    // offset 0x14
    std::uint8_t pad_18[0x10];           // offset 0x18
    std::uint32_t mode_28;                // offset 0x28
    std::uint8_t pad_2c[0x9a];           // offset 0x2c
    std::uint8_t flag_c6;                 // offset 0xc6

    void __thiscall sub_0048e9c0();
    void __thiscall update_mode_0048e6f0();
};

// -----------------------------------------------------------------------------
// Function 2: 004a6960 (153 PE body bytes)
// Frame sync latency and presentation sleep throttler.
// -----------------------------------------------------------------------------
extern void* g_stream_ptr_00656518;
extern std::uint32_t g_stream_id_00656510;
extern std::uint32_t g_render_flag_005d1734;
extern std::uint32_t g_render_flag_005d1738;
extern void* g_render_ptr_00655d44;
extern const char g_throttle_tag_005d1400[];

void __cdecl time_delay_005659f0(std::int32_t ms);
void __cdecl stream_destroy_00531f90(void* stream);
void __cdecl render_sync_004ae310();
void __cdecl render_cycle_004ab4b0();
std::uint32_t __cdecl get_time_delta_00565890();
void __cdecl throttle_sleep_005a177b(const void* tag, std::uint32_t ms);

void __cdecl application_main_function_004a6960();

// -----------------------------------------------------------------------------
// Function 3: 004a5410 (157 PE body bytes)
// Subsystem startup memory and timer initialization dispatcher.
// -----------------------------------------------------------------------------
extern void* g_heap_hook_005debf0;
extern void* g_subsystem_mgr_00628c70;
extern const void* const g_heap_default_table_0059fbc0;

void __cdecl heap_init_0059e9d0(std::uint32_t a, std::uint32_t b, std::uint32_t c, std::uint32_t d);
void __cdecl heap_reserve_0059edb0(std::uint32_t size, std::uint32_t flags);
void __cdecl sys_alloc_00565030(std::uint32_t size);
void* __cdecl operator_new_0059ef90(std::uint32_t size);

struct InputManager_0048fc80 {
    InputManager_0048fc80* __thiscall ctor_0048fc80();
};

void __cdecl sys_service_0055fcf0();
void __cdecl sys_service_00564e70();
void __cdecl sys_service_00564ab0();
void __cdecl sys_service_00564850(std::uint32_t mode);
void __cdecl timer_init_00536e50();
void __cdecl timer_register_005367b0(std::uint32_t id, std::uint32_t period, std::uint32_t flags);
void __cdecl packet_init_004b6ff0();
void __cdecl window_channel_init_00563ad0(std::uint32_t ch, std::uint32_t size, std::uint32_t flags);

void __cdecl application_main_function_004a5410();

// -----------------------------------------------------------------------------
// Function 4: 004d1a90 (172 PE body bytes)
// SoundContext object constructor and default device configuration.
// -----------------------------------------------------------------------------
extern const char g_default_sound_device_005e8e50[];
extern const void* const g_sound_vtable_005b683c;

struct SoundBase_00525e20 {
    void __thiscall init_00525e20();
};

struct SoundSubDevice_005294c0 {
    SoundSubDevice_005294c0* __thiscall ctor_005294c0();
};

struct SoundContext_004d1a90 {
    const void* vtable;                      // offset 0x00
    std::uint8_t pad_04[0xd0];
    SoundSubDevice_005294c0* sub_device_d4;  // offset 0xd4
    std::uint8_t pad_d8[0x08];
    std::uint32_t field_e0;                 // offset 0xe0
    std::uint32_t field_e4;                 // offset 0xe4
    std::uint32_t field_e8;                 // offset 0xe8
    std::uint8_t pad_ec[0x0c];
    std::uint32_t field_f8;                 // offset 0xf8
    std::uint32_t field_fc;                 // offset 0xfc
    std::uint32_t field_100;                // offset 0x100
    std::uint32_t field_104;                // offset 0x104
    std::uint32_t field_108;                // offset 0x108
    char device_name_10c[0x64];             // offset 0x10c
    std::uint32_t field_170;                // offset 0x170
    std::uint8_t field_174;                 // offset 0x174
    std::uint8_t pad_175[0x07];
    std::uint8_t field_17c;                 // offset 0x17c

    SoundContext_004d1a90* __thiscall init_004d1a90();
};

} // namespace porsche

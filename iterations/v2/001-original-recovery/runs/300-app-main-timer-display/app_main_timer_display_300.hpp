#pragma once

#include <cstdint>
#include <cstddef>
#include <mmintrin.h>

namespace porsche {

// -----------------------------------------------------------------------------
// Function 1: 0053c290 (77 PE body bytes, 80 bytes allocated)
// CPU SIMD/MMX feature branch vector operation dispatcher.
// -----------------------------------------------------------------------------
extern std::uint32_t g_cpu_feature_3dnow_005deb1c;
extern std::uint32_t g_cpu_feature_mmx_005deb18;

void __cdecl vector_transform_3dnow_005b0b00(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);
void __cdecl vector_transform_mmx_005b0a40(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);
void __cdecl vector_transform_generic_005b0980(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);

void __cdecl application_main_function_0053c290(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2);

// -----------------------------------------------------------------------------
// Function 2: 004b6660 (99 PE body bytes, 112 bytes allocated)
// Packet stream serialization and buffer flush dispatcher.
// -----------------------------------------------------------------------------
extern void* g_stream_buffer_5d6820;

void* __cdecl stream_alloc_buffer_00531ca0(const void* tag, void* buffer, std::uint32_t size);
void __cdecl stream_init_context_004b5ee0(const void* tag, void** p_cursor);
void __cdecl stream_write_packet_004b60d0(std::uint32_t arg0, std::uint32_t arg1, void** p_cursor);
void __cdecl stream_flush_buffer_00569640(void* buffer, std::uint32_t total_bytes);

void* __cdecl application_main_function_004b6660(std::uint32_t arg0, std::uint32_t arg1);

// -----------------------------------------------------------------------------
// Function 3: 00467fc0 (112 PE body bytes, 112 bytes allocated)
// Display resolution and video mode switcher.
// -----------------------------------------------------------------------------
extern std::uint32_t g_display_res_x_00619784;
extern std::uint32_t g_display_res_y_00619788;
extern std::uint32_t g_display_bpp_0061978c;

std::uint32_t __cdecl find_display_mode_005376c0(std::uint32_t width, std::uint32_t height, std::uint32_t bpp, std::uint32_t refresh_rate, std::uint32_t flags);

struct DisplayManager_00467fc0 {
    std::uint8_t pad_00[0x60];
    std::uint8_t fullscreen_flag_60;

    void __thiscall set_mode_00468030(std::uint32_t mode_id);
    void __thiscall set_resolution_00467fc0(std::uint32_t width, std::uint32_t height, std::uint32_t bpp, std::uint32_t refresh_rate);
};

void __fastcall application_main_function_00467fc0(
    DisplayManager_00467fc0* self,
    void* edx_unused,
    std::uint32_t width,
    std::uint32_t height,
    std::uint32_t bpp,
    std::uint32_t refresh_rate
);

// -----------------------------------------------------------------------------
// Function 4: 005366e0 (132 PE body bytes, 144 bytes allocated)
// Periodic game timer subsystem dispatcher.
// -----------------------------------------------------------------------------
using TimerCallbackFn = std::uint32_t (__cdecl*)(void* user_data, std::uint32_t elapsed_ticks);

struct GameTimerEntry_005366e0 {
    TimerCallbackFn callback;         // offset 0x00
    std::uint32_t period_ticks;      // offset 0x04
    std::uint32_t next_fire_time;    // offset 0x08
    std::uint32_t is_running;        // offset 0x0c
};

extern std::uint32_t g_timer_last_tick_0069de24;
extern std::uint32_t g_current_time_006b7c40;
extern GameTimerEntry_005366e0 g_timer_table_0069dd20[16];

std::uint32_t __cdecl application_main_function_005366e0(void* user_data);

} // namespace porsche

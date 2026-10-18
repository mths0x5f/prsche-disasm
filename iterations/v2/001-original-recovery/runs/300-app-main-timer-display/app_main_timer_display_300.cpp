#include "app_main_timer_display_300.hpp"

namespace porsche {

// 0053c290: CPU SIMD/MMX feature branch vector operation dispatcher
void __cdecl application_main_function_0053c290(std::uint32_t arg0, std::uint32_t arg1, std::uint32_t arg2) {
    if (g_cpu_feature_3dnow_005deb1c != 0u) {
        vector_transform_3dnow_005b0b00(arg0, arg1, arg2);
        return;
    }
    if (g_cpu_feature_mmx_005deb18 != 0u) {
        vector_transform_mmx_005b0a40(arg0, arg1, arg2);
        _mm_empty();
        return;
    }
    vector_transform_generic_005b0980(arg0, arg1, arg2);
}

// 004b6660: Packet stream serialization and buffer flush dispatcher
void* __cdecl application_main_function_004b6660(std::uint32_t arg0, std::uint32_t arg1) {
    void* buffer = stream_alloc_buffer_00531ca0(reinterpret_cast<const void*>(0x005d6e1cu), g_stream_buffer_5d6820, 0x10u);
    void* cursor = buffer;
    stream_init_context_004b5ee0(reinterpret_cast<const void*>(0x005d6e14u), &cursor);
    stream_write_packet_004b60d0(arg0, arg1, &cursor);
    *reinterpret_cast<std::uint32_t*>(cursor) = 0u;
    cursor = reinterpret_cast<void*>(reinterpret_cast<std::uintptr_t>(cursor) + 4u);
    const std::uint32_t total_bytes = static_cast<std::uint32_t>(
        reinterpret_cast<const std::uint8_t*>(cursor) - reinterpret_cast<const std::uint8_t*>(buffer)
    );
    stream_flush_buffer_00569640(buffer, total_bytes);
    return buffer;
}

// 00467fc0: Display resolution and video mode switcher
void __thiscall DisplayManager_00467fc0::set_resolution_00467fc0(std::uint32_t width, std::uint32_t height, std::uint32_t bpp, std::uint32_t refresh_rate) {
    if (width == g_display_res_x_00619784 && height == g_display_res_y_00619788 && bpp == g_display_bpp_0061978c) {
        return;
    }
    if (width == 0u) {
        width = g_display_res_x_00619784;
        height = g_display_res_y_00619788;
    }
    if (this->fullscreen_flag_60 != 0u) {
        this->set_mode_00468030(0u);
        return;
    }
    const std::uint32_t mode_id = find_display_mode_005376c0(width, height, bpp, refresh_rate, 1u);
    this->set_mode_00468030(mode_id);
}

void __fastcall application_main_function_00467fc0(
    DisplayManager_00467fc0* self,
    void* edx_unused,
    std::uint32_t width,
    std::uint32_t height,
    std::uint32_t bpp,
    std::uint32_t refresh_rate
) {
    (void)edx_unused;
    self->set_resolution_00467fc0(width, height, bpp, refresh_rate);
}

// 005366e0: Periodic game timer subsystem dispatcher
std::uint32_t __cdecl application_main_function_005366e0(void* user_data) {
    const std::uint32_t cur_time = g_current_time_006b7c40;
    if (g_timer_last_tick_0069de24 == cur_time) {
        return 0u;
    }

    g_timer_last_tick_0069de24 = cur_time;
    std::uint32_t accumulator = 0u;

    for (std::size_t i = 0; i < 16; ++i) {
        GameTimerEntry_005366e0& timer = g_timer_table_0069dd20[i];
        if (timer.callback == nullptr) {
            continue;
        }
        if (static_cast<std::int32_t>(g_current_time_006b7c40) < static_cast<std::int32_t>(timer.next_fire_time)) {
            continue;
        }
        if (timer.is_running != 0u) {
            continue;
        }

        timer.is_running = 1u;
        const std::uint32_t elapsed = g_current_time_006b7c40 - timer.next_fire_time;
        const std::uint32_t res = timer.callback(user_data, elapsed);
        accumulator |= res;

        timer.next_fire_time = g_current_time_006b7c40 + timer.period_ticks;
        timer.is_running = 0u;
    }

    return accumulator;
}

} // namespace porsche

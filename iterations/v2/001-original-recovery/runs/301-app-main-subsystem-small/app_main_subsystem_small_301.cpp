#include "app_main_subsystem_small_301.hpp"
#include <intrin.h>

namespace porsche {

// -----------------------------------------------------------------------------
// Function 1: 0048e6f0 (153 PE body bytes)
// -----------------------------------------------------------------------------
void __thiscall InputDevice_0048e6f0::update_mode_0048e6f0() {
    if (this->mode_28 == 0) {
        this->sub_0048e9c0();
        if (g_input_mgr_00628c70 != nullptr) {
            post_input_event_0048e1a0(0, 0, 0);
        }
        return;
    }

    if (this->mode_28 == 2) {
        this->sub_0048e9c0();
        if (g_input_mgr_00628c70 != nullptr) {
            post_input_event_0048e1a0(2, 0, 0);
        }
        return;
    }

    if (this->flag_c6 != 0) {
        if (this->sub_object_14 != nullptr) {
            this->sub_object_14->cleanup_004935c0();
            operator_delete_0059f050(this->sub_object_14);
            this->sub_object_14 = nullptr;
        }
        this->handle_0c->dispatch_input_cmd_0048c870(0xba, 0x80000000u, 0x80000000u, 0, 0);
        return;
    }

    this->sub_0048e9c0();
}

// -----------------------------------------------------------------------------
// Function 2: 004a6960 (153 PE body bytes)
// -----------------------------------------------------------------------------
void __cdecl application_main_function_004a6960() {
    time_delay_005659f0(-1);

    if (g_stream_ptr_00656518 != nullptr) {
        stream_destroy_00531f90(g_stream_ptr_00656518);
        g_stream_ptr_00656518 = nullptr;
        g_stream_id_00656510 = 0xffffffffu;
    }

    render_sync_004ae310();

    if (g_render_flag_005d1734 != 0 || g_render_flag_005d1738 != 0) {
        if (g_render_ptr_00655d44 != nullptr) {
            render_cycle_004ab4b0();
            std::uint32_t delta = get_time_delta_00565890();
            stream_destroy_00531f90(g_render_ptr_00655d44);
            g_render_ptr_00655d44 = nullptr;

            std::int32_t ecx = static_cast<std::int32_t>((delta + 1u) << 18);
            union {
                std::int64_t i64;
                struct {
                    std::uint32_t lo;
                    std::int32_t hi;
                } s;
            } u;
            u.i64 = __emul(ecx, 0x51eb851f);
            std::int32_t edx = u.s.hi >> 5;
            std::uint32_t sign = static_cast<std::uint32_t>(edx) >> 31;
            std::uint32_t sleep_ms = static_cast<std::uint32_t>(edx) + sign;

            throttle_sleep_005a177b(g_throttle_tag_005d1400, sleep_ms);
        }
    }
}

// -----------------------------------------------------------------------------
// Function 3: 004a5410 (157 PE body bytes)
// -----------------------------------------------------------------------------
void __cdecl application_main_function_004a5410() {
    g_heap_hook_005debf0 = const_cast<void*>(g_heap_default_table_0059fbc0);
    heap_init_0059e9d0(0x1800000u, 0x400000u, 0x100u, 0x100u);
    heap_reserve_0059edb0(0x190u, 0);
    sys_alloc_00565030(0x80u);

    if (g_subsystem_mgr_00628c70 == nullptr) {
        void* mem = operator_new_0059ef90(0x268u);
        if (mem != nullptr) {
            reinterpret_cast<InputManager_0048fc80*>(mem)->ctor_0048fc80();
        }
    }

    sys_service_0055fcf0();
    sys_service_00564e70();
    sys_service_00564ab0();
    sys_service_00564850(2);
    timer_init_00536e50();
    timer_register_005367b0(0, 0x3e8u, 1);
    packet_init_004b6ff0();
    window_channel_init_00563ad0(0x1eu, 0x2000u, 0);
}

// -----------------------------------------------------------------------------
// Function 4: 004d1a90 (172 PE body bytes)
// -----------------------------------------------------------------------------
SoundContext_004d1a90* __thiscall SoundContext_004d1a90::init_004d1a90() {
    reinterpret_cast<SoundBase_00525e20*>(this)->init_00525e20();

    this->sub_device_d4 = nullptr;
    this->field_e0 = 0;
    this->field_e4 = 0;
    this->field_e8 = 0;
    this->field_f8 = 0;
    this->field_fc = 0;
    this->field_100 = 0;
    this->field_104 = 0;
    this->field_108 = 0;
    this->field_170 = 0;
    this->field_174 = 0;
    this->field_17c = 0;
    this->vtable = g_sound_vtable_005b683c;

    void* mem = operator_new_0059ef90(0x2cu);
    SoundSubDevice_005294c0* sub_dev = nullptr;
    if (mem != nullptr) {
        sub_dev = reinterpret_cast<SoundSubDevice_005294c0*>(mem)->ctor_005294c0();
    }
    this->sub_device_d4 = sub_dev;

    const char* src = g_default_sound_device_005e8e50;
    char* dst = this->device_name_10c;
    while ((*dst++ = *src++) != '\0') {}

    return this;
}

} // namespace porsche

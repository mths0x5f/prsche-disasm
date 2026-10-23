#include "startup_mouse_children.hpp"
#include "../361-startup-device-pool/startup_device.hpp"
#include "porsche/files.hpp"
#include "porsche/file_threads.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/heap.hpp"
#include "porsche/render_driver_calls.hpp"
#include "porsche/render_event_route.hpp"
#include "porsche/shared_runtime_globals.hpp"
#include "porsche/startup_input.hpp"
#include "porsche/window_shutdown.hpp"
#include "porsche/window_state.hpp"
#include <cstdint>

namespace porsche {
// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Original 00537070 and 005370c0. DirectInput vtable offsets are bytes in x86.
static_assert(sizeof(void*)==4,"original DirectInput calls require x86");
std::uint32_t startup_mouse_access_005de758=4;
std::uint32_t startup_mouse_option8_005de75c=2;
std::uint32_t startup_mouse_option9_005de760=1;
std::int32_t startup_cursor_x_005deab0=0;
std::int32_t startup_cursor_y_005deab4=0;

// 00570ed0/00570f00 copy and restore a 96-byte renderer snapshot. Their
// complete state ownership is outside this batch; keep their exact calls.
void __cdecl startup_cursor_state_save_00570ed0(void* snapshot);
void __cdecl startup_cursor_state_restore_00570f00(const void* snapshot);

namespace {
template<class F> F slot(void* object,std::uint32_t index) {
    return reinterpret_cast<F>((*reinterpret_cast<void***>(object))[index]);
}
using Unary=std::uint32_t (__stdcall*)(void*);
using SetCooperativeLevel=std::uint32_t (__stdcall*)(void*,void*,std::uint32_t);

void diagnostic(std::uint32_t line,const char* message) {
    diagnostic_file_005deb74_set("\\real\\patch3\\pc\\mouse.c");
    diagnostic_line_005deb78=line;
    diagnostic_handler_005debf0(message);
}
}

void __cdecl startup_directinput_cleanup_00537070() {
    if (startup_mouse_device_0069e09c) {
        slot<Unary>(startup_mouse_device_0069e09c,8)(startup_mouse_device_0069e09c);
        slot<Unary>(startup_mouse_device_0069e09c,2)(startup_mouse_device_0069e09c);
        startup_mouse_device_0069e09c=nullptr;
    }
    if (startup_directinput_0069e098) {
        slot<Unary>(startup_directinput_0069e098,2)(startup_directinput_0069e098);
        startup_directinput_0069e098=nullptr;
    }
}

std::uint32_t __cdecl startup_mouse_mode_005370c0(std::uint32_t selector,
                                                   std::uint32_t value) {
    switch (selector) {
    case 3:
        startup_mouse_slot0_0069e07c=value;
        if (startup_mouse_access_005de758==4)
            startup_cursor_apply_005727c0(value,startup_mouse_slot1_0069e080);
        return 1;
    case 4:
        startup_mouse_slot1_0069e080=value;
        if (startup_mouse_access_005de758==4)
            startup_cursor_apply_005727c0(startup_mouse_slot0_0069e07c,value);
        return 1;
    case 5:
        startup_mouse_slot2_0069e084=value;
        return 1;
    case 7: {
        std::uint32_t success=1;
        if (startup_mouse_access_005de758!=value) {
            if (!startup_directinput_0069e098) {
                diagnostic(0x158,"MOUSE_setstate(INPUT_STATE_ACCESSMODE) - Cannot change the access mode as Direct Input was not initialized correctly\n");
            } else if (value==4 && startup_mouse_access_005de758!=4) {
                slot<Unary>(startup_mouse_device_0069e09c,8)(startup_mouse_device_0069e09c);
                startup_cursor_apply_005727c0(startup_mouse_slot0_0069e07c,
                                              startup_mouse_slot1_0069e080);
            } else {
                const std::uint32_t flags=(value==5 ? 5u : 6u);
                auto* device=startup_mouse_device_0069e09c;
                const auto first=slot<SetCooperativeLevel>(device,13)(device,
                    startup_window_handle_00557460(),flags);
                success=first==0;
                if (!success) {
                    const auto acquired=slot<Unary>(device,8)(device);
                    if (acquired==0 || acquired==1) {
                        success=slot<SetCooperativeLevel>(device,13)(device,
                            startup_window_handle_00557460(),flags)==0;
                        slot<Unary>(device,7)(device);
                    }
                }
            }
        }
        startup_mouse_access_005de758=value;
        return success;
    }
    case 8: startup_mouse_option8_005de75c=value;return 1;
    case 9: startup_mouse_option9_005de760=value;return 1;
    default:
        diagnostic(0x188,"[MOUSE] - Invalid setstate\n");
        return 0;
    }
}

void __cdecl startup_cursor_apply_005727c0(std::int32_t x,std::int32_t y) {
    alignas(4) std::uint8_t snapshot[96];
    if (file_current_thread_0055f780(0)) {
        startup_cursor_state_save_00570ed0(snapshot);
        (void)window_shutdown_prepare_00534550();
    } else {
        heap_enter_005322b0(thread_start_lock_006a57d8);
    }
    const auto left=static_cast<std::int32_t>(render_driver_bounds_a_006a643c);
    const auto right=static_cast<std::int32_t>(render_driver_bounds_c_006a6430);
    const auto top=static_cast<std::int32_t>(render_driver_bounds_b_006a6438);
    const auto bottom=static_cast<std::int32_t>(render_driver_bounds_d_006a6434);
    x=x>left ? x : left;
    if (x>=right) x=right;
    y=y>top ? y : top;
    if (y>=bottom) y=bottom;
    startup_cursor_x_005deab0=x;
    render_driver_limit_a_006a6448=static_cast<std::uint32_t>(startup_cursor_x_005deab0);
    startup_cursor_y_005deab4=y;
    render_driver_limit_b_006a6444=static_cast<std::uint32_t>(startup_cursor_y_005deab4);
    render_event_set_cursor_position_0053a970(window_configuration_address_006b77a0,x,y);
    if (file_current_thread_0055f780(0))
        startup_cursor_state_restore_00570f00(snapshot);
    else
        heap_leave_005322c0(thread_start_lock_006a57d8);
}
} // namespace porsche

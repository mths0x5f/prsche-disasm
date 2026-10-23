#include "mouse_callbacks.hpp"
#include "../361-startup-device-pool/startup_device.hpp"
#include "porsche/startup_input.hpp"

// MSVC x86 address-only compatibility binding. The legacy cdecl name is used
// solely as an address operand by frozen361 startup_device.cpp. It MUST NOT
// be called as cdecl. The canonical implementation below always returns RET24.
#pragma comment(linker,"/alternatename:?startup_mouse_callback_00537020@porsche@@YAIIIIIII@Z=?startup_mouse_window_handler_00537020@porsche@@YGIPAX0IIHPAH@Z")

namespace porsche {
// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00537020..00537062, 005370b0..005370bf. See original-evidence.json.
std::uint32_t startup_mouse_wheel_0069e0a8=0;

std::uint32_t __stdcall startup_mouse_window_handler_00537020(
    void* active,void* window,std::uint32_t,std::uint32_t wparam,
    std::int32_t,std::int32_t*) {
    if (active && window_hwnd_006b7bf8==window) {
        const std::int32_t high=static_cast<std::int32_t>(wparam>>16);
        const std::int32_t delta=(high>=0x8000 ? high-0x10000 : high);
        // Original signed magic multiply implements truncation toward zero /120.
        // Unsigned destination deliberately preserves x86 ADD wrapping.
        startup_mouse_wheel_0069e0a8+=static_cast<std::uint32_t>(delta/120);
    }
    return 0;
}

void __cdecl startup_mouse_exit_005370b0() {
    startup_directinput_cleanup_00537070();
    startup_mouse_initialized_0069e0a0=0;
}
}

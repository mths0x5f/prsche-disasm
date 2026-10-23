#pragma once
#include <cstdint>
#include "porsche/window_procedure.hpp"

namespace porsche {
// Original loader-zero-filled wheel accumulator. Poll005372a0 consumes and clears it.
extern std::uint32_t startup_mouse_wheel_0069e0a8;
// The frozen361 cdecl declaration is ADDRESS-ONLY and resolves to this entry.
// All invocations must use this stdcall signature (WindowHandler, RET24).
std::uint32_t __stdcall startup_mouse_window_handler_00537020(
    void*,void*,std::uint32_t,std::uint32_t,std::int32_t,std::int32_t*);
void __cdecl startup_mouse_exit_005370b0();
}

#pragma once
#include <cstdint>

namespace porsche {
// Porsche.exe 005de758..005de760, accessed by 005370c0.
extern std::uint32_t startup_mouse_access_005de758;
extern std::uint32_t startup_mouse_option8_005de75c;
extern std::uint32_t startup_mouse_option9_005de760;
extern std::int32_t startup_cursor_x_005deab0;
extern std::int32_t startup_cursor_y_005deab4;

void __cdecl startup_directinput_cleanup_00537070();
std::uint32_t __cdecl startup_mouse_mode_005370c0(std::uint32_t selector,
                                                   std::uint32_t value);
void __cdecl startup_cursor_apply_005727c0(std::int32_t x,std::int32_t y);
}

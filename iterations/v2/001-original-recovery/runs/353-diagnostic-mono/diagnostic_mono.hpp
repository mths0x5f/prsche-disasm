#pragma once
#include <cstdint>

namespace porsche {
// Physical 14-byte .data image at 005e25dc..005e25e9.
alignas(4) extern std::uint8_t diagnostic_mono_image_005e25dc[14];
extern std::uint32_t diagnostic_mono_lock_006af140;
extern std::uint32_t diagnostic_mono_row_006af148;

int __cdecl application_diagnostic_mono_format_00592a50(const char*,...);
int __cdecl application_diagnostic_mono_xy_format_00592ac0(std::int32_t,std::int32_t,const char*,...);
void __cdecl application_diagnostic_mono_write_00592b60(const char*);
void __cdecl application_diagnostic_mono_scroll_00592d00();
void __cdecl application_diagnostic_mono_clear_00592d70();
void __cdecl application_diagnostic_mono_attribute_00592e00(std::uint32_t);
int __cdecl application_diagnostic_mono_vsprintf_005a299e(char*,const char*,const std::uint32_t*);
}

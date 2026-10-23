#pragma once
#include <cstdint>
namespace porsche {
// Original256-DWORD palette006b4b20..006b4f1f, initially PE loader-zeroed.
extern std::uint32_t render_pixel_palette_006b4b20[256];
void* __cdecl render_buffer_address_00574050(std::int32_t x,std::int32_t y);
std::uint32_t __cdecl render_buffer_convert_00574b70(std::uint32_t pixel);
}

#pragma once
#include <cstdint>
namespace porsche {
void __cdecl render_buffer_select_00556910(std::int32_t x,std::int32_t y,std::uint32_t pixel);
// Original engine services remain explicit; no renderer/address/conversion
// approximation is supplied by this batch.
std::uint32_t __cdecl render_buffer_convert_00574b70(std::uint32_t pixel);
void __cdecl render_buffer_draw_0056de20(float x,float y,std::uint32_t pixel);
void* __cdecl render_buffer_address_00574050(std::int32_t x,std::int32_t y);
void* __cdecl render_buffer_word_0056e301(void* destination,std::uint32_t pixel,std::int32_t bytes);
}

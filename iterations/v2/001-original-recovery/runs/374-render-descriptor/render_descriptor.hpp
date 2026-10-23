#pragma once
#include <cstdint>
namespace porsche {
extern void* render_descriptor_fallback_0069dd14;
extern std::uint32_t render_descriptor_flags_005deb60;
extern std::uint32_t render_descriptor_option_005deb88;
extern const std::uint8_t render_descriptor_bits_005de890[128];
std::uint32_t __cdecl render_descriptor_format_00556880(std::uint32_t format);
std::uint32_t __cdecl render_descriptor_bits_00537f90(const void* descriptor_format);
std::uint32_t __cdecl render_descriptor_window_00534360(void* descriptor);
std::uint32_t __cdecl render_descriptor_bind_00534480(void* descriptor);
void* __cdecl render_descriptor_create_00535950(std::uint32_t,std::uint32_t,
    std::uint32_t,std::uint32_t);
// Original engine constructor remains external until separately recovered.
void* __cdecl render_descriptor_allocate_00535700(std::uint32_t,std::uint32_t,
    std::uint32_t,std::uint32_t,std::uint32_t);
}

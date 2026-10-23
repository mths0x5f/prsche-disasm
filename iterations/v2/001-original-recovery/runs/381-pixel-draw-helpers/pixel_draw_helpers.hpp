#pragma once
#include <cstdint>
namespace porsche {
// Five original cdecl stack DWORDs: four FLOAT32 representations and a pixel.
// Raw transport avoids quieting signaling NaNs in the MOV/PUSH-only wrapper.
// The656-byte0056daf0 geometry/clipping body remains explicitly external.
void __cdecl render_draw_rectangle_bits_0056daf0(std::uint32_t x_bits,
    std::uint32_t y_bits,std::uint32_t width_bits,std::uint32_t height_bits,
    std::uint32_t pixel);
}

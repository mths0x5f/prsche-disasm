#include "pixel_helpers.hpp"
#include "porsche/window_shutdown.hpp"
#include <cstdint>
namespace porsche {
std::uint32_t render_pixel_palette_006b4b20[256]{};
void* __cdecl render_buffer_address_00574050(std::int32_t x,std::int32_t y){
    const auto pitch=window_shutdown_config_005de620[9];
    const auto storage_bits=reinterpret_cast<const std::uint8_t*>(window_shutdown_config_005de620)[14];
    const auto vertical=pitch*static_cast<std::uint32_t>(y);
    const auto horizontal=static_cast<std::uint32_t>(storage_bits)*static_cast<std::uint32_t>(x);
    const auto base=window_shutdown_config_005de620[11];
    // SAR3 follows the low32 bits of IMUL, including multiplication overflow.
    const auto shifted=(horizontal>>3)|((horizontal&0x80000000u)?0xe0000000u:0u);
    const auto address=vertical+base+shifted;
    return reinterpret_cast<void*>(static_cast<std::uintptr_t>(address));
}
std::uint32_t __cdecl render_buffer_convert_00574b70(std::uint32_t pixel){
    const auto* config=reinterpret_cast<const std::uint8_t*>(window_shutdown_config_005de620);
    switch(config[13]){
    case 15:{
        const auto alpha=(pixel&0x8000u)?0xffu:0u;
        return (alpha<<24)|(((pixel>>10)&31u)<<19)|(((pixel>>5)&31u)<<11)|((pixel&31u)<<3);
    }
    case 16:
        if(config[12]==0x6d)
            return (((pixel>>12)&15u)<<28)|(((pixel>>8)&15u)<<20)|(((pixel>>4)&15u)<<12)|((pixel&15u)<<4);
        return ((pixel!=0?0xffu:0u)<<24)|(((pixel>>11)&31u)<<19)|(((pixel>>5)&63u)<<10)|((pixel&31u)<<3);
    case 24:case 32:return pixel;
    default:return render_pixel_palette_006b4b20[pixel];
    }
}
}

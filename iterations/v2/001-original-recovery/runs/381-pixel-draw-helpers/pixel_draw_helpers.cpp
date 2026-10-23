#include "pixel_draw_helpers.hpp"
#include "../378-buffer-select/buffer_select.hpp"
#include <cstring>
namespace porsche {
//0056de20..0056de41 forwards the original FLOAT32 words without an FPU load.
void __cdecl render_buffer_draw_0056de20(float x,float y,std::uint32_t pixel){
    std::uint32_t x_bits,y_bits;
    std::memcpy(&x_bits,&x,4);std::memcpy(&y_bits,&y,4);
    render_draw_rectangle_bits_0056daf0(x_bits,y_bits,0x3f800000u,0x3f800000u,pixel);
}
//0056e301..0056e337 is distinct from the accepted big-endian0056e2c0 entry.
void* __cdecl render_buffer_word_0056e301(void* destination,std::uint32_t pixel,std::int32_t bytes){
    auto* out=static_cast<std::uint8_t*>(destination);
    if(bytes>=3){
        if(bytes==3){
            const auto low=static_cast<std::uint16_t>(pixel);std::memcpy(out,&low,2);
            // Original MOV byte[EAX],DL after SHR EDX,16 overwrites byte0.
            // Byte2 is untouched, while the returned pointer still advances3.
            out[0]=static_cast<std::uint8_t>(pixel>>16);return out+3;
        }
        std::memcpy(out,&pixel,4);return out+4;
    }
    if(bytes<1)return out;
    if(bytes==1){out[0]=static_cast<std::uint8_t>(pixel);return out+1;}
    const auto low=static_cast<std::uint16_t>(pixel);std::memcpy(out,&low,2);return out+2;
}
}

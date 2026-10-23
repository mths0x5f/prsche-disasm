#include "buffer_select.hpp"
#include "porsche/window_shutdown.hpp"
#include "porsche/render_display.hpp"
#include "porsche/render_settings.hpp"
#include "porsche/render_loader.hpp"
#include <cstring>
namespace porsche {
namespace {
void texture(std::uint32_t value){
    using Select=void (__stdcall*)(std::uint32_t);
    reinterpret_cast<Select>(static_cast<std::uintptr_t>(render_thrash_exports_006bd910[17]))(value);
}
}
// Original00556910 consumes three cdecl DWORDs: signed x/y and a packed pixel.
// The legacy select_buffer name is retained solely as the existing facade ABI.
void __cdecl render_buffer_select_00556910(std::int32_t x,std::int32_t y,std::uint32_t pixel){
    const auto mode=window_shutdown_mode_005de630;
    if(mode!=0&&mode!=255&&window_shutdown_state_005de64c==0){
        const auto saved10=render_settings_get_state_006bd984(10);
        const auto saved1=render_settings_get_state_006bd984(1);
        (void)render_settings_set_state_006bd97c(10,0);texture(0);
        const auto converted=render_buffer_convert_00574b70(pixel);
        // Original FILD signed DWORD / FSTP32; comparison domain uses the
        // normal round-to-nearest x87/MXCSR environment.
        render_buffer_draw_0056de20(static_cast<float>(x),static_cast<float>(y),converted);
        (void)render_settings_set_state_006bd97c(10,saved10);texture(saved1);return;
    }
    if(x<static_cast<std::int32_t>(window_shutdown_config_005de620[5])||
       x>=static_cast<std::int32_t>(window_shutdown_config_005de620[7])||
       y<static_cast<std::int32_t>(window_shutdown_config_005de620[6])||
       y>=static_cast<std::int32_t>(window_shutdown_config_005de620[8]))return;
    auto* destination=static_cast<std::uint8_t*>(render_buffer_address_00574050(x,y));
    // Original reads the depth byte after the address service returns.
    const auto depth=reinterpret_cast<const std::uint8_t*>(window_shutdown_config_005de620)[13];
    switch(depth){
    case 4:
        if(static_cast<std::uint32_t>(x)&1u)
            *destination=static_cast<std::uint8_t>((*destination&15u)|static_cast<std::uint8_t>(pixel<<4));
        else
            *destination=static_cast<std::uint8_t>((*destination&240u)|static_cast<std::uint8_t>(pixel));
        return;
    case 8:*destination=static_cast<std::uint8_t>(pixel);return;
    case 15:case 16:{const auto word=static_cast<std::uint16_t>(pixel);std::memcpy(destination,&word,2);return;}
    case 24:(void)render_buffer_word_0056e301(destination,pixel,3);return;
    case 32:std::memcpy(destination,&pixel,4);return;
    default:return;
    }
}
void __cdecl render_display_select_buffer_00556910(std::uint32_t x,std::uint32_t y,std::uint32_t pixel){
    render_buffer_select_00556910(static_cast<std::int32_t>(x),static_cast<std::int32_t>(y),pixel);
}
}

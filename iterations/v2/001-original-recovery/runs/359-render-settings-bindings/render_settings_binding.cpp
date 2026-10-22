#include "porsche/render_settings.hpp"
#include "porsche/render_mode.hpp"
#include "porsche/window_shutdown.hpp"
#include "porsche/render_loader.hpp"
#include <cstdint>

namespace porsche {
namespace {
template<class T> T procedure(std::uint32_t index){
    return reinterpret_cast<T>(static_cast<std::uintptr_t>(render_thrash_exports_006bd910[index]));
}
using About=const RenderSettingsDevice* (__stdcall*)();
using Get=std::uint32_t (__stdcall*)(std::uint32_t);
using Set=std::uint32_t (__stdcall*)(std::uint32_t,std::uint32_t);
using Window=void (__stdcall*)(std::uint32_t);
}
const RenderSettingsDevice* __cdecl render_settings_current_device_006bd934(){
    return procedure<About>(9)();
}
std::uint32_t __stdcall render_settings_get_state_006bd984(std::uint32_t key){
    return procedure<Get>(29)(key);
}
std::uint32_t __stdcall render_settings_set_state_006bd97c(std::uint32_t key,std::uint32_t value){
    return procedure<Set>(27)(key,value);
}
void __stdcall render_mode_setstate_iat_006bd918(std::uint32_t key,std::uint32_t value){
    (void)procedure<Set>(2)(key,value);
}
void __stdcall window_shutdown_display_callback_006bd9b0(std::uint32_t mode){
    procedure<Window>(40)(mode);
}
}

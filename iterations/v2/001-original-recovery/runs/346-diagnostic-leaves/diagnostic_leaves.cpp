#include "../345-diagnostic-devices/diagnostic_devices.hpp"
#include "porsche/formatter_stdio.hpp"
#include <cstdint>

namespace porsche {
// Original 00592a50 accepts a printf-style format. Only the one-pointer
// forwarding ABI of 00586ca0 is recovered here.
int __cdecl application_diagnostic_mono_format_00592a50(const char*,...);
// Controlled binding for original KERNEL32 OutputDebugStringA IAT 005b2208.
void __stdcall application_diagnostic_output_debug_string(const char*);

void __cdecl application_diagnostic_device_set_0055ed20(
    std::uint32_t index,std::uint32_t enabled){
    auto& flags=application_diagnostic_devices_005e1c8c[index].flags;
    flags=(flags&0xfffffffeu)|(enabled!=0u);
}

void __cdecl application_diagnostic_channel_set_0055efd0(
    std::uint32_t index,std::uint32_t enabled){
    const std::uint32_t bit=enabled!=0u;
    if(index==0u){
        for(auto& channel:application_diagnostic_channels_005df4a0)
            channel.flags=(channel.flags&~1u)|bit;
    }else if(index==1u){
        for(auto& channel:application_diagnostic_channels_005df4a0)
            if((channel.flags&2u)!=0u)channel.flags=(channel.flags&~1u)|bit;
    }else{
        auto& flags=application_diagnostic_channels_005df4a0[index].flags;
        flags=(flags&~1u)|bit;
    }
}

void __cdecl application_diagnostic_device_callback_00586ca0(
    std::uint32_t,const char* message){
    application_diagnostic_mono_format_00592a50(message);
}
void __cdecl application_diagnostic_device_callback_00586cb0(
    std::uint32_t,const char* message){
    formatter_stdio_printf_005a177b(message);
}
void __cdecl application_diagnostic_device_callback_00586cc0(
    std::uint32_t,const char* message){
    application_diagnostic_output_debug_string(message);
}
}

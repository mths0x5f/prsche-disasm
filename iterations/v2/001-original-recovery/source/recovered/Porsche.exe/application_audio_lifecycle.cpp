#include "porsche/application_audio_lifecycle.hpp"
#include "porsche/application_state.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/frame_services.hpp"
#include <cstring>

namespace porsche {
std::uint32_t application_audio_auxiliary_006568e4 = 0;
std::uint32_t application_audio_device_configured_00655d40 = 0;
std::uint8_t& application_audio_post_init_byte_00656868 = frame_services_byte_00656868;
std::uint8_t& application_audio_post_init_byte_00656869 = frame_services_byte_00656869;
namespace {
std::uint32_t state_word(std::size_t offset) {
    std::uint32_t value;
    std::memcpy(&value, application_audio_device_state_006b48c0.data()+offset, 4);
    return value;
}
void release(std::uint32_t address) {
    (void)free_00531f90(reinterpret_cast<void*>(static_cast<std::uintptr_t>(address)));
}
template<class Function> Function callback(std::size_t offset) {
    return reinterpret_cast<Function>(static_cast<std::uintptr_t>(state_word(offset)));
}
}

// 004ab470..004ab4ae. Callers ignore incidental EAX; no scalar return is claimed.
void __cdecl application_audio_post_setup_004ab470() {
    if(application_audio_device_configured_00655d40)
        application_audio_period_control_00565c70(0x80,0,40,~0u,~0u);
    application_audio_period_control_00565c70(0x20,0,40,~0u,~0u);
    application_audio_post_init_byte_00656869=0;
    application_audio_post_init_byte_00656868=0;
}

// 004ab4b0..004ab4de; the pointer is reloaded after the control effect.
void __cdecl application_audio_probe_finish_004ab4b0() {
    application_audio_period_control_00565c70(0,0,0,~0u,~0u);
    if(application_audio_auxiliary_006568e4) {
        release(application_audio_auxiliary_006568e4);
        application_audio_auxiliary_006568e4=0;
    }
}

// 00565890..00565916. Each callback is loaded after its predecessor returns.
std::int32_t __cdecl application_audio_probe_measure_00565890() {
    if(!application_audio_device_state_006b48c0[0xdc]) return -10;
    application_audio_period_control_00565c70(0,0,0,~0u,~0u);
    using NoArguments=void (__cdecl *)();
    if(const auto target=callback<NoArguments>(0x138)) target();
    if(const auto target=callback<NoArguments>(0x13c)) target();
    if(const auto target=callback<NoArguments>(0x134)) target();
    application_audio_backend_quiet_0058ff10();
    using OneArgument=void (__cdecl *)(std::int32_t);
    if(const auto target=callback<OneArgument>(0x130)) target(-1);
    application_audio_backend_stop_device_0058fe80();
    application_audio_backend_release_0058ac30(state_word(0x140));
    application_audio_backend_release_0058ac30(state_word(0x144));
    application_audio_device_state_006b48c0[0xdc]=0;
    application_audio_backend_stop_0058e2e0();
    return application_audio_backend_close_0058aac0();
}

// 004a6a00..004a6b76. Preserve the low-byte tests and callback-sensitive reloads.
void __cdecl application_audio_transition_004a6a00(std::uint32_t disabled,
    std::uint32_t unused,std::uint32_t mode,std::uint32_t configuration,
    std::uint32_t secondary) {
    (void)unused;
    if(mode==3) disabled=(disabled&0xffffff00u)|1u;
    if(mode==application_audio_mode_00655d38 &&
       application_audio_flag_00655d3c==0 &&
       configuration==application_audio_config_00655d34) return;
    auto& arena=application_state_006573e8;
    application_audio_mode_00655d38=mode;
    arena.word(0x00657c98)=mode;
    application_audio_flag_00655d3c=0;
    application_audio_config_00655d34=configuration;
    arena.word(0x00657c94)=disabled&0xff;
    arena.word(0x00657c9c)=0;
    if(application_audio_buffer_00655d44) {
        (void)application_audio_stop_channel_005659f0(-1);
        auto& last=application_audio_records_006564a0[7];
        if(last.raw_08) {
            release(last.raw_08);
            last.raw_08=0;
            last.raw_00=~0u;
        }
        application_audio_probe_prepare_004ae2b0();
        application_audio_probe_finish_004ab4b0();
        (void)application_audio_probe_measure_00565890();
        release(application_audio_buffer_00655d44);
        application_audio_buffer_00655d44=0;
        application_audio_active_005d1734=0;
    }
    if(static_cast<std::uint8_t>(disabled)) return;
    application_audio_buffer_00655d44=static_cast<std::uint32_t>(
        reinterpret_cast<std::uintptr_t>(allocate_00531ca0("audio heap",0x40000,0)));
    for(auto& item:application_audio_records_006564a0) {
        item.raw_00=~0u;item.raw_08=0;
    }
    if(application_audio_probe_initialize_004a66b0()) {
        application_audio_active_005d1734=1;
        application_audio_transition_configure_004ae010(configuration,secondary);
        application_audio_probe_start_004a8b80();
        application_audio_transition_finish_004ae4d0(0,0);
        return;
    }
    release(application_audio_buffer_00655d44);
    application_audio_buffer_00655d44=0;
    arena.word(0x00657c94)=1;
    arena.word(0x00657c98)=3;
    application_audio_mode_00655d38=3;
    application_audio_flag_00655d3c=0;
    arena.word(0x00657c9c)=0;
    application_audio_config_00655d34=0;
    application_audio_active_005d1734=0;
}
} // namespace porsche

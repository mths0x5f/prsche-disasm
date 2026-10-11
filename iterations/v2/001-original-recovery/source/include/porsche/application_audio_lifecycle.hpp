#pragma once
#include "porsche/application_audio_device.hpp"
#include "porsche/application_services.hpp"
#include <cstdint>

namespace porsche {
extern std::uint32_t application_audio_auxiliary_006568e4;
extern std::uint32_t application_audio_device_configured_00655d40;
extern std::uint8_t& application_audio_post_init_byte_00656868;
extern std::uint8_t& application_audio_post_init_byte_00656869;

// 004e48b4 supplies five cdecl arguments. The second is not consumed.
// Its virtual-method-derived third argument has no proved signed range.
void __cdecl application_audio_transition_004a6a00(std::uint32_t disabled,
    std::uint32_t unused, std::uint32_t mode, std::uint32_t configuration,
    std::uint32_t secondary);
void __cdecl application_audio_post_setup_004ab470();
// finish and measure declarations are shared with application_services.hpp.

// Unrecovered effects; none is a production fixture or no-op.
void __cdecl application_audio_period_control_00565c70(std::uint32_t,
    std::uint32_t, std::uint32_t, std::uint32_t, std::uint32_t);
std::int32_t __cdecl application_audio_stop_channel_005659f0(std::int32_t);
void __cdecl application_audio_transition_configure_004ae010(
    std::uint32_t configuration, std::uint32_t secondary);
void __cdecl application_audio_transition_finish_004ae4d0(std::uint32_t,
    std::uint32_t);
void __cdecl application_audio_backend_release_0058ac30(std::uint32_t);
void __cdecl application_audio_backend_quiet_0058ff10();
std::int32_t __cdecl application_audio_backend_close_0058aac0();
} // namespace porsche

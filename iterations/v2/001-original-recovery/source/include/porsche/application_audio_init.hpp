#pragma once

#include "porsche/application_audio_device.hpp"

#include <array>
#include <cstdint>

namespace porsche {

// Original 004a66b0 return is consumed through AL by 004a6840.
std::uint8_t __cdecl application_audio_initialize_004a66b0();

// This byte-for-byte original state cell was not owned by Run 128.
extern std::uint32_t application_audio_device_configured_00655d40;
extern std::uint8_t application_audio_post_init_byte_00656868;
extern std::uint8_t application_audio_post_init_byte_00656869;

// Explicit device/timing boundaries. The callsite argument order and whether
// each return is observed are retained; device implementation stays external.
void __cdecl application_audio_prepare_00565950();
void __cdecl application_audio_wait_0053c380(std::int32_t interval);
void __cdecl application_audio_period_control_00565c70(
    std::uint32_t first, std::uint32_t second, std::uint32_t third,
    std::uint32_t fourth, std::uint32_t fifth);

// The body at 004ab470 is short and fully represented here; only its
// 00565c70 device-control calls remain boundaries.
void __cdecl application_audio_post_setup_004ab470();

using AudioInitDescriptor = std::array<std::uint8_t, 0x7c>;
static_assert(sizeof(AudioInitDescriptor) == 124);

} // namespace porsche

// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// Channel table shared with Run 421: a signed 16-bit count at 006b49a4 and a
// pointer at 006b4a00 to 0x70-byte records. Declared identically to Run 421;
// storage stays a link boundary here too.
extern std::int16_t audio_backend_channel_count_006b49a4;
extern std::uint32_t audio_backend_channels_006b4a00;

// Only the fields these two bodies read are named.
struct AudioChannelRecord_422 {
    std::int32_t handle;            // +0x00  compared raw, and tested >= 0
    std::uint8_t opaque_04[0x0b];
    std::uint8_t active;            // +0x0f  0 = free; next_voice wants exactly 1
    std::uint8_t opaque_10[0x0e];
    std::uint8_t group;             // +0x1e  voice group, 0 = ungrouped
    std::uint8_t opaque_1f[0x51];
};
static_assert(sizeof(AudioChannelRecord_422) == 0x70, "original record stride");
static_assert(offsetof(AudioChannelRecord_422, active) == 0x0f, "active offset");
static_assert(offsetof(AudioChannelRecord_422, group) == 0x1e, "group offset");

// Declared identically by Run 400's frame_loop_clusters_400.hpp.
std::int32_t __cdecl audio_backend_find_channel_00589d20(std::uint32_t handle);
std::uint32_t __cdecl audio_backend_next_voice_00590340(std::int32_t channel, std::uint32_t* voice_slot);

} // namespace porsche

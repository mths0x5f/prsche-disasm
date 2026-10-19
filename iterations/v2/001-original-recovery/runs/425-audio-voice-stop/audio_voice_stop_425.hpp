// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
#pragma once

#include <cstdint>
#include <cstddef>

#include "porsche/application_audio_lifecycle.hpp"   // application_audio_backend_release_0058ac30

namespace porsche {

// ---------------------------------------------------------------------------
// Storage boundaries, declared and not defined (same policy as Runs 421/422).
// ---------------------------------------------------------------------------
extern std::uint32_t audio_voice_table_006b489c;           // 0xf8-byte voice records
extern std::uint32_t audio_backend_stamp_006b49a8;         // copied into a released channel
extern std::uint32_t audio_backend_pool_006b4a18;          // Run 421
extern std::int16_t audio_backend_channel_count_006b49a4;  // Run 421/422
extern std::uint32_t audio_backend_channels_006b4a00;      // Run 421/422

// Voice record: only the fields the four bodies touch are named.
struct AudioVoiceRecord_425 {
    std::uint32_t flags;                 // +0x00  bit 1: +0xf4 path, bit 2: link release, 0x10: group
    std::uint8_t opaque_04[0x28];
    std::uint8_t link_a[0x38];           // +0x2c  embedded node; also the callback argument
    std::uint8_t link_b[0x60];           // +0x64  embedded node; word +0x66 holds the voice index
    std::uint32_t link_head;             // +0xc4  singly linked list, next pointer at node +0
    void (__cdecl* stop_callback)(std::uint32_t link_a_va);   // +0xc8
    std::uint8_t opaque_cc[0x28];
    std::uint32_t field_f4;              // +0xf4  cleared on the bit-1 path
};
static_assert(sizeof(AudioVoiceRecord_425) == 0xf8, "voice record stride");
static_assert(offsetof(AudioVoiceRecord_425, link_a) == 0x2c, "link_a");
static_assert(offsetof(AudioVoiceRecord_425, link_b) == 0x64, "link_b");
static_assert(offsetof(AudioVoiceRecord_425, link_head) == 0xc4, "link_head");
static_assert(offsetof(AudioVoiceRecord_425, stop_callback) == 0xc8, "callback");
static_assert(offsetof(AudioVoiceRecord_425, field_f4) == 0xf4, "field_f4");

// Channel record view (stride 0x70, as in Run 422) with the fields 00589c00 uses.
struct AudioChannelRecord_425 {
    std::int32_t handle;                 // +0x00
    std::uint8_t opaque_04[0x0b];
    std::uint8_t active;                 // +0x0f  0 free, 1, 2
    std::uint8_t opaque_10[0x0b];
    std::uint8_t leader;                 // +0x1b  marks the group member that leads
    std::uint8_t opaque_1c[2];
    std::uint8_t group;                  // +0x1e
    std::uint8_t opaque_1f;
    std::uint32_t stamp;                 // +0x20  receives audio_backend_stamp_006b49a8
    std::uint8_t opaque_24[0x4c];
};
static_assert(sizeof(AudioChannelRecord_425) == 0x70, "channel stride");
static_assert(offsetof(AudioChannelRecord_425, leader) == 0x1b, "leader");
static_assert(offsetof(AudioChannelRecord_425, group) == 0x1e, "group");
static_assert(offsetof(AudioChannelRecord_425, stamp) == 0x20, "stamp");

// Pool header view: Run 421's five fields plus the negative entry count at
// +0x14 that 0058ac30 maintains. 8-byte entries {offset, size} grow downwards
// from end_marker; entry i (i = 0, -1, ...) is at end_marker + i*8.
struct AudioPoolHeader_425 {
    std::uint32_t first_aligned;   // +0x00
    std::uint32_t end_marker;      // +0x04
    std::uint32_t size;            // +0x08
    std::uint32_t limit;           // +0x0c  grows by 8 per released entry
    std::uint32_t cursor;          // +0x10
    std::int32_t entry_count;      // +0x14  minus the number of live entries
};
static_assert(sizeof(AudioPoolHeader_425) == 0x18, "pool header");

// Declared identically by Run 400's frame_loop_clusters_400.hpp.
void __cdecl audio_backend_stop_voice_0058a8b0(std::uint32_t voice_slot);
// Named here; no earlier declaration exists.
void __cdecl audio_voice_release_links_00597010(std::uint32_t link_b_va);
void __cdecl audio_channel_group_release_00589c00(std::uint32_t channel);

} // namespace porsche

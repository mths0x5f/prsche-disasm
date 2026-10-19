// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Channel lookup and voice iteration over the 0x70-byte channel table:
//   00589d20..00589d6e (79 bytes)   audio_backend_find_channel_00589d20
//   00590340..005903c4 (133 bytes)  audio_backend_next_voice_00590340
// Both are leaves. Their only caller is audio_channel_stop_00565d60 (Run 400),
// which starts the voice slot at 0xffffffff and stops each voice returned.
#include "audio_channel_voice_lookup_422.hpp"

namespace porsche {

namespace {

const AudioChannelRecord_422* record_at(std::uint32_t table, std::int32_t index) {
    // lea ecx,[idx*8]; sub ecx,idx; shl ecx,4  ->  idx * 0x70
    return reinterpret_cast<const AudioChannelRecord_422*>(
        static_cast<std::uintptr_t>(table + static_cast<std::uint32_t>(index) * 0x70u));
}

constexpr std::int32_t kNoChannel = -8;   // mov eax,0fffffff8h

} // namespace

// ---------------------------------------------------------------------------
// 00589d20 (79 bytes): the channel index is the low byte of the handle; it is
// valid only if the handle is non-negative, the index is below the signed
// 16-bit count, the record is active and the record holds the same handle.
// Every failure returns -8.
// ---------------------------------------------------------------------------
std::int32_t __cdecl audio_backend_find_channel_00589d20(std::uint32_t handle) {
    if (static_cast<std::int32_t>(handle) < 0) {          // test edx,edx; jge
        return kNoChannel;
    }
    const std::int32_t count = audio_backend_channel_count_006b49a4;   // movsx
    const std::int32_t index = static_cast<std::int32_t>(handle & 0xffu);
    if (!(index < count)) {                                // cmp eax,ecx; jl (signed)
        return kNoChannel;
    }
    const AudioChannelRecord_422* record = record_at(audio_backend_channels_006b4a00, index);
    if (record->active == 0) {                             // test bl,bl; je
        return kNoChannel;
    }
    if (static_cast<std::uint32_t>(record->handle) != handle) {   // cmp [ecx],edx; je
        return kNoChannel;
    }
    return index;
}

// ---------------------------------------------------------------------------
// 00590340 (133 bytes): return 1 and advance *voice_slot to the next voice of
// this channel's group, or return 0 when there is none.
//
// An ungrouped channel (group 0) has exactly one voice, itself: the first call
// (slot < 0) stores the channel and returns 1, the next returns 0.
//
// A grouped channel scans forward from slot + 1 for a record in the same group
// whose active byte is exactly 1 and whose handle is non-negative. The slot is
// written before every bound test, so it ends one past the last index tried.
// The slot is declared uint32_t but every comparison on it is signed.
// The table pointer and the count are read once: the body makes no calls.
// ---------------------------------------------------------------------------
std::uint32_t __cdecl audio_backend_next_voice_00590340(
    std::int32_t channel, std::uint32_t* voice_slot) {
    const std::uint32_t table = audio_backend_channels_006b4a00;
    const std::uint32_t group = record_at(table, channel)->group;   // zero-extended

    if (group == 0) {
        if (static_cast<std::int32_t>(*voice_slot) >= 0) {   // cmp [ecx],0; jge
            return 0;
        }
        *voice_slot = static_cast<std::uint32_t>(channel);  // eax still holds channel
        return 1;
    }

    const std::int32_t count = audio_backend_channel_count_006b49a4;   // movsx
    std::int32_t index = static_cast<std::int32_t>(*voice_slot) + 1;
    *voice_slot = static_cast<std::uint32_t>(index);        // stored before the test
    if (index >= count) {
        return 0;
    }
    for (;;) {
        const AudioChannelRecord_422* record = record_at(table, index);
        if (record->group == group && record->active == 1 && record->handle >= 0) {
            return 1;
        }
        ++index;
        *voice_slot = static_cast<std::uint32_t>(index);    // inc edx; mov [edi],edx
        if (!(index < count)) {
            return 0;
        }
    }
}

} // namespace porsche

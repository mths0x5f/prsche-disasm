// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Voice stop and the three bodies it reaches, 551 PE body bytes:
//   0058a8b0..0058a907 (88)   audio_backend_stop_voice_0058a8b0
//   00597010..00597062 (83)   audio_voice_release_links_00597010
//   0058ac30..0058ac96 (103)  application_audio_backend_release_0058ac30
//   00589c00..00589d14 (277)  audio_channel_group_release_00589c00
// Addresses are computed as 32-bit integers, as the original does, because
// 00589c00 can index the record before the channel table (see below).
#include "audio_voice_stop_425.hpp"

namespace porsche {

namespace {

template <class T>
T* at(std::uint32_t va) { return reinterpret_cast<T*>(static_cast<std::uintptr_t>(va)); }

std::uint32_t voice_at(std::int32_t index) {
    // edi*32 - edi = edi*31, then *8 -> index * 0xf8
    return audio_voice_table_006b489c + static_cast<std::uint32_t>(index) * 0xf8u;
}
std::uint32_t channel_at(std::int32_t index) {
    // lea [i*8]; sub i; shl 4 -> index * 0x70 (index may be -1)
    return audio_backend_channels_006b4a00 + static_cast<std::uint32_t>(index) * 0x70u;
}

constexpr std::int32_t kNotFound = -8;

// The three "release this channel" tails of 00589c00 are identical.
void release_channel(AudioChannelRecord_425* record) {
    record->active = 0;
    record->group = 0;
    record->stamp = audio_backend_stamp_006b49a8;
}

} // namespace

// ---------------------------------------------------------------------------
// 0058a8b0 (88 bytes). Calls the record's stop callback with &link_a, then reads
// the flags (after the call): bit 1 clears +0xf4, otherwise bit 2 releases the
// link list; independently, flag 0x10 (re-read from memory) releases the
// channel's group membership. The body returns 0; Run 400 declares it void.
// ---------------------------------------------------------------------------
void __cdecl audio_backend_stop_voice_0058a8b0(std::uint32_t voice_slot) {
    const std::uint32_t rec_va = voice_at(static_cast<std::int32_t>(voice_slot));
    AudioVoiceRecord_425* rec = at<AudioVoiceRecord_425>(rec_va);
    rec->stop_callback(rec_va + 0x2c);                    // push esi+2c; call [esi+0c8]
    const std::uint32_t flags = rec->flags;               // mov eax,[esi]
    if (flags & 1u) {
        rec->field_f4 = 0;
    } else if (flags & 2u) {
        audio_voice_release_links_00597010(rec_va + 0x64);
    }
    if (*at<std::uint8_t>(rec_va) & 0x10u) {              // test byte ptr [esi],10h
        audio_channel_group_release_00589c00(voice_slot);
    }
}

// ---------------------------------------------------------------------------
// 00597010 (83 bytes). The voice index is the signed word at link_b + 2. Every
// node on the record's list is released except the two embedded ones; the next
// pointer is read before the release, and the head is advanced after it.
// ---------------------------------------------------------------------------
void __cdecl audio_voice_release_links_00597010(std::uint32_t link_b_va) {
    const std::int32_t voice = *at<std::int16_t>(link_b_va + 2);        // movsx eax,word [eax+2]
    const std::uint32_t rec_va = voice_at(voice);
    AudioVoiceRecord_425* rec = at<AudioVoiceRecord_425>(rec_va);
    if (rec->link_head == 0) {
        return;
    }
    const std::uint32_t embedded_a = rec_va + 0x2c;
    const std::uint32_t embedded_b = rec_va + 0x64;
    std::uint32_t next;
    do {
        const std::uint32_t node = rec->link_head;
        next = *at<std::uint32_t>(node);                  // mov edi,[eax] before the call
        if (node != embedded_a && node != embedded_b) {
            application_audio_backend_release_0058ac30(node);
        }
        rec->link_head = next;
    } while (next != 0);
}

// ---------------------------------------------------------------------------
// 0058ac30 (103 bytes). Find the entry whose offset equals block - first and
// remove it: the entry count (negative) moves one towards zero, the limit grows
// by 8, and the entries below are shifted up one slot to close the gap. Not
// found, or an empty table (count >= 0), leaves everything untouched. The body
// returns -8 or 0 in eax; the canonical declaration is void and the only caller
// (00597010) ignores it.
// ---------------------------------------------------------------------------
void __cdecl application_audio_backend_release_0058ac30(std::uint32_t block) {
    AudioPoolHeader_425* pool = at<AudioPoolHeader_425>(audio_backend_pool_006b4a18);
    const std::uint32_t offset = block - pool->first_aligned;
    std::int32_t count = pool->entry_count;
    std::int32_t index = 0;
    if (count >= 0) {
        return;                                           // kNotFound
    }
    std::uint32_t entry = pool->end_marker;
    while (*at<std::uint32_t>(entry) != offset) {
        --index;
        entry -= 8;
        if (!(index > count)) {
            return;                                       // kNotFound
        }
    }
    ++count;
    pool->entry_count = count;
    pool->limit += 8;
    const std::int32_t live = pool->entry_count;
    if (index <= live) {
        return;
    }
    std::uint32_t dst = pool->end_marker + static_cast<std::uint32_t>(index) * 8u;
    std::uint32_t src = dst - 8;
    std::int32_t remaining = index - live;
    do {
        *at<std::uint32_t>(dst) = *at<std::uint32_t>(src);
        src -= 8;
        *at<std::uint32_t>(dst + 4) = *at<std::uint32_t>(src + 0xc);
        dst -= 8;
    } while (--remaining != 0);
}

// ---------------------------------------------------------------------------
// 00589c00 (277 bytes). Leave the channel's voice group.
//
// An ungrouped channel is simply released (active 0, group 0, stamp). Otherwise
// the body counts the live members of the group (same group, handle >= 0,
// active != 0) and remembers the LAST member whose leader byte is set; that
// index starts at -1. One member: release this channel. Two members whose
// leader has active 2 and is not this channel: release both. The leader being
// this channel with active 1: promote it to active 2 and keep it. Anything else:
// release this channel.
//
// Faithfulness note: when no member has the leader byte set and the count is
// not 1, the original indexes record -1, 0x70 bytes before the table, reads its
// active byte and, if that is 2 with exactly two members, releases it too. This
// recovery computes the same address and does the same; it does not invent a
// bound the original lacks.
// ---------------------------------------------------------------------------
void __cdecl audio_channel_group_release_00589c00(std::uint32_t channel) {
    const std::int32_t self_index = static_cast<std::int32_t>(channel);
    AudioChannelRecord_425* self = at<AudioChannelRecord_425>(channel_at(self_index));
    const std::uint32_t group = self->group;
    if (group == 0) {
        release_channel(self);
        return;
    }
    std::int32_t members = 0;
    std::int32_t leader = -1;
    const std::int32_t count = audio_backend_channel_count_006b49a4;    // movsx, read once
    for (std::int32_t i = 0; i < count; ++i) {
        const AudioChannelRecord_425* r = at<AudioChannelRecord_425>(channel_at(i));
        if (r->group != group || r->handle < 0 || r->active == 0) {
            continue;
        }
        ++members;
        if (r->leader != 0) {
            leader = i;
        }
    }
    if (members == 1) {
        release_channel(self);
        return;
    }
    AudioChannelRecord_425* lead = at<AudioChannelRecord_425>(channel_at(leader));
    const std::uint8_t lead_active = lead->active;
    if (lead_active == 2 && self_index != leader && members == 2) {
        release_channel(self);
        release_channel(lead);
        return;
    }
    if (lead_active == 1 && self_index == leader) {
        lead->active = 2;
        return;
    }
    release_channel(self);
}

} // namespace porsche

#include "porsche/application_audio_init.hpp"

#include "porsche/application_services.hpp"
#include "porsche/application_state.hpp"
#include "porsche/file_events.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>

namespace porsche {

std::uint32_t application_audio_device_configured_00655d40 = 0;
std::uint8_t application_audio_post_init_byte_00656868 = 0;
std::uint8_t application_audio_post_init_byte_00656869 = 0;

namespace {

// Immutable source bytes covering 005b4ac0..005b4b3f. 004a66b0 indexes the
// table bytes at 005b4ae4, 005b4af0, 005b4afc, 005b4b08, 005b4b14,
// 005b4b20, and 005b4b2c with a four-byte stride. Keep the surrounding bytes
// so negative mode indices down to -8 preserve the original adjacent reads;
// values below that are outside the startup mode domain and remain open.
constexpr std::array<std::uint8_t, 0x80> kOriginalAudioModeData = {
    0x66,0x66,0x46,0x41,0x78,0x52,0x5c,0x00,0x80,0x56,0x4a,0x00,0x60,0x56,0x4a,0x00,
    0x70,0x56,0x4a,0x00,0xc0,0x52,0x5c,0x00,0x80,0x56,0x4a,0x00,0x60,0x56,0x4a,0x00,
    0x70,0x56,0x4a,0x00,0x00,0x7d,0x00,0x00,0x22,0x56,0x00,0x00,0x80,0x3e,0x00,0x00,
    0x20,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x08,0x00,0x00,0x00,0x18,0x00,0x00,0x00,
    0x10,0x00,0x00,0x00,0x0c,0x00,0x00,0x00,0x30,0x00,0x00,0x00,0x18,0x00,0x00,0x00,
    0x0c,0x00,0x00,0x00,0x08,0x00,0x00,0x00,0x14,0x00,0x00,0x00,0x32,0x00,0x00,0x00,
    0x64,0x00,0x00,0x00,0x3c,0x00,0x00,0x00,0x1e,0x00,0x00,0x00,0x91,0x00,0x00,0x00,
    0x91,0x00,0x00,0x00,0x91,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xf0,0x40
};
constexpr std::uint32_t kAudioModeDataVa = 0x005b4ac0u;

std::size_t table_offset(std::uint32_t table_va, std::int32_t mode,
    std::size_t width) {
    const auto address = static_cast<std::int64_t>(table_va) +
        static_cast<std::int64_t>(mode) * 4;
    const auto offset = address - static_cast<std::int64_t>(kAudioModeDataVa);
    if (offset < 0 || static_cast<std::uint64_t>(offset) + width >
        kOriginalAudioModeData.size())
        throw std::out_of_range("audio mode lies outside pinned original data window");
    return static_cast<std::size_t>(offset);
}

std::uint8_t table_byte(std::uint32_t va, std::int32_t mode) {
    return kOriginalAudioModeData[table_offset(va, mode, 1)];
}

std::uint32_t table_dword(std::uint32_t va, std::int32_t mode) {
    const auto offset = table_offset(va, mode, 4);
    return static_cast<std::uint32_t>(kOriginalAudioModeData[offset]) |
        (static_cast<std::uint32_t>(kOriginalAudioModeData[offset + 1]) << 8) |
        (static_cast<std::uint32_t>(kOriginalAudioModeData[offset + 2]) << 16) |
        (static_cast<std::uint32_t>(kOriginalAudioModeData[offset + 3]) << 24);
}

std::int32_t signed_dword(std::uint32_t value) noexcept {
    std::int32_t result{};
    std::memcpy(&result, &value, sizeof(result));
    return result;
}

std::uint16_t get_u16(const AudioInitDescriptor& descriptor, std::size_t offset) {
    return static_cast<std::uint16_t>(descriptor[offset]) |
        static_cast<std::uint16_t>(static_cast<std::uint16_t>(descriptor[offset + 1]) << 8);
}

void put_u16(AudioInitDescriptor& descriptor, std::size_t offset, std::uint16_t value) {
    descriptor[offset] = static_cast<std::uint8_t>(value);
    descriptor[offset + 1] = static_cast<std::uint8_t>(value >> 8);
}

} // namespace

void __cdecl application_audio_post_setup_004ab470() {
    if (application_audio_device_configured_00655d40 != 0)
        application_audio_period_control_00565c70(
            0x80, 0, 0x28, 0xffffffffu, 0xffffffffu);
    application_audio_period_control_00565c70(
        0x20, 0, 0x28, 0xffffffffu, 0xffffffffu);
    application_audio_post_init_byte_00656869 = 0;
    application_audio_post_init_byte_00656868 = 0;
}

std::uint8_t __cdecl application_audio_initialize_004a66b0() {
    const auto mode = signed_dword(application_state_006573e8.word(0x00657c98u));
    application_audio_prepare_00565950(); // original EAX is ignored

    AudioInitDescriptor descriptor{};
    const auto query = application_audio_query_config_00565680(descriptor.data());
    if (query < 0) {
        application_audio_device_configured_00655d40 = 0;
        return 0;
    }

    std::uint32_t zero = 0;
    if (mode < 3) {
        const auto gate = application_state_006573e8.word(0x00657c9cu);
        descriptor[0x18] = 0x40;
        descriptor[0x19] = 0;
        descriptor[0x27] = 1;
        descriptor[0x28] = 0x24;
        descriptor[0x1f] = 0;
        descriptor[0x1d] = table_byte(0x005b4b08u, mode);
        descriptor[0x23] = 0;
        application_audio_device_configured_00655d40 = 0;

        if (gate != 0 && descriptor[8] != 0) {
            const auto count = static_cast<std::int32_t>(descriptor[0x0a]);
            if (count > 0) {
                const auto mask = static_cast<std::uint8_t>(
                    table_byte(0x005b4b2cu, mode));
                std::int32_t found = -1;
                for (std::int32_t i = 0; i < count; ++i) {
                    if ((descriptor[0x0b + static_cast<std::size_t>(i)] & mask) == mask) {
                        found = i;
                        break;
                    }
                }
                if (found >= 0) {
                    const auto cap = table_dword(0x005b4af0u, mode);
                    descriptor[0x27] = 2;
                    descriptor[0x29] = 0x24;
                    const auto selected = descriptor[0x0b + static_cast<std::size_t>(found)];
                    descriptor[0x28] = selected;
                    auto sample_count = static_cast<std::uint32_t>(descriptor[8]);
                    if (sample_count > cap) sample_count = cap;
                    descriptor[0x1f] = static_cast<std::uint8_t>(sample_count);
                    auto range = static_cast<std::uint8_t>(
                        table_byte(0x005b4afcu, mode) - descriptor[0x1f]);
                    range = static_cast<std::uint8_t>(range +
                        table_byte(0x005b4af0u, mode));
                    descriptor[0x23] = 1;
                    descriptor[0x1d] = range;
                    application_audio_device_configured_00655d40 = 1;
                }
            }
        }

        descriptor[0x25] = table_byte(0x005b4b20u, mode);
        descriptor[0x21] = table_byte(0x005b4b14u, mode);
        const auto maximum = signed_dword(table_dword(0x005b4ae4u, mode));
        const auto requested = static_cast<std::int32_t>(get_u16(descriptor, 2));
        auto adjusted = get_u16(descriptor, 2);
        if (maximum <= requested)
            adjusted = static_cast<std::uint16_t>(maximum);
        put_u16(descriptor, 0x1a, adjusted);
        descriptor[0x1c] = 2;
        descriptor[0x24] = static_cast<std::uint8_t>(zero);
        descriptor[0x22] = static_cast<std::uint8_t>(zero);
    }

    application_audio_apply_config_005656d0(descriptor.data());
    const auto result = application_audio_create_device_00565720(
        application_audio_buffer_00655d44, 0x40000, 3);
    if (result < 0) return 0;

    if (mode < 2) {
        if (application_audio_device_configured_00655d40 != 0) {
            const auto rate = signed_dword(timer_rate_005deb48);
            const auto rounded = rate < 0 ? rate + 1 : rate;
            // The original uses CDQ; SUB EAX,EDX; SAR EAX,1. The bias
            // converts truncating division into arithmetic-shift rounding.
            // C++ division alone would truncate the biased negative value
            // toward zero, so explicitly round that value down.
            const auto interval = rounded / 2 -
                (rounded < 0 && rounded % 2 != 0 ? 1 : 0);
            application_audio_wait_0053c380(interval);
        }
        application_audio_post_setup_004ab470();
    }
    return 1;
}

} // namespace porsche

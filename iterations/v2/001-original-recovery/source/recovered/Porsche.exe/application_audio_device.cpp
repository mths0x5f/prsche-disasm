#include "porsche/application_audio_device.hpp"

#include <cstring>

namespace porsche {

#ifndef PORSCHE_AUDIO_STATE_BLOCK
ApplicationAudioDeviceStateStorage application_audio_device_state_006b48c0{};
#endif
// In the game target this storage lies inside the audio state block (Run 427,
// 006b00c0..006b4a44), which also places the backend cells it contains
// (006b499c, 006b49a4, 006b4a00, 006b4a18, ...) at their original offsets.
std::uint32_t application_audio_descriptor_initialized_006a5c30 = 0;
// Original defined-data row 005e2470 is exactly 60 bytes including NUL.
char application_audio_author_text_005e2470[60] =
    "SNDAUTHOR: Dave Mercier, Friday 03:06PM Mar 03, 2000, V4.1g";
// Native pointer view of the original .data cell 005e246c -> 005e2470.
char* application_audio_marker_pointer_005e246c = application_audio_author_text_005e2470;
static_assert(sizeof(application_audio_author_text_005e2470) == 60);

namespace {
constexpr std::size_t kDescriptorBytes = 0x7c;
constexpr std::size_t kAudioStateCopyBytes = 0x60;

void copy_dwords_forward(std::uint8_t* destination, const std::uint8_t* source,
    std::size_t bytes) noexcept {
    for (std::size_t offset = 0; offset < bytes; offset += sizeof(std::uint32_t)) {
        std::uint32_t word{};
        std::memcpy(&word, source + offset, sizeof(word));
        std::memcpy(destination + offset, &word, sizeof(word));
    }
}

std::uint16_t read_u16(std::size_t offset) noexcept {
    return static_cast<std::uint16_t>(application_audio_device_state_006b48c0[offset]) |
        static_cast<std::uint16_t>(application_audio_device_state_006b48c0[offset + 1] << 8);
}

std::uint32_t read_u32(std::size_t offset) noexcept {
    std::uint32_t value{};
    std::memcpy(&value, application_audio_device_state_006b48c0.data() + offset,
        sizeof(value));
    return value;
}

void write_u16(std::size_t offset, std::uint16_t value) noexcept {
    application_audio_device_state_006b48c0[offset] = static_cast<std::uint8_t>(value);
    application_audio_device_state_006b48c0[offset + 1] = static_cast<std::uint8_t>(value >> 8);
}

void write_u32(std::size_t offset, std::uint32_t value) noexcept {
    std::memcpy(application_audio_device_state_006b48c0.data() + offset, &value,
        sizeof(value));
}

std::int32_t signed_word(std::uint16_t value) noexcept {
    return value < 0x8000u ? static_cast<std::int32_t>(value)
        : static_cast<std::int32_t>(value) - 0x10000;
}

} // namespace

std::int32_t __cdecl application_audio_query_config_00565680(
    std::uint8_t* descriptor) {
    std::int32_t result = 0;
    if (application_audio_descriptor_initialized_006a5c30 == 0) {
        result = application_audio_backend_initialize_0058a4f0();
        write_u16(0x18, 0x10);
        application_audio_descriptor_initialized_006a5c30 = 1;
        std::memcpy(application_audio_device_state_006b48c0.data() + 0x7c,
            application_audio_device_state_006b48c0.data() + 0x14,
            kAudioStateCopyBytes);
    }
    copy_dwords_forward(descriptor, application_audio_device_state_006b48c0.data(),
        kDescriptorBytes);
    return result;
}

std::uint32_t __cdecl application_audio_apply_config_005656d0(
    const std::uint8_t* descriptor) {
    std::uint32_t dword{};
    std::memcpy(&dword, descriptor + 0x78, sizeof(dword));
    copy_dwords_forward(application_audio_device_state_006b48c0.data() + 0x14,
        descriptor + 0x14, kAudioStateCopyBytes);
    write_u32(0x78, dword);
    std::memcpy(&dword, descriptor + 0x74, sizeof(dword));
    write_u32(0x74, dword);
    application_audio_backend_apply_0058a690();
    std::memcpy(application_audio_device_state_006b48c0.data() + 0x7c,
        application_audio_device_state_006b48c0.data() + 0x14,
        kAudioStateCopyBytes);
    return 0;
}

std::int32_t __cdecl application_audio_create_device_00565720(
    std::uint32_t buffer_va, std::uint32_t buffer_bytes,
    std::uint32_t device_flags) {
    (void)device_flags; // The original caller supplies this stack word; body never reads it.
    *application_audio_marker_pointer_005e246c = 0x53;
    if (application_audio_device_state_006b48c0[0xdc] != 0)
        return 0;

    application_audio_backend_configure_0058fef0(buffer_va, buffer_bytes);
    application_audio_backend_configure_0058aa90(buffer_va, buffer_bytes);

    if (read_u16(0xe4) == 0) {
        const auto query = application_audio_query_config_00565680(
            application_audio_device_state_006b48c0.data());
        if (query < 0)
            return query;
        application_audio_apply_config_005656d0(
            application_audio_device_state_006b48c0.data());
    }

    const auto channels = signed_word(read_u16(0xe4));
    const auto channel_bytes = static_cast<std::uint32_t>(channels) * 0x70u;
    write_u32(0x140,
        application_audio_backend_allocate_0058aae0(channel_bytes));
    const auto format = read_u16(0x18);
    const auto sample_bytes = static_cast<std::uint32_t>(format) * 12u;
    write_u32(0x144,
        application_audio_backend_allocate_0058aae0(sample_bytes));

    if (read_u32(0xec) == 0)
        write_u32(0xec, 0x00589520u);
    application_audio_backend_start_0058e2d0();
    write_u32(0xe8, 0);
    application_audio_device_state_006b48c0[0xdd] = 0x7f;
    application_audio_device_state_006b48c0[0xe2] = 0;
    application_audio_device_state_006b48c0[0xe0] = 0;
    application_audio_device_state_006b48c0[0xe1] = 0;

    const auto result = application_audio_backend_start_device_0058fdb0();
    if (result < 0) {
        application_audio_backend_stop_device_0058fe80();
        application_audio_backend_stop_0058e2e0();
        return result;
    }

    application_audio_device_state_006b48c0[0xdc] = 1;
    const bool alternate = application_audio_device_state_006b48c0[0x1c] == 2;
    write_u16(0x164, alternate ? 0xc000 : 0xe000);
    write_u16(0x166, alternate ? 0x4000 : 0x2000);
    write_u16(0x16c, 0xd555);
    write_u16(0x16e, 0x2aaa);
    write_u16(0x170, 0x8000);
    // The second pair consumes ECX/EAX set before the mode branch; unlike the
    // first pair, those registers are not changed by the alternate path.
    write_u16(0x174, 0xe000);
    write_u16(0x176, 0x2000);
    write_u16(0x178, 0xa000);
    write_u16(0x17a, 0x6000);
    application_audio_backend_finalize_0058e0e0();
    return 0;
}

} // namespace porsche

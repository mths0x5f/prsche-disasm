#include "porsche/formatter_cleanup.hpp"

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace porsche {
namespace {

std::uint32_t tail_word(const FormatterOriginalDescriptor32* descriptor,
                        std::size_t offset) {
    std::uint32_t value;
    std::memcpy(&value, descriptor->opaque_tail + offset, sizeof(value));
    return value;
}

std::int32_t arithmetic_shift_right_5(std::uint32_t bits) {
    std::uint32_t shifted = bits >> 5;
    if ((bits & 0x80000000u) != 0) shifted |= 0xf8000000u;
    std::int32_t value;
    std::memcpy(&value, &shifted, sizeof(value));
    return value;
}

std::int32_t signed_bits(std::uint32_t bits) {
    std::int32_t value;
    std::memcpy(&value, &bits, sizeof(value));
    return value;
}

std::uint32_t pointer_difference_bits(const char* lhs, const char* rhs) {
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(lhs)) -
           static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(rhs));
}


void set_cleanup_error(FormatterOriginalDescriptor32* descriptor) {
    descriptor->flags |= 0x20u;
}

} // namespace

// Exact 005abf35 consumer: unsigned range test, 32 handles per bank, 36-byte
// records, character-device flag at record +4 / bit 0x40.
std::uint32_t cleanup_is_character_device_005abf35(std::uint32_t file_id) {
    if (file_id >= formatter_cleanup_handle_limit_006c02e0) return 0;
    const std::int32_t bank = arithmetic_shift_right_5(file_id);
    const std::uint32_t slot = file_id & 0x1fu;
    const std::uint8_t* bank_base = bank == -1
        ? formatter_cleanup_preceding_handle_bank_006c01dc
        : formatter_cleanup_handle_table_006c01e0[bank];
    const auto* record = bank_base + slot * 0x24u;
    return record[4] & 0x40u;
}


std::int32_t __cdecl formatter_cleanup_005a4259(
    std::uint32_t character, FormatterOriginalDescriptor32* descriptor) {
    // Original x86 loads +0x10 before flags, but early exits never consume it.
    // Snapshot bytes as representation only; do not evaluate an indeterminate
    // stack DWORD from 005a0fbf's uninitialized descriptor tail.
    std::uint8_t file_id_representation[4];
    std::memcpy(file_id_representation, descriptor->opaque_tail,
                sizeof(file_id_representation));
    std::uint32_t flags = descriptor->flags;
    if ((flags & 0x82u) == 0 || (flags & 0x40u) != 0) {
        set_cleanup_error(descriptor);
        return -1;
    }

    std::uint32_t file_id;
    std::memcpy(&file_id, file_id_representation, sizeof(file_id));

    if ((flags & 1u) != 0) {
        descriptor->remaining = 0;
        if ((flags & 0x10u) == 0) {
            set_cleanup_error(descriptor);
            return -1;
        }
        descriptor->cursor = descriptor->base;
        flags &= ~1u;
        descriptor->flags = flags;
    }

    descriptor->remaining = 0;
    flags = (descriptor->flags & ~0x10u) | 2u;
    descriptor->flags = flags;

    if ((flags & 0x10cu) == 0) {
        const bool special = descriptor == formatter_cleanup_stream_005e5508 ||
                             descriptor == formatter_cleanup_stream_005e5528;
        if (!special || cleanup_is_character_device_005abf35(file_id) == 0)
            (void)formatter_cleanup_prepare_descriptor_005abef1(descriptor);
    }

    // 005a42cb tests the descriptor again after 005abef1, which may mutate it.
    flags = descriptor->flags;
    if ((flags & 0x108u) == 0) {
        const std::uint32_t word = character;
        const std::int32_t result = formatter_cleanup_file_write_005a9e49(
            file_id, &word, 1);
        if (result != 1) {
            set_cleanup_error(descriptor);
            return -1;
        }
        return static_cast<std::int32_t>(character & 0xffu);
    }

    const std::int32_t expected = signed_bits(
        pointer_difference_bits(descriptor->cursor, descriptor->base));
    descriptor->cursor = descriptor->base + 1;
    const std::int32_t buffer_size = signed_bits(tail_word(descriptor, 8));
    const std::uint32_t remaining_bits =
        static_cast<std::uint32_t>(buffer_size) - 1u;
    std::memcpy(&descriptor->remaining, &remaining_bits, sizeof(remaining_bits));

    std::int32_t result = 0;
    if (expected < 1) {
        const std::int32_t bank = arithmetic_shift_right_5(file_id);
        const std::uint8_t* bank_base = file_id == 0xffffffffu
            ? nullptr
            : (bank == -1 ? formatter_cleanup_preceding_handle_bank_006c01dc
                          : formatter_cleanup_handle_table_006c01e0[bank]);
        const std::uint8_t* record = file_id == 0xffffffffu
            ? formatter_cleanup_invalid_handle_record_005e5f50
            : bank_base + (file_id & 0x1fu) * 0x24u;
        if ((record[4] & 0x20u) != 0)
            (void)formatter_cleanup_file_aux_005a9ab8(file_id, 0, 2);
    } else {
        result = formatter_cleanup_file_write_005a9e49(
            file_id, descriptor->base, expected);
    }

    descriptor->base[0] = static_cast<char>(character);
    if (result == expected)
        return static_cast<std::int32_t>(character & 0xffu);
    set_cleanup_error(descriptor);
    return -1;
}

std::int32_t __cdecl formatter_original_cleanup_boundary_005a4259(
    std::uint32_t character, FormatterOriginalDescriptor32* descriptor) {
    return formatter_cleanup_005a4259(character, descriptor);
}

} // namespace porsche

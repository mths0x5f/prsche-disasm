#include "diagnostic_parsers.hpp"
#include "porsche/application_heap_state.hpp"
#include "porsche/exit_registry.hpp"

namespace porsche {
namespace {
std::uint8_t lower(std::uint8_t byte) {
    return byte >= 0x41u && byte <= 0x5au ? byte + 0x20u : byte;
}
std::uint32_t length(const char* text) {
    std::uint32_t count = 0;
    while (text[count] != 0) ++count;
    return count;
}
const char* name_pointer(std::uint32_t value) {
    return static_cast<const char*>(application_heap_pointer(value));
}
}

// 0055edf0..0055ee64. The comparison is inclusive: after copying the byte
// at min(strlen(source),capacity-1), the original writes another terminator.
// Recompute lengths while copying, preserving overlapping-buffer behavior.
void __cdecl application_diagnostic_copy_lower_0055edf0(const char* source,
    char* destination,std::uint32_t capacity) {
    std::uint32_t index = 0;
    for (;;) {
        auto limit = capacity - 1u;
        if (length(source) < limit) limit = length(source);
        if (limit < index) {
            destination[index] = 0;
            return;
        }
        destination[index] = static_cast<char>(lower(static_cast<std::uint8_t>(source[index])));
        ++index;
    }
}

// 0055eeb0..0055ef13: ASCII-only common-prefix length, not full equality.
std::int32_t __cdecl application_diagnostic_prefix_0055eeb0(const char* name,
    const char* token) {
    std::uint32_t matched = 0;
    while (name[matched] != 0) {
        const auto byte = static_cast<std::uint8_t>(token[matched]);
        if (byte == 0 || lower(static_cast<std::uint8_t>(name[matched])) != lower(byte)) break;
        ++matched;
    }
    return static_cast<std::int32_t>(matched);
}

// 0055ee70..0055eeae: names start four bytes before the callback view.
std::int32_t __cdecl application_diagnostic_device_lookup_0055ee70(const char* token) {
    std::int32_t best = -1, maximum = 0;
    for (std::uint32_t i = 0; i != 8; ++i) {
        const auto name = application_heap_load(application_heap_address(
            &application_diagnostic_device_image_005e1c88,i * 12u));
        if (name != 0) {
            const auto score = application_diagnostic_prefix_0055eeb0(name_pointer(name),token);
            if (maximum < score) { maximum = score; best = static_cast<std::int32_t>(i); }
        }
    }
    return best;
}

// 0055f0f0..0055f12e: strict comparison retains the first matching tie.
std::int32_t __cdecl application_diagnostic_channel_lookup_0055f0f0(const char* token) {
    std::int32_t best = -1, maximum = 0;
    for (std::uint32_t i = 0; i != 64; ++i) {
        const auto name = application_diagnostic_channels_005df4a0[i].name;
        if (name != 0) {
            const auto score = application_diagnostic_prefix_0055eeb0(name_pointer(name),token);
            if (maximum < score) { maximum = score; best = static_cast<std::int32_t>(i); }
        }
    }
    return best;
}

// 0055ed50..0055ede0. Long-input stack spill from the original fixed local
// buffer remains outside acceptance; do not silently clamp or enlarge it.
void __cdecl application_diagnostic_device_parse_0055ed50(const char* input) {
    char buffer[256];
    const char separators[] = " ,";
    application_diagnostic_copy_lower_0055edf0(input,buffer,0x100);
    auto* token = application_diagnostic_tokenize_005a30ee(buffer,separators);
    while (token != nullptr) {
        const auto disable = token[0] == '-';
        const auto index = application_diagnostic_device_lookup_0055ee70(token + (disable ? 1 : 0));
        if (index >= 0) application_diagnostic_device_set_0055ed20(static_cast<std::uint32_t>(index),disable ? 0 : 1);
        token = application_diagnostic_tokenize_005a30ee(nullptr,separators);
    }
}

// 0055f060..0055f0eb: channel parsing additionally recognizes ! and ;.
void __cdecl application_diagnostic_channel_parse_0055f060(const char* input) {
    char buffer[256];
    const char separators[] = " ,;";
    application_diagnostic_copy_lower_0055edf0(input,buffer,0x100);
    auto* token = application_diagnostic_tokenize_005a30ee(buffer,separators);
    while (token != nullptr) {
        const auto disable = token[0] == '-' || token[0] == '!';
        const auto index = application_diagnostic_channel_lookup_0055f0f0(token + (disable ? 1 : 0));
        if (index >= 0) application_diagnostic_channel_set_0055efd0(static_cast<std::uint32_t>(index),disable ? 0 : 1);
        token = application_diagnostic_tokenize_005a30ee(nullptr,separators);
    }
}

// 005a3050..005a3070: cache the return pointer before the unlock callback.
const char* __cdecl application_diagnostic_environment_005a3050(const char* name) {
    exit_registry_lock_api_005a4ba4(12);
    const auto value = application_diagnostic_environment_inner_005a3071(name);
    exit_registry_unlock_api_005a4c05(12);
    return value;
}
}

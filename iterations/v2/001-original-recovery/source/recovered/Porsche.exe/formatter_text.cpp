#include "porsche/formatter_text.hpp"

#if defined(PORSCHE_FORMATTER_TEXT_TRACE)
extern void formatter_text_read_trace(const void*, unsigned, std::uint32_t);
#endif

namespace porsche {
std::uint32_t formatter_text_locale_006afd80 = 0;
std::uint32_t formatter_text_locale_writer_006c02e4 = 0;
std::int32_t formatter_text_locale_readers_006c02e8 = 0;
FormatterTextAtomic formatter_text_increment_005b2258 = formatter_text_platform_increment;
FormatterTextAtomic formatter_text_decrement_005b2254 = formatter_text_platform_decrement;
namespace {
std::uint8_t read8(const void* p) {
    const auto v = *static_cast<const volatile std::uint8_t*>(p);
#if defined(PORSCHE_FORMATTER_TEXT_TRACE)
    formatter_text_read_trace(p, 1, v);
#endif
    return v;
}
std::uint16_t read16(const void* p) {
    const auto v = *static_cast<const volatile std::uint16_t*>(p);
#if defined(PORSCHE_FORMATTER_TEXT_TRACE)
    formatter_text_read_trace(p, 2, v);
#endif
    return v;
}
const std::uint8_t* class_pointer(int c) {
    return reinterpret_cast<const std::uint8_t*>(reinterpret_cast<std::uintptr_t>(
        formatter_ctype_table_005e52d0) + static_cast<std::uint32_t>(c) * 2u);
}
int ascii_case(int c, bool upper) {
    const int first = upper ? 'a' : 'A';
    return c >= first && c <= first + 25 ? c + (upper ? -32 : 32) : c;
}
int inner_case(int c, bool upper) {
    if (!formatter_text_locale_006afd80) return ascii_case(c, upper);
    const unsigned mask = upper ? 2u : 1u;
    if (c < 256) {
        const auto kind = formatter_float_character_width_005e54dc > 1
            ? static_cast<unsigned>(formatter_float_classify_005a2eae(c, mask))
            : read8(class_pointer(c)) & mask;
        if (!kind) return c;
    }
    const auto high = (static_cast<std::uint32_t>(c) >> 8) & 255u;
    const bool pair = (read8(class_pointer(high) + 1) & 0x80u) != 0;
    // These are the bytes written into the original by-value argument slot.
    char input[4] = {static_cast<char>(c), static_cast<char>(static_cast<unsigned>(c) >> 8),
        static_cast<char>(static_cast<unsigned>(c) >> 16), static_cast<char>(static_cast<unsigned>(c) >> 24)};
    if (pair) { input[0] = static_cast<char>(high); input[1] = static_cast<char>(c); input[2] = 0; }
    else input[1] = 0;
    char output[4];
    const int n = formatter_text_map_005a7e05(formatter_text_locale_006afd80,
        upper ? 0x200u : 0x100u, input, pair ? 2 : 1, output, 3, 0, 1);
    if (!n) return c;
    const auto low = static_cast<unsigned char>(output[0]);
    return n == 1 ? low : (static_cast<unsigned char>(output[1]) << 8) | low;
}
int outer_case(int c, bool upper) {
    if (!formatter_text_locale_006afd80) return ascii_case(c, upper);
    formatter_text_increment_005b2258(&formatter_text_locale_readers_006c02e8);
    const bool writer = formatter_text_locale_writer_006c02e4 != 0;
    const auto decrement = formatter_text_decrement_005b2254;
    if (writer) {
        decrement(&formatter_text_locale_readers_006c02e8);
        exit_registry_lock_api_005a4ba4(19);
    }
    const int result = upper ? formatter_text_upper_inner_005a269b(c)
                             : formatter_text_lower_inner_005a22b7(c);
    if (writer) exit_registry_unlock_api_005a4c05(19);
    else decrement(&formatter_text_locale_readers_006c02e8);
    return result;
}
int class_mask(int c, int mask, bool word) {
    if (formatter_float_character_width_005e54dc > 1)
        return formatter_float_classify_005a2eae(c, mask);
    return (word ? read16(class_pointer(c)) : read8(class_pointer(c))) & mask;
}
}
int __cdecl formatter_float_lower_005a2248(int c) { return outer_case(c, false); }
int __cdecl formatter_text_lower_inner_005a22b7(int c) { return inner_case(c, false); }
int __cdecl formatter_text_upper_005a262c(int c) { return outer_case(c, true); }
int __cdecl formatter_text_upper_inner_005a269b(int c) { return inner_case(c, true); }
int __cdecl formatter_float_classify_005a2eae(int c, int mask) {
    if (static_cast<std::uint32_t>(c) + 1u <= 256u) return read16(class_pointer(c)) & mask;
    const auto high = (static_cast<std::uint32_t>(c) >> 8) & 255u;
    const bool pair = (read8(class_pointer(high) + 1) & 0x80u) != 0;
    char input[3];
    input[0] = static_cast<char>(pair ? high : c);
    input[1] = pair ? static_cast<char>(c) : 0;
    if (pair) input[2] = 0;
    std::uint16_t output;
    if (!formatter_text_type_005a98c2(1, input, pair ? 2 : 1, &output, 0, 0, 1)) return 0;
    return output & mask;
}
int __cdecl formatter_text_alpha_005a2c24(int c) { return class_mask(c, 0x103, true); }
int __cdecl formatter_text_digit_005a2c52(int c) { return class_mask(c, 4, false); }
int __cdecl formatter_text_space_005a2c7a(int c) { return class_mask(c, 8, false); }
int __cdecl formatter_text_compare_n_005a2210(const char* first, const char* second, std::uint32_t n) {
    if (!n) return 0;
    std::uint32_t length = 0;
    do { ++length; } while (read8(first + length - 1) != 0 && length != n);
    std::uint32_t i = 0;
    do {
        const auto a = read8(first + i);
        const auto b = read8(second + i);
        ++i;
        if (b != a) break;
    } while (i != length);
    const auto b = read8(second + i - 1);
    const auto a = read8(first + i - 1);
    return a == b ? 0 : a > b ? 1 : -1;
}
std::uint32_t __cdecl formatter_text_reject_span_005a2e70(const char* text, const char* reject) {
    std::uint32_t bits[8] = {};
    for (;;) { const auto c = read8(reject++); if (!c) break; bits[c >> 5] |= 1u << (c & 31); }
    std::uint32_t n = 0;
    for (;;) { const auto c = read8(text++); if (!c || (bits[c >> 5] & (1u << (c & 31)))) return n; ++n; }
}
const char* __cdecl formatter_text_find_last_005a2870(const char* text, int value) {
    std::uint32_t n = 0;
    while (read8(text + n++)) {}
    const auto c = static_cast<std::uint8_t>(value);
    const char* p = text + n - 1;
    for (std::uint32_t remaining = n;;) {
        const auto v = read8(p);
        --remaining;
        if (v == c || !remaining) break;
        --p;
    }
    return read8(p) == c ? p : nullptr;
}
}

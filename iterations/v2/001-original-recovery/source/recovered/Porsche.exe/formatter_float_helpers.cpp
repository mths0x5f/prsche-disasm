#include "porsche/formatter_float_helpers.hpp"
#include <cstddef>
#include <cstring>

namespace porsche {
std::int32_t formatter_float_character_width_005e54dc = 1;
std::uint32_t formatter_float_decimal_word_005e54e0 = 0x2e;
const std::uint32_t formatter_float_pack64_config_005e6128[6] = {
    0x400, 0xfffffc01u, 0x35, 0xb, 0x40, 0x3ff
};
const std::uint32_t formatter_float_pack32_config_005e6140[6] = {
    0x80, 0xffffff81u, 0x18, 8, 0x20, 0x7f
};

void __cdecl formatter_float_decimal_005a3e33(char* text) {
    auto* cursor = text;
    if (formatter_float_lower_005a2248(static_cast<signed char>(*cursor)) != 'e') {
        int digit;
        do {
            ++cursor;
            const int value = static_cast<signed char>(*cursor);
            if (formatter_float_character_width_005e54dc > 1)
                digit = formatter_float_classify_005a2eae(value, 4);
            else
                digit = formatter_ctype_table_005e52d0[static_cast<std::ptrdiff_t>(value) * 2] & 4;
        } while (digit);
    }
    auto carry = static_cast<unsigned char>(*cursor);
    *cursor++ = static_cast<char>(formatter_float_decimal_word_005e54e0);
    for (;;) {
        const auto next = static_cast<unsigned char>(*cursor);
        *cursor = static_cast<char>(carry);
        // Original rereads the just-written byte to decide whether to stop.
        const bool done = *cursor++ == 0;
        carry = next;
        if (done) break;
    }
}
void __cdecl formatter_float_trim_005a3e8d(char* text) {
    char* cursor = text;
    const char decimal = static_cast<char>(formatter_float_decimal_word_005e54e0);
    while (*cursor && *cursor != decimal) ++cursor;
    if (!*cursor++) return;
    while (*cursor && *cursor != 'e' && *cursor != 'E') ++cursor;
    char* suffix = cursor;
    do { --cursor; } while (*cursor == '0');
    if (*cursor == decimal) --cursor;
    do { *++cursor = *suffix++; } while (*cursor);
}
int __cdecl formatter_float_sign_body_005a3edb(const double* number) {
    // Preserve original x87 FLD/FCOMP exceptions, condition codes, TOP and
    // existing stack. A C++ double comparison would change NaN/denormal effects.
    static const std::uint64_t zero = 0;
    unsigned short status;
    __asm {
        mov eax, number
        fld qword ptr [eax]
        fcomp qword ptr [zero]
        fnstsw status
    }
    return (status & 0x100u) == 0;
}
int __cdecl formatter_float_pack64_005abc73(const FormatterFloatWords12* words, void* output) {
    return formatter_float_pack_words_005abb07(words, output, formatter_float_pack64_config_005e6128);
}
int __cdecl formatter_float_pack32_005abc89(const FormatterFloatWords12* words, void* output) {
    return formatter_float_pack_words_005abb07(words, output, formatter_float_pack32_config_005e6140);
}
int __cdecl formatter_float_parse64_005abc9f(void* output, const char* text) {
    FormatterFloatWords12 words;
    const char* cursor = text;
    formatter_float_parse_words_005ac716(&words, &cursor, text, 0, 0, 0, 0);
    return formatter_float_pack64_005abc73(&words, output);
}
int __cdecl formatter_float_parse32_005abccc(void* output, const char* text) {
    FormatterFloatWords12 words;
    const char* cursor = text;
    formatter_float_parse_words_005ac716(&words, &cursor, text, 0, 0, 0, 0);
    return formatter_float_pack32_005abc89(&words, output);
}
void __cdecl formatter_float_assign_body_005a3ef3(int wide, void* output, const void* text) {
    if (wide) {
        std::uint32_t words[2];
        formatter_float_parse64_005abc9f(words, static_cast<const char*>(text));
        // Preserve the two original ordered DWORD stores after conversion.
        std::memcpy(output, words, 4);
        std::memcpy(static_cast<unsigned char*>(output) + 4, words + 1, 4);
    } else {
        std::uint32_t word;
        formatter_float_parse32_005abccc(&word, static_cast<const char*>(text));
        std::memcpy(output, &word, 4);
    }
}
void __cdecl formatter_float_convert_005a41e3(const void* number, char* output,
                                           int conversion, int precision, int caps) {
    if (conversion == 'e' || conversion == 'E')
        formatter_float_scientific_005a3f31(number, output, precision, caps);
    else if (conversion == 'f')
        formatter_float_fixed_005a4054(number, output, precision);
    else
        formatter_float_general_005a4150(number, output, precision, caps);
}
} // namespace porsche

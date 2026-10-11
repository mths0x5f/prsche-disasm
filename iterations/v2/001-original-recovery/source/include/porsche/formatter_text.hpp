#pragma once
#include "porsche/formatter_float_helpers.hpp"
#include "porsche/formatter_parser.hpp"
#include "porsche/exit_registry.hpp"

namespace porsche {
extern std::uint32_t formatter_text_locale_006afd80;
extern std::uint32_t formatter_text_locale_writer_006c02e4;
extern std::int32_t formatter_text_locale_readers_006c02e8;
using FormatterTextAtomic = std::int32_t (__stdcall *)(std::int32_t*);
extern FormatterTextAtomic formatter_text_increment_005b2258;
extern FormatterTextAtomic formatter_text_decrement_005b2254;
std::int32_t __stdcall formatter_text_platform_increment(std::int32_t*);
std::int32_t __stdcall formatter_text_platform_decrement(std::int32_t*);

// Original locale services remain typed boundaries, not host ctype replacements.
int __cdecl formatter_text_map_005a7e05(std::uint32_t locale, std::uint32_t flags,
    const char* input, int input_bytes, char* output, int output_bytes,
    std::uint32_t codepage, int reject_invalid);
int __cdecl formatter_text_type_005a98c2(std::uint32_t type, const char* input,
    int input_bytes, std::uint16_t* output, std::uint32_t codepage,
    std::uint32_t locale, int reject_invalid);
int __cdecl formatter_text_lower_inner_005a22b7(int);
int __cdecl formatter_text_upper_005a262c(int);
int __cdecl formatter_text_upper_inner_005a269b(int);
int __cdecl formatter_text_alpha_005a2c24(int);
int __cdecl formatter_text_digit_005a2c52(int);
int __cdecl formatter_text_space_005a2c7a(int);
int __cdecl formatter_text_compare_n_005a2210(const char*, const char*, std::uint32_t);
std::uint32_t __cdecl formatter_text_reject_span_005a2e70(const char*, const char*);
const char* __cdecl formatter_text_find_last_005a2870(const char*, int);
}

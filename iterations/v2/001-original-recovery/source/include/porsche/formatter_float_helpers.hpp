#pragma once
#include "porsche/formatter_bootstrap.hpp"

namespace porsche {
extern std::int32_t formatter_float_character_width_005e54dc;
extern std::uint32_t formatter_float_decimal_word_005e54e0;

struct FormatterFloatWords12 { std::uint32_t words[3]; };
extern const std::uint32_t formatter_float_pack64_config_005e6128[6];
extern const std::uint32_t formatter_float_pack32_config_005e6140[6];

int __cdecl formatter_float_parse64_005abc9f(void* output, const char* text);
int __cdecl formatter_float_parse32_005abccc(void* output, const char* text);
int __cdecl formatter_float_pack64_005abc73(const FormatterFloatWords12*, void*);
int __cdecl formatter_float_pack32_005abc89(const FormatterFloatWords12*, void*);

// Exact wrappers do not claim these original decimal/rounding engines.
int __cdecl formatter_float_parse_words_005ac716(FormatterFloatWords12*, const char**,
                                               const char*, int, int, int, int);
int __cdecl formatter_float_pack_words_005abb07(const FormatterFloatWords12*, void*,
                                              const std::uint32_t* config);
int __cdecl formatter_float_lower_005a2248(int);
int __cdecl formatter_float_classify_005a2eae(int, int mask);
char* __cdecl formatter_float_scientific_005a3f31(const void*, char*, int, int);
char* __cdecl formatter_float_fixed_005a4054(const void*, char*, int);
char* __cdecl formatter_float_general_005a4150(const void*, char*, int, int);
} // namespace porsche

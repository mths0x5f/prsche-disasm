#pragma once
#include "porsche/formatter_float_output.hpp"
namespace porsche {
int __cdecl formatter_float_tail_zero_005ab90d(const std::uint32_t*,int);
std::uint32_t __cdecl formatter_float_bump_bit_005ab956(std::uint32_t*,int);
int __cdecl formatter_float_round_words_005ab9ac(std::uint32_t*,int);
void __cdecl formatter_float_copy_words_005aba38(std::uint32_t*,const std::uint32_t*);
void __cdecl formatter_float_zero_words_005aba53(std::uint32_t*);
int __cdecl formatter_float_words_zero_005aba5f(const std::uint32_t*);
void __cdecl formatter_float_shift_words_005aba7a(std::uint32_t*,int);
void __cdecl formatter_float_digits_words_005adb88(const char*,std::uint32_t,FormatterFloatWords12*);
}

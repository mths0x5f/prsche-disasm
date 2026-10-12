#pragma once
#include "porsche/formatter_float_helpers.hpp"
namespace porsche {
struct FormatterFloatDecimal16 { std::int32_t sign,exponent,status; char* digits; };
struct FormatterFloatDecimal28 { std::int16_t exponent; char sign; std::uint8_t count; char digits[24]; };
char* __cdecl formatter_float_scientific_digits_005a3f92(char*,int,int,FormatterFloatDecimal16*,int);
char* __cdecl formatter_float_fixed_digits_005a40a9(char*,int,FormatterFloatDecimal16*,int);
void __cdecl formatter_float_shift_text_005a4234(char*,int);
void __cdecl formatter_float_round_digits_005abcf9(char*,int,FormatterFloatDecimal16*);
FormatterFloatDecimal16* __cdecl formatter_float_decimal_digits_005abd70(std::uint32_t,std::uint32_t,FormatterFloatDecimal16*,char*);
void __cdecl formatter_float_expand64_005abdcc(void*,const void*);
std::uint32_t __cdecl formatter_float_add_word_005adaae(std::uint32_t,std::uint32_t,std::uint32_t*);
void __cdecl formatter_float_add96_005adacf(FormatterFloatWords12*,const FormatterFloatWords12*);
void __cdecl formatter_float_left96_005adb2d(FormatterFloatWords12*);
void __cdecl formatter_float_right96_005adb5b(FormatterFloatWords12*);
int __cdecl formatter_float_extended_digits_005adc4f(std::uint32_t,std::uint32_t,std::uint32_t,int,int,FormatterFloatDecimal28*);
void __cdecl formatter_float_multiply96_005adf5b(FormatterFloatWords12*,const FormatterFloatWords12*);
void __cdecl formatter_float_scale96_005ae17b(FormatterFloatWords12*,std::int32_t,int);
extern const std::uint8_t formatter_float_powers_positive_005e6380[348];
extern const std::uint8_t formatter_float_powers_negative_005e64e0[348];
}

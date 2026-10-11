#pragma once
#include "porsche/formatter_text.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include <cstddef>

namespace porsche {
struct FormatterLocaleCodepageState {
    std::uint32_t codepage;
    std::uint32_t ids[3];
    std::uint32_t multibyte;
    std::uint8_t case_map[256];
    std::uint8_t class_bits[257];
    std::uint8_t padding[3];
    std::uint32_t locale;
};
static_assert(sizeof(FormatterLocaleCodepageState)==0x21c);
static_assert(offsetof(FormatterLocaleCodepageState,class_bits)==0x114);
static_assert(offsetof(FormatterLocaleCodepageState,locale)==0x218);
struct FormatterLocaleCPInfo { std::uint32_t max_character_bytes; std::uint8_t default_character[2]; std::uint8_t lead_ranges[12]; std::uint8_t padding[2]; };
static_assert(sizeof(FormatterLocaleCPInfo)==20);
extern FormatterLocaleCodepageState formatter_locale_codepage_006c02ec;
extern std::uint32_t formatter_locale_resolved_006afd68;
extern std::uint32_t formatter_locale_default_codepage_006afd90;
extern std::uint32_t formatter_locale_map_mode_006afd98;
extern std::uint32_t formatter_locale_type_mode_006afec4;
extern std::uint32_t formatter_locale_initialized_006c152c;

// Exact Kernel32 import signatures. Bindings belong to platform adapters.
int __stdcall formatter_locale_map_w(std::uint32_t,std::uint32_t,const std::uint16_t*,int,void*,int);
int __stdcall formatter_locale_map_a(std::uint32_t,std::uint32_t,const char*,int,char*,int);
int __stdcall formatter_locale_to_wide(std::uint32_t,std::uint32_t,const char*,int,std::uint16_t*,int);
int __stdcall formatter_locale_from_wide(std::uint32_t,std::uint32_t,const std::uint16_t*,int,char*,int,const char*,int*);
int __stdcall formatter_locale_type_w(std::uint32_t,const std::uint16_t*,int,std::uint16_t*);
int __stdcall formatter_locale_type_a(std::uint32_t,std::uint32_t,const char*,int,std::uint16_t*);
std::uint32_t __stdcall formatter_locale_oem_codepage();
std::uint32_t __stdcall formatter_locale_ansi_codepage();
int __stdcall formatter_locale_codepage_info(std::uint32_t,FormatterLocaleCPInfo*);

std::uint32_t __cdecl formatter_locale_bounded_length_005ad2bf(const char*,std::uint32_t);
int __cdecl formatter_locale_set_codepage_005a6895(int);
std::uint32_t __cdecl formatter_locale_resolve_codepage_005a6a42(int);
std::uint32_t __cdecl formatter_locale_codepage_lcid_005a6a8c(std::uint32_t);
void __cdecl formatter_locale_reset_005a6abf();
void __cdecl formatter_locale_build_tables_005a6ae8();
void __cdecl formatter_locale_initialize_005a6c6d();
}

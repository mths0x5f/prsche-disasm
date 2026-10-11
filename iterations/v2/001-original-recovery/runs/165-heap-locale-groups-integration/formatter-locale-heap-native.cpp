#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <cstring>
#include "porsche/formatter_locale.hpp"
#include "porsche/formatter_small_heap.hpp"

int main() {
    using namespace porsche;
    const auto heap=formatter_small_heap_create(0,0,0);
    if (!heap) return 1;
    auto* p=static_cast<unsigned char*>(formatter_crt_heap_allocate(heap,0,16));
    if (!p) return 2;
    std::memset(p,0x5a,16);
    p=static_cast<unsigned char*>(formatter_small_heap_reallocate(heap,HEAP_ZERO_MEMORY,p,64));
    if (!p || formatter_small_heap_size(heap,0,p)<64) return 3;
    for (unsigned i=0;i<64;++i) if (p[i]!=(i<16?0x5a:0)) return 4;
    if (!formatter_crt_heap_free(heap,0,p) || !formatter_small_heap_destroy(heap)) return 5;
    auto* region=static_cast<unsigned char*>(formatter_small_virtual_allocate(nullptr,0x20000,MEM_RESERVE,PAGE_READWRITE));
    if (!region) return 6;
    if (formatter_small_virtual_allocate(region,0x1000,MEM_COMMIT,PAGE_READWRITE)!=region) return 7;
    region[0]=0x51;region[0xfff]=0x52;
    if (!formatter_small_virtual_free(region,0x1000,MEM_DECOMMIT)) return 8;
    if (formatter_small_virtual_allocate(region,0x1000,MEM_COMMIT,PAGE_READWRITE)!=region || region[0] || region[0xfff]) return 9;
    if (!formatter_small_virtual_free(region,0,MEM_RELEASE)) return 10;
    constexpr std::uint32_t locale=0x409;
    const std::uint16_t upper[]={'A','B',0};
    std::uint16_t wide[4]={},types[4]={};char text[4]={};
    if (formatter_locale_map_w(locale,LCMAP_LOWERCASE,upper,-1,wide,4)!=3 || wide[0]!='a' || wide[1]!='b' || wide[2]) return 11;
    if (formatter_locale_map_a(locale,LCMAP_LOWERCASE,"AB",-1,text,4)!=3 || std::strcmp(text,"ab")) return 12;
    if (formatter_locale_to_wide(1252,0,"AB",-1,wide,4)!=3 || wide[0]!='A' || wide[1]!='B' || wide[2]) return 13;
    if (formatter_locale_from_wide(1252,0,upper,-1,text,4,nullptr,nullptr)!=3 || std::strcmp(text,"AB")) return 14;
    if (!formatter_locale_type_w(CT_CTYPE1,upper,2,types) || !(types[0]&C1_UPPER) || !(types[1]&C1_UPPER)) return 15;
    if (!formatter_locale_type_a(locale,CT_CTYPE1,"AB",2,types) || !(types[0]&C1_UPPER) || !(types[1]&C1_UPPER)) return 16;
    FormatterLocaleCPInfo info{};
    if (!formatter_locale_codepage_info(932,&info) || info.max_character_bytes!=2) return 17;
    if (formatter_locale_ansi_codepage()!=::GetACP() || formatter_locale_oem_codepage()!=::GetOEMCP()) return 18;
    std::puts("{\"fixture_passed\":true,\"heap_resize_size\":true,\"virtual_memory_lifecycle\":true,\"locale_map_convert_classify\":true,\"codepage_info\":true,\"game_launch_verified\":false}");
}

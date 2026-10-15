#include "porsche/formatter_search.hpp"
#include <intrin.h>
#if defined(PORSCHE_FORMATTER_SEARCH_TRACE)
extern void formatter_search_read_trace(const void*, unsigned, std::uint32_t);
#endif
namespace porsche {
namespace {
template<class T> T read(const void* p) {
    const T v=*static_cast<const volatile T*>(p);
#if defined(PORSCHE_FORMATTER_SEARCH_TRACE)
    formatter_search_read_trace(p,sizeof(T),v);
#endif
    return v;
}
std::uint8_t byte(const char* p) {return read<std::uint8_t>(p);}
std::uint8_t fold(std::uint8_t c) {
    return static_cast<std::uint8_t>(c+((static_cast<std::uint8_t>(c-0x41)<0x1a)?0x20:0));
}
}
const char* __cdecl formatter_search_character_005a2780(const char* text,int character) {
    const auto c=static_cast<std::uint8_t>(character);
    const char* p=text;
    while(reinterpret_cast<std::uintptr_t>(p)&3u) {
        const auto v=byte(p++);
        if(v==c)return p-1; // Shared original return tail at 005a2770.
        if(!v)return nullptr;
    }
    const std::uint32_t pattern=static_cast<std::uint32_t>(c)*0x01010101u;
    for(;;) {
        const auto v=read<std::uint32_t>(p);
        const auto x=v^pattern;
        const auto add_v=0x7efefeffu+v;
        const auto add_x=0x7efefeffu+x;
        const auto candidate=(~x^add_x)&0x81010100u;
        const auto zero=(~v^add_v)&0x81010100u;
        p+=4;
        if(candidate) {
            const auto again=read<std::uint32_t>(p-4);
            for(unsigned i=0;i!=4;++i) {
                const auto part=static_cast<std::uint8_t>(again>>(i*8));
                if(part==c)return p-4+i;
                if(!part)return nullptr;
            }
        } else if(zero) {
            if((zero&0x01010100u) || !(add_v&0x80000000u))return nullptr;
        }
    }
}
const char* __cdecl formatter_search_substring_005a1e10(const char* text,const char* needle) {
    const auto first=byte(needle);
    if(!first)return text;
    const auto second=byte(needle+1);
    if(!second)return formatter_search_character_005a2780(text,first); // Original tail JMP 005a2786.
    const char* candidate=text;
    const char* p;
    const char* n;
    std::uint8_t a,b;
restart:
    p=candidate;n=needle;a=byte(candidate);++p;
search:
    if(a!=first) {
        if(!a)return nullptr;
        a=byte(p++);goto search;
    }
    a=byte(p++);
    if(a!=second)goto search;
    candidate=p-1;
pair:
    b=byte(n+2);
    if(!b)return candidate-1;
    a=byte(p);p+=2;
    if(a!=b)goto restart;
    a=byte(n+3);
    if(!a)return candidate-1;
    b=byte(p-1);n+=2;
    if(a==b)goto pair;
    goto restart;
}
std::int32_t __cdecl formatter_search_compare_005ae3c0(const char* left,const char* right) {
    if(!formatter_text_locale_006afd80) {
        std::uint8_t a=0xff,b;
        while(a) {
            a=byte(right++);b=byte(left++);
            if(a==b)continue;
            const auto right_fold=fold(a);a=fold(b);
            if(a!=right_fold)return a<right_fold?-1:1;
        }
        return static_cast<std::int8_t>(a);
    }
    auto* readers=reinterpret_cast<volatile long*>(&formatter_text_locale_readers_006c02e8);
    _InterlockedIncrement(readers);
    const bool writer=static_cast<std::int32_t>(formatter_text_locale_writer_006c02e4)>0;
    if(writer) {_InterlockedDecrement(readers);exit_registry_lock_api_005a4ba4(19);}
    std::uint32_t a=0xff,b=0;
    while(static_cast<std::uint8_t>(a)) {
        a=(a&0xffffff00u)|byte(right++);
        b=(b&0xffffff00u)|byte(left++);
        if(static_cast<std::uint8_t>(a)==static_cast<std::uint8_t>(b))continue;
        b=formatter_text_lower_inner_005a22b7(static_cast<int>(b));
        a=formatter_text_lower_inner_005a22b7(static_cast<int>(a));
        if(static_cast<std::uint8_t>(b)!=static_cast<std::uint8_t>(a)) {
            a=static_cast<std::uint8_t>(b)<static_cast<std::uint8_t>(a)?0xffffffffu:1u;break;
        }
    }
    const auto result=static_cast<std::int32_t>(a);
    if(writer)exit_registry_unlock_api_005a4c05(19);else _InterlockedDecrement(readers);
    return result;
}
}

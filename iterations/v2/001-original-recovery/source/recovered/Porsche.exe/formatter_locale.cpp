#include "porsche/formatter_locale.hpp"
#include <malloc.h>

#if defined(PORSCHE_FORMATTER_LOCALE_PROBE)
extern void formatter_locale_stack_observer(std::uint32_t,unsigned);
#define LOCALE_STACK(bytes,site) (formatter_locale_stack_observer(bytes,site),_alloca(bytes))
#else
#define LOCALE_STACK(bytes,site) _alloca(bytes)
#endif

namespace porsche {
FormatterLocaleCodepageState formatter_locale_codepage_006c02ec = {};
std::uint32_t formatter_locale_resolved_006afd68 = 0;
std::uint32_t formatter_locale_default_codepage_006afd90 = 0;
std::uint32_t formatter_locale_map_mode_006afd98 = 0;
std::uint32_t formatter_locale_type_mode_006afec4 = 0;
std::uint32_t formatter_locale_initialized_006c152c = 0;
namespace {
alignas(4) const std::uint8_t codepage_data[248] = {
#include "formatter_locale_data.inc"
};
const std::uint8_t probe_zero[12] = {};
std::uint32_t data32(unsigned offset) {
    return static_cast<std::uint32_t>(codepage_data[offset]) | (static_cast<std::uint32_t>(codepage_data[offset+1])<<8)
        | (static_cast<std::uint32_t>(codepage_data[offset+2])<<16) | (static_cast<std::uint32_t>(codepage_data[offset+3])<<24);
}
std::uint32_t allocation_bytes(int n) { return (static_cast<std::uint32_t>(n)*2u+3u)&~3u; }
void clear_classes() {
    auto* p=reinterpret_cast<volatile std::uint32_t*>(formatter_locale_codepage_006c02ec.class_bits);
    for(unsigned i=0;i<64;++i)p[i]=0;
    formatter_locale_codepage_006c02ec.class_bits[256]=0;
}
void clear_ids() { for(unsigned i=0;i<3;++i)formatter_locale_codepage_006c02ec.ids[i]=0; }
}
std::uint32_t __cdecl formatter_locale_bounded_length_005ad2bf(const char* text,std::uint32_t n) {
    auto* p=reinterpret_cast<const volatile std::uint8_t*>(text);
    if(n) {
        std::uint32_t remaining=n;
        while(*p) { ++p; if(!--remaining)break; }
    }
    return *p==0 ? static_cast<std::uint32_t>(p-reinterpret_cast<const volatile std::uint8_t*>(text)) : n;
}
int __cdecl formatter_text_map_005a7e05(std::uint32_t locale,std::uint32_t flags,
    const char* input,int count,char* output,int capacity,std::uint32_t codepage,int strict) {
    if(!formatter_locale_map_mode_006afd98) {
        if(formatter_locale_map_w(0,0x100,reinterpret_cast<const std::uint16_t*>(probe_zero+4),1,nullptr,0))
            formatter_locale_map_mode_006afd98=1;
        else if(formatter_locale_map_a(0,0x100,reinterpret_cast<const char*>(probe_zero),1,nullptr,0))
            formatter_locale_map_mode_006afd98=2;
        else return 0;
    }
    if(count>0)count=static_cast<int>(formatter_locale_bounded_length_005ad2bf(input,count));
    if(formatter_locale_map_mode_006afd98==2)return formatter_locale_map_a(locale,flags,input,count,output,capacity);
    if(formatter_locale_map_mode_006afd98!=1)return 0;
    if(!codepage)codepage=formatter_locale_default_codepage_006afd90;
    const int wide_count=formatter_locale_to_wide(codepage,strict?9u:1u,input,count,nullptr,0);
    if(!wide_count)return 0;
    std::uint16_t* wide_input;
    __try { wide_input=static_cast<std::uint16_t*>(LOCALE_STACK(allocation_bytes(wide_count),0)); }
    __except(1) { wide_input=nullptr; }
    if(!wide_input)return 0;
    if(!formatter_locale_to_wide(codepage,1,input,count,wide_input,wide_count))return 0;
    const int mapped_count=formatter_locale_map_w(locale,flags,wide_input,wide_count,nullptr,0);
    if(!mapped_count)return 0;
    if(flags&0x400u) {
        if(capacity) {
            if(mapped_count>capacity)return 0;
            if(!formatter_locale_map_w(locale,flags,wide_input,wide_count,output,capacity))return 0;
        }
        return mapped_count;
    }
    std::uint16_t* wide_output;
    __try { wide_output=static_cast<std::uint16_t*>(LOCALE_STACK(allocation_bytes(mapped_count),1)); }
    __except(1) { wide_output=nullptr; }
    if(!wide_output)return 0;
    if(!formatter_locale_map_w(locale,flags,wide_input,wide_count,wide_output,mapped_count))return 0;
    return formatter_locale_from_wide(codepage,0x220,wide_output,mapped_count,
        capacity?output:nullptr,capacity?capacity:0,nullptr,nullptr);
}
int __cdecl formatter_text_type_005a98c2(std::uint32_t type,const char* input,int count,
    std::uint16_t* output,std::uint32_t codepage,std::uint32_t locale,int strict) {
    auto mode=formatter_locale_type_mode_006afec4;
    if(!mode) {
        std::uint16_t probe_output;
        if(formatter_locale_type_w(1,reinterpret_cast<const std::uint16_t*>(probe_zero+4),1,&probe_output))mode=1;
        else if(formatter_locale_type_a(0,1,reinterpret_cast<const char*>(probe_zero),1,&probe_output))mode=2;
        else return 0;
        formatter_locale_type_mode_006afec4=mode;
    }
    if(mode==2)return formatter_locale_type_a(locale?locale:formatter_text_locale_006afd80,type,input,count,output);
    if(mode!=1)return 0;
    if(!codepage)codepage=formatter_locale_default_codepage_006afd90;
    const int queried=formatter_locale_to_wide(codepage,strict?9u:1u,input,count,nullptr,0);
    if(!queried)return 0;
    std::uint16_t* wide;
    __try {
        wide=static_cast<std::uint16_t*>(LOCALE_STACK(allocation_bytes(queried),2));
        formatter_crt_memset_005abe90(wide,0,static_cast<std::uint32_t>(queried)*2u);
    } __except(1) { wide=nullptr; }
    if(!wide)return 0;
    const int converted=formatter_locale_to_wide(codepage,1,input,count,wide,queried);
    if(!converted)return 0;
    return formatter_locale_type_w(type,wide,converted,output);
}
std::uint32_t __cdecl formatter_locale_resolve_codepage_005a6a42(int requested) {
    formatter_locale_resolved_006afd68=0;
    if(requested==-2) { formatter_locale_resolved_006afd68=1;return formatter_locale_oem_codepage(); }
    if(requested==-3) { formatter_locale_resolved_006afd68=1;return formatter_locale_ansi_codepage(); }
    if(requested==-4) { const auto result=formatter_locale_default_codepage_006afd90;formatter_locale_resolved_006afd68=1;return result; }
    return static_cast<std::uint32_t>(requested);
}
std::uint32_t __cdecl formatter_locale_codepage_lcid_005a6a8c(std::uint32_t cp) {
    switch(cp) {case 932:return 0x411;case 936:return 0x804;case 949:return 0x412;case 950:return 0x404;default:return 0;}
}
void __cdecl formatter_locale_reset_005a6abf() {
    clear_classes();
    formatter_locale_codepage_006c02ec.codepage=0;
    formatter_locale_codepage_006c02ec.multibyte=0;
    formatter_locale_codepage_006c02ec.locale=0;
    clear_ids();
}
void __cdecl formatter_locale_build_tables_005a6ae8() {
    FormatterLocaleCPInfo info;
    if(formatter_locale_codepage_info(formatter_locale_codepage_006c02ec.codepage,&info)==1) {
        std::uint8_t input[256]; std::uint16_t types[256]; std::uint8_t lower[256],upper[256];
        for(unsigned i=0;i<256;++i)input[i]=static_cast<std::uint8_t>(i);
        input[0]=0x20;
        const auto* range=info.lead_ranges;
        while(range[0]) {
            unsigned first=range[0],last=range[1];
            if(first<=last) {
                auto* destination=input+first;unsigned bytes=last-first+1;
                while(bytes>=4) { *reinterpret_cast<volatile std::uint32_t*>(destination)=0x20202020;destination+=4;bytes-=4; }
                while(bytes--) *destination++=0x20;
            }
            range+=2;
        }
        formatter_text_type_005a98c2(1,reinterpret_cast<const char*>(input),256,types,
            formatter_locale_codepage_006c02ec.codepage,formatter_locale_codepage_006c02ec.locale,0);
        formatter_text_map_005a7e05(formatter_locale_codepage_006c02ec.locale,0x100,
            reinterpret_cast<const char*>(input),256,reinterpret_cast<char*>(lower),256,formatter_locale_codepage_006c02ec.codepage,0);
        formatter_text_map_005a7e05(formatter_locale_codepage_006c02ec.locale,0x200,
            reinterpret_cast<const char*>(input),256,reinterpret_cast<char*>(upper),256,formatter_locale_codepage_006c02ec.codepage,0);
        for(unsigned i=0;i<256;++i) {
            const auto type=*reinterpret_cast<const volatile std::uint16_t*>(types+i);
            if(type&1) {formatter_locale_codepage_006c02ec.class_bits[i+1]|=0x10;formatter_locale_codepage_006c02ec.case_map[i]=lower[i];}
            else if(type&2) {formatter_locale_codepage_006c02ec.class_bits[i+1]|=0x20;formatter_locale_codepage_006c02ec.case_map[i]=upper[i];}
            else formatter_locale_codepage_006c02ec.case_map[i]=0;
        }
    } else {
        for(unsigned i=0;i<256;++i) {
            if(i>='A' && i<='Z') {formatter_locale_codepage_006c02ec.class_bits[i+1]|=0x10;formatter_locale_codepage_006c02ec.case_map[i]=static_cast<std::uint8_t>(i+32);}
            else if(i>='a' && i<='z') {formatter_locale_codepage_006c02ec.class_bits[i+1]|=0x20;formatter_locale_codepage_006c02ec.case_map[i]=static_cast<std::uint8_t>(i-32);}
            else formatter_locale_codepage_006c02ec.case_map[i]=0;
        }
    }
}
int __cdecl formatter_locale_set_codepage_005a6895(int requested) {
    exit_registry_lock_api_005a4ba4(25);
    const auto cp=formatter_locale_resolve_codepage_005a6a42(requested);
    int result=0;
    if(cp!=formatter_locale_codepage_006c02ec.codepage) {
        if(!cp) {formatter_locale_reset_005a6abf();formatter_locale_build_tables_005a6ae8();}
        else {
            unsigned preset=0;
            while(preset<5 && data32(8+preset*48)!=cp)++preset;
            if(preset<5) {
                clear_classes();
                for(unsigned kind=0;kind<4;++kind) {
                    const auto* range=codepage_data+24+preset*48+kind*8;
                    while(range[0]) {
                        if(!range[1])break;
                        for(unsigned i=range[0];i<=range[1];++i)formatter_locale_codepage_006c02ec.class_bits[i+1]|=codepage_data[kind];
                        range+=2;
                    }
                }
                formatter_locale_codepage_006c02ec.multibyte=1;
                formatter_locale_codepage_006c02ec.codepage=cp;
                const auto lcid=formatter_locale_codepage_lcid_005a6a8c(cp);
                formatter_locale_codepage_006c02ec.ids[0]=data32(12+preset*48);
                formatter_locale_codepage_006c02ec.ids[1]=data32(16+preset*48);
                formatter_locale_codepage_006c02ec.locale=lcid;
                formatter_locale_codepage_006c02ec.ids[2]=data32(20+preset*48);
                formatter_locale_build_tables_005a6ae8();
            } else {
                FormatterLocaleCPInfo info;
                if(formatter_locale_codepage_info(cp,&info)==1) {
                    formatter_locale_codepage_006c02ec.locale=0;clear_classes();
                    formatter_locale_codepage_006c02ec.codepage=cp;
                    if(info.max_character_bytes>1) {
                        const auto* range=info.lead_ranges;
                        while(range[0]) {
                            if(!range[1])break;
                            for(unsigned i=range[0];i<=range[1];++i)formatter_locale_codepage_006c02ec.class_bits[i+1]|=4;
                            range+=2;
                        }
                        for(unsigned i=1;i<255;++i)formatter_locale_codepage_006c02ec.class_bits[i+1]|=8;
                        formatter_locale_codepage_006c02ec.locale=formatter_locale_codepage_lcid_005a6a8c(cp);
                        formatter_locale_codepage_006c02ec.multibyte=1;
                    } else formatter_locale_codepage_006c02ec.multibyte=0;
                    clear_ids();formatter_locale_build_tables_005a6ae8();
                } else if(formatter_locale_resolved_006afd68) {
                    formatter_locale_reset_005a6abf();formatter_locale_build_tables_005a6ae8();
                } else result=-1;
            }
        }
    }
    exit_registry_unlock_api_005a4c05(25);
    return result;
}
void __cdecl formatter_locale_initialize_005a6c6d() {
    if(!formatter_locale_initialized_006c152c) {
        formatter_locale_set_codepage_005a6895(-3);
        formatter_locale_initialized_006c152c=1;
    }
}
}

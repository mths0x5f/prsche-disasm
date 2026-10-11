#include "porsche/formatter_locale.hpp"
#include <windows.h>
#include <intrin.h>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>

namespace {
using U=std::uint32_t;
constexpr U B=0x29000000,kINPUT=B+0x1000,kOUTPUT=B+0x2000;
U id,fn,p[17],cp_calls;std::string events;const void* zeroed;
enum {kMM,kMT,kREQUEST,kFLAGS,kCOUNT,kCAPACITY,kCP,kLCID,kSTRICT,kVARIANT,kQUERY,kCONVERTED,kMAPPED,kENCODED,kMAX_INFO,kCURRENT,kONCE};
std::string hx(U x){char b[12];std::snprintf(b,sizeof(b),"%08x",x);return b;}
void event(const char* name,std::initializer_list<U> values) {
    events+=name;for(auto v:values)events+=':'+hx(v);events+=';';
}
int effective(const void* input,int count,unsigned unit) {
    if(count==-1) {
        for(int i=0;i<512;++i) {
            unsigned v=static_cast<const unsigned char*>(input)[i*unit];
            if(unit==2)v|=static_cast<const unsigned char*>(input)[i*unit+1]<<8;
            if(!v)return i+1;
        }
        return 512;
    }
    return count<0?0:count>512?512:count;
}
std::string bytes(const void* address,unsigned n) {
    std::string out;char b[4];for(unsigned i=0;i<n;++i){std::snprintf(b,sizeof(b),"%02x",static_cast<const unsigned char*>(address)[i]);out+=b;}return out;
}
void api(const char* name,std::initializer_list<U> values,const void* input,int count,unsigned unit) {
    event(name,values);events+="data:"+bytes(input,effective(input,count,unit)*unit)+';';
}
void mutate() {
    using namespace porsche;
    if(p[kVARIANT]&32768) {
        formatter_locale_default_codepage_006afd90=0x9876;formatter_text_locale_006afd80=0x7654;
        formatter_locale_codepage_006c02ec.codepage=0x5432;formatter_locale_codepage_006c02ec.locale=0x4321;
    }
}
void decode(U a,const std::string& s) {
    for(unsigned i=0;i<s.size();i+=2){unsigned v;if(sscanf_s(s.c_str()+i,"%2x",&v)!=1)std::exit(6);reinterpret_cast<unsigned char*>(a)[i/2]=static_cast<unsigned char>(v);}
}
}
void formatter_locale_stack_observer(U size,unsigned site) {
    const bool fail=(site==1 ? (p[kVARIANT]&8192) : (p[kVARIANT]&4096))!=0;
    event("stack",{size,site,fail?1u:0u});
    if(fail)RaiseException(0xe1440001,0,0,nullptr);
}
namespace porsche {
std::uint32_t formatter_text_locale_006afd80=0;
void* __cdecl formatter_crt_memset_005abe90(void* dest,int value,U count) {
    event("memset",{static_cast<U>(value),count,(p[kVARIANT]&16384)?1u:0u});
    if(p[kVARIANT]&16384)RaiseException(0xe1440002,0,0,nullptr);
    std::memset(dest,value,count);zeroed=dest;return dest;
}
void __cdecl exit_registry_lock_api_005a4ba4(U lock) {
    event("lock",{lock});
    if(p[kVARIANT]&65536)formatter_locale_codepage_006c02ec.codepage=p[kREQUEST];
}
void __cdecl exit_registry_unlock_api_005a4c05(U lock) {event("unlock",{lock});}
int __stdcall formatter_locale_map_w(U locale,U flags,const std::uint16_t* input,int count,void* output,int cap) {
    api("mapW",{locale,flags,static_cast<U>(count),output?1u:0u,static_cast<U>(cap)},input,count,2);
    const bool probe=count==1 && input[0]==0 && locale==0 && flags==0x100 && !output;
    if(probe){mutate();return p[kVARIANT]&1?0:1;}
    const int result=static_cast<int>(output?p[kENCODED]:p[kMAPPED]);
    if(output && cap>0) {
        const int n=cap<static_cast<int>(p[kMAPPED])?cap:static_cast<int>(p[kMAPPED]);
        if(flags&0x400)for(int i=0;i<n;++i)static_cast<unsigned char*>(output)[i]=static_cast<unsigned char>(0x91+i);
        else for(int i=0;i<n;++i)static_cast<std::uint16_t*>(output)[i]=static_cast<std::uint16_t>(0x5100+i);
    }
    mutate();return p[kVARIANT]&(output?32u:16u)?0:result;
}
int __stdcall formatter_locale_map_a(U locale,U flags,const char* input,int count,char* output,int cap) {
    api("mapA",{locale,flags,static_cast<U>(count),output?1u:0u,static_cast<U>(cap)},input,count,1);
    const bool probe=count==1 && input[0]==0 && locale==0 && flags==0x100 && !output;
    if(output && cap>0)for(int i=0;i<effective(input,count,1) && i<cap;++i)output[i]=static_cast<char>(static_cast<unsigned char>(input[i])+(flags==0x100?7:-7));
    mutate();return probe?(p[kVARIANT]&2?0:1):static_cast<int>(p[kENCODED]);
}
int __stdcall formatter_locale_to_wide(U cp,U flags,const char* input,int count,std::uint16_t* output,int cap) {
    api("toW",{cp,flags,static_cast<U>(count),output?1u:0u,static_cast<U>(cap)},input,count,1);
    if(output && output==zeroed){events+="prezero:"+bytes(output,cap*2)+';';zeroed=nullptr;}
    if(output && cap>0)for(int i=0;i<cap;++i)output[i]=static_cast<std::uint16_t>(0x4100+i);
    mutate();return p[kVARIANT]&(output?8u:4u)?0:static_cast<int>(output?p[kCONVERTED]:p[kQUERY]);
}
int __stdcall formatter_locale_from_wide(U cp,U flags,const std::uint16_t* input,int count,char* output,int cap,const char* fallback,int* used) {
    api("fromW",{cp,flags,static_cast<U>(count),output?1u:0u,static_cast<U>(cap),fallback?1u:0u,used?1u:0u},input,count,2);
    if(output && cap>0)for(int i=0;i<cap && i<static_cast<int>(p[kENCODED]);++i)output[i]=static_cast<char>(0x61+i);
    mutate();return p[kVARIANT]&64?0:static_cast<int>(p[kENCODED]);
}
int __stdcall formatter_locale_type_w(U type,const std::uint16_t* input,int count,std::uint16_t* output) {
    api("typeW",{type,static_cast<U>(count)},input,count,2);
    const bool probe=count==1 && input[0]==0;
    for(int i=0;i<effective(input,count,2);++i)output[i]=static_cast<std::uint16_t>(0x200+i%3+1);
    mutate();return p[kVARIANT]&(probe?128u:512u)?0:1;
}
int __stdcall formatter_locale_type_a(U locale,U type,const char* input,int count,std::uint16_t* output) {
    api("typeA",{locale,type,static_cast<U>(count)},input,count,1);
    const bool probe=count==1 && input[0]==0 && locale==0 && type==1;
    for(int i=0;i<effective(input,count,1);++i)output[i]=static_cast<std::uint16_t>(0x200+i%3+1);
    mutate();return p[kVARIANT]&(probe?256u:512u)?0:1;
}
U __stdcall formatter_locale_oem_codepage() {event("OEMCP",{932});if(p[kVARIANT]&32768)formatter_locale_resolved_006afd68=0;return 932;}
U __stdcall formatter_locale_ansi_codepage() {event("ACP",{1252});if(p[kVARIANT]&32768)formatter_locale_resolved_006afd68=0;return 1252;}
int __stdcall formatter_locale_codepage_info(U cp,FormatterLocaleCPInfo* info) {
    ++cp_calls;event("CPInfo",{cp,cp_calls});
    std::memset(info,0,sizeof(*info));info->max_character_bytes=p[kMAX_INFO];info->default_character[0]='?';
    const unsigned char ranges[]={0x81,0x82,0x90,0x8f,0xe0,0xe2,0,0,0,0,0,0};
    std::memcpy(info->lead_ranges,ranges,12);mutate();
    return p[kVARIANT]&(cp_calls==1?1024u:2048u)?0:1;
}
}
int main() {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x4000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    while(std::cin>>std::dec>>id>>fn) {
        for(auto& v:p)if(!(std::cin>>std::hex>>v))return 4;
        std::string text;if(!(std::cin>>text))return 5;
        using namespace porsche;
        for(U i=0;i<0x4000;++i)reinterpret_cast<unsigned char*>(B)[i]=static_cast<unsigned char>(i*13u+id*3u+0x21u);
        auto* state=reinterpret_cast<unsigned char*>(&formatter_locale_codepage_006c02ec);
        for(U i=0;i<sizeof(formatter_locale_codepage_006c02ec);++i)state[i]=static_cast<unsigned char>(i*31u+id*9u+0x63u);
        formatter_locale_codepage_006c02ec.codepage=p[kCURRENT];
        formatter_locale_resolved_006afd68=0x55;formatter_locale_default_codepage_006afd90=1252;
        formatter_locale_map_mode_006afd98=p[kMM];formatter_locale_type_mode_006afec4=p[kMT];
        formatter_locale_initialized_006c152c=p[kONCE];formatter_text_locale_006afd80=0x409;
        const U input=p[kVARIANT]&0x100000?kOUTPUT:kINPUT;
        decode(input,text);events.clear();cp_calls=0;zeroed=nullptr;U result=0;
        const auto seh_before=__readfsdword(0);
        switch(fn) {
        case 0:result=formatter_text_map_005a7e05(p[kLCID],p[kFLAGS],reinterpret_cast<const char*>(input),p[kCOUNT],reinterpret_cast<char*>(kOUTPUT),p[kCAPACITY],p[kCP],p[kSTRICT]);break;
        case 1:result=formatter_text_type_005a98c2(p[kFLAGS],reinterpret_cast<const char*>(input),p[kCOUNT],reinterpret_cast<std::uint16_t*>(kOUTPUT),p[kCP],p[kLCID],p[kSTRICT]);break;
        case 2:result=formatter_locale_bounded_length_005ad2bf(reinterpret_cast<const char*>(input),p[kCOUNT]);break;
        case 3:result=formatter_locale_set_codepage_005a6895(p[kREQUEST]);break;
        case 4:result=formatter_locale_resolve_codepage_005a6a42(p[kREQUEST]);break;
        case 5:result=formatter_locale_codepage_lcid_005a6a8c(p[kREQUEST]);break;
        case 6:formatter_locale_reset_005a6abf();break;
        case 7:formatter_locale_build_tables_005a6ae8();break;
        default:formatter_locale_initialize_005a6c6d();break;
        }
        if(__readfsdword(0)!=seh_before)return 7;
        std::printf("{\"case\":%u,\"result\":\"%08x\",\"events\":\"%s\",\"resolved\":\"%08x\",\"default_cp\":\"%08x\",\"map_mode\":\"%08x\",\"type_mode\":\"%08x\",\"initialized\":\"%08x\",\"locale\":\"%08x\",\"state\":\"%s\",\"memory\":\"",
            id,result,events.c_str(),formatter_locale_resolved_006afd68,formatter_locale_default_codepage_006afd90,
            formatter_locale_map_mode_006afd98,formatter_locale_type_mode_006afec4,formatter_locale_initialized_006c152c,
            formatter_text_locale_006afd80,bytes(state,sizeof(formatter_locale_codepage_006c02ec)).c_str());
        for(U i=0;i<0x4000;++i)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[i]);std::puts("\"}");
    }
}

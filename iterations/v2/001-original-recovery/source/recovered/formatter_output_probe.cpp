#include "porsche/formatter_output.hpp"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>

namespace {
using U=std::uint32_t;
constexpr U B=0x29000000,kINPUT=B+0x4000,kOUTPUT=B+0x5000,kDESC=B+0x7000,kHEAP=B+0x8000;
U seq,fn,p[16],writes;std::string events;
enum {kID,kFLAGS,kLENGTH,kVARIANT,kSEEK,kERROR,kCAP,kFAILCALL,kLOCALE,kWIDTH,kCP,kVALUE,kWRITER,kREADERS,kALLOCS,kORIGIN};
std::string hx(U x) {char buf[12];std::snprintf(buf,sizeof(buf),"%08x",x);return buf;}
std::string hex(const void* data,U n) {std::string out;char b[4];for(U i=0;i<n;++i){std::snprintf(b,sizeof(b),"%02x",static_cast<const unsigned char*>(data)[i]);out+=b;}return out;}
void event(const char* name,std::initializer_list<U> values={}) {events+=name;for(auto v:values)events+=':'+hx(v);events+=';';}
void put(U address,U value) {*reinterpret_cast<U*>(address)=value;}
U get(U address) {return *reinterpret_cast<U*>(address);}
void swap_bank() {porsche::formatter_cleanup_handle_table_006c01e0[(p[kID]&63u)>>5]=reinterpret_cast<const std::uint8_t*>(B+0x3000);}
std::int32_t __stdcall decrement_b(std::int32_t*);
std::int32_t __stdcall decrement_a(std::int32_t* value) {
    event("decA",{static_cast<U>(*value)});return static_cast<std::int32_t>(--*reinterpret_cast<U*>(value));
}
std::int32_t __stdcall decrement_b(std::int32_t* value) {
    event("decB",{static_cast<U>(*value)});return static_cast<std::int32_t>(--*reinterpret_cast<U*>(value));
}
std::int32_t __stdcall increment(std::int32_t* value) {
    event("inc",{static_cast<U>(*value)});
    if(p[kVARIANT]&256)porsche::formatter_text_decrement_005b2254=decrement_b;
    if(p[kVARIANT]&1024)porsche::formatter_text_locale_writer_006c02e4^=1;
    return static_cast<std::int32_t>(++*reinterpret_cast<U*>(value));
}
}
namespace porsche {
// Unused005a4259 link-fixture cells; this probe only calls canonical005abf35.
FormatterOriginalDescriptor32* formatter_cleanup_stream_005e5508=nullptr;
FormatterOriginalDescriptor32* formatter_cleanup_stream_005e5528=nullptr;
const std::uint8_t* formatter_cleanup_invalid_handle_record_005e5f50=nullptr;
const std::uint8_t* formatter_cleanup_preceding_handle_bank_006c01dc=nullptr;
const std::uint8_t* formatter_cleanup_handle_table_006c01e0[64]{};
std::uint32_t formatter_cleanup_handle_limit_006c02e0;
std::uint32_t formatter_text_locale_006afd80,formatter_text_locale_writer_006c02e4;
std::int32_t formatter_text_locale_readers_006c02e8;
FormatterTextAtomic formatter_text_increment_005b2258=increment,formatter_text_decrement_005b2254=decrement_a;
std::uint32_t formatter_locale_default_codepage_006afd90;
std::int32_t formatter_float_character_width_005e54dc;
std::int32_t* __cdecl formatter_lowio_errno_005a669e() {event("errno");return reinterpret_cast<std::int32_t*>(B+0x100);}
std::uint32_t* __cdecl formatter_lowio_doserrno_005a66a7() {event("doserrno");if(p[kVARIANT]&16384)put(B+0x100,0x55667788);return reinterpret_cast<U*>(B+0x104);}
void __cdecl formatter_lowio_lock_005ab726(U id) {event("lockfile",{id});if(p[kVARIANT]&32)swap_bank();}
void __cdecl formatter_lowio_unlock_005ab785(U id) {event("unlockfile",{id});}
U __cdecl formatter_lowio_handle_005ab6e4(U id) {
    event("handle",{id});if(p[kVARIANT]&2048)return 0xffffffffu;
    return get(reinterpret_cast<U>(formatter_cleanup_handle_table_006c01e0[id>>5])+(id&31u)*36u);
}
void* __cdecl exit_registry_malloc_005a3be5(U size) {event("malloc",{size,formatter_output_allocations_006afcf8});if(p[kVARIANT]&1)return nullptr;return reinterpret_cast<void*>(kHEAP);}
void __cdecl exit_registry_lock_api_005a4ba4(U id) {event("lockcrt",{id});}
void __cdecl exit_registry_unlock_api_005a4c05(U id) {event("unlockcrt",{id});}
U __stdcall formatter_output_set_file_pointer(U handle,std::int32_t distance,std::int32_t* high,U origin) {
    event("seek",{handle,static_cast<U>(distance),high?1u:0u,origin});if(p[kVARIANT]&128)swap_bank();return p[kSEEK];
}
U __stdcall formatter_crt_get_last_error() {event("error",{p[kERROR]});return p[kERROR];}
int __stdcall formatter_error_write_file(void* handle,const void* data,U n,U* written,void* overlapped) {
    ++writes;const U amount=(p[kVARIANT]&32768)?p[kCAP]:(n<p[kCAP]?n:p[kCAP]);*written=amount;
    const bool fail=(p[kVARIANT]&4) && writes==p[kFAILCALL];
    event("write",{reinterpret_cast<U>(handle),n,overlapped?1u:0u,amount,fail?0u:1u});events+="data:"+hex(data,n)+';';
    if(p[kVARIANT]&64)swap_bank();return fail?0:1;
}
int __stdcall formatter_locale_from_wide(U cp,U flags,const std::uint16_t* input,int n,char* output,int cap,const char* fallback,int* used) {
    event("wide",{cp,flags,*input,static_cast<U>(n),static_cast<U>(cap),fallback?1u:0u,used?1u:0u});
    if(output && cap>0)for(int i=0;i<cap && i<4;++i)output[i]=static_cast<char>(0x91+i);
    *used=(p[kVARIANT]&8)?1:0;
    if(p[kVARIANT]&512)formatter_text_decrement_005b2254=decrement_b;
    return (p[kVARIANT]&16)?0:static_cast<int>(p[kCAP]);
}
}
int main() {
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    while(std::cin>>std::dec>>seq>>fn) {
        for(auto& v:p)if(!(std::cin>>std::hex>>v))return 4;
        using namespace porsche;
        for(U i=0;i<0x10000;++i)reinterpret_cast<unsigned char*>(B)[i]=static_cast<unsigned char>(i*13u+seq*7u+0x21u);
        for(U bank=0;bank<3;++bank)for(U i=0;i<32;++i) {
            const U a=B+0x1000+bank*0x1000+i*36;put(a,0x7000+bank*0x100+i);*reinterpret_cast<unsigned char*>(a+4)=static_cast<unsigned char>(p[kFLAGS]^(bank==2?0xc0u:0u));
        }
        for(U i=0;i<4096;++i)reinterpret_cast<unsigned char*>(kINPUT)[i]=(p[kVARIANT]&8192)?0x1a:(p[kVARIANT]&4096)?10:(i%11==3?10:static_cast<unsigned char>('A'+i%26));
        for(auto& bank:formatter_cleanup_handle_table_006c01e0)bank=nullptr;
        formatter_cleanup_handle_table_006c01e0[0]=reinterpret_cast<const std::uint8_t*>(B+0x1000);formatter_cleanup_handle_table_006c01e0[1]=reinterpret_cast<const std::uint8_t*>(B+0x2000);
        formatter_cleanup_handle_limit_006c02e0=64;formatter_text_locale_006afd80=p[kLOCALE];formatter_text_locale_writer_006c02e4=p[kWRITER];formatter_text_locale_readers_006c02e8=static_cast<int>(p[kREADERS]);
        formatter_locale_default_codepage_006afd90=p[kCP];formatter_float_character_width_005e54dc=static_cast<int>(p[kWIDTH]);formatter_output_allocations_006afcf8=p[kALLOCS];formatter_text_decrement_005b2254=decrement_a;
        put(B+0x100,0x11111111);put(B+0x104,0x22222222);events.clear();writes=0;U result;
        const U dest=(p[kVARIANT]&2)?0:kOUTPUT;
        switch(fn) {
        case 0:result=formatter_wide_encode_boundary_005abf5e(reinterpret_cast<char*>(dest),p[kVALUE]);break;
        case 1:result=formatter_output_wide_inner_005abfb7(reinterpret_cast<char*>(dest),p[kVALUE]);break;
        case 2:result=formatter_cleanup_file_write_005a9e49(p[kID],reinterpret_cast<const void*>(kINPUT),static_cast<int>(p[kLENGTH]));break;
        case 3:result=formatter_output_write_inner_005a9eae(p[kID],reinterpret_cast<const void*>(kINPUT),static_cast<int>(p[kLENGTH]));break;
        case 4:result=formatter_cleanup_file_aux_005a9ab8(p[kID],p[kVALUE],p[kORIGIN]);break;
        case 5:result=formatter_output_seek_inner_005a9b1d(p[kID],p[kVALUE],p[kORIGIN]);break;
        case 6:result=formatter_cleanup_prepare_descriptor_005abef1(reinterpret_cast<FormatterOriginalDescriptor32*>(kDESC));break;
        case 7:result=cleanup_is_character_device_005abf35(p[kID]);break;
        default:result=reinterpret_cast<U>(formatter_output_map_error_005a662b(p[kERROR]));break;
        }
        std::printf("{\"case\":%u,\"result\":\"%08x\",\"events\":\"%s\",\"allocs\":\"%08x\",\"readers\":\"%08x\",\"writer\":\"%08x\",\"decrement\":%u,\"banks\":[\"%08x\",\"%08x\"],\"memory\":\"%s\"}\n",
            seq,result,events.c_str(),formatter_output_allocations_006afcf8,static_cast<U>(formatter_text_locale_readers_006c02e8),formatter_text_locale_writer_006c02e4,
            formatter_text_decrement_005b2254==decrement_b?1:0,reinterpret_cast<U>(formatter_cleanup_handle_table_006c01e0[0]),reinterpret_cast<U>(formatter_cleanup_handle_table_006c01e0[1]),hex(reinterpret_cast<void*>(B),0x10000).c_str());
    }
}

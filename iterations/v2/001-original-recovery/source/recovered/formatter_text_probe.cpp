#include "porsche/formatter_text.hpp"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {
using U = std::uint32_t;
constexpr U B=0x28000000, FIRST=B+0x400, SECOND=B+0x800, TABLE=B+0x1400, ALT=B+0x2400;
U id,fn,c,mask,locale,writer,variant,n; int width;
std::string events,reads; std::vector<unsigned char> original_table;
void append(const char* format,U a,U b=0,U d=0,U e=0) {
    char line[160]; std::snprintf(line,sizeof(line),format,a,b,d,e); events+=line;
}
void decode(U address,const char* s) {
    while(*s) { unsigned value; if(sscanf_s(s,"%2x",&value)!=1)std::exit(6);
        *reinterpret_cast<unsigned char*>(address++)=static_cast<unsigned char>(value); s+=2; }
}
void mutation() {
    using namespace porsche;
    if(variant&64) {
        formatter_text_locale_006afd80=0x4321;
        formatter_text_locale_writer_006c02e4^=1;
        formatter_float_character_width_005e54dc=2;
        formatter_ctype_table_005e52d0=reinterpret_cast<const unsigned char*>(ALT);
    }
}
std::int32_t __stdcall alternate_decrement(std::int32_t* p) {
    *p=static_cast<std::int32_t>(static_cast<U>(*p)-1u); append("alternate:%08x;",static_cast<U>(*p)); return *p;
}
void input_event(const char* name,U a,U b,const char* input,int count,U capacity,U cp,U strict) {
    char line[200]; std::snprintf(line,sizeof(line),"%s:%08x:%08x:%08x:",name,a,b,count); events+=line;
    for(int i=0;i<=count;++i) { std::snprintf(line,sizeof(line),"%02x",static_cast<unsigned char>(input[i])); events+=line; }
    std::snprintf(line,sizeof(line),":%08x:%08x:%08x;",capacity,cp,strict); events+=line;
}
}
void formatter_text_read_trace(const void* p,unsigned size,U value) {
    const U address=reinterpret_cast<U>(p);
    if(address>=B && address<B+0x3000) {
        char line[80]; std::snprintf(line,sizeof(line),"r:%08x:%u:%08x;",address,size,value); reads+=line;
    }
}
namespace porsche {
std::int32_t formatter_float_character_width_005e54dc=1;
const std::uint8_t* formatter_ctype_table_005e52d0=nullptr;
std::int32_t __stdcall formatter_text_platform_increment(std::int32_t* p) {
    *p=static_cast<std::int32_t>(static_cast<U>(*p)+1u); append("increment:%08x;",static_cast<U>(*p));
    if(variant&8)formatter_text_locale_writer_006c02e4^=1;
    if(variant&16)formatter_text_locale_006afd80=0;
    return *p;
}
std::int32_t __stdcall formatter_text_platform_decrement(std::int32_t* p) {
    *p=static_cast<std::int32_t>(static_cast<U>(*p)-1u); append("decrement:%08x;",static_cast<U>(*p));
    if(variant&32)formatter_text_decrement_005b2254=alternate_decrement;
    return *p;
}
void __cdecl exit_registry_lock_api_005a4ba4(U lock) {
    append("lock:%08x;",lock);
    if(variant&128)formatter_text_locale_006afd80=0;
}
void __cdecl exit_registry_unlock_api_005a4c05(U lock) {append("unlock:%08x;",lock);}
int __cdecl formatter_text_map_005a7e05(U l,U flags,const char* input,int count,
    char* output,int capacity,U cp,int strict) {
    input_event("map",l,flags,input,count,capacity,cp,strict);
    output[0]=static_cast<char>(0xa1); output[1]=static_cast<char>(0xb2); output[2]=0;
    mutation();
    if(variant&64)formatter_text_decrement_005b2254=alternate_decrement;
    return variant&4 ? -1 : static_cast<int>(variant&3);
}
int __cdecl formatter_text_type_005a98c2(U type,const char* input,int count,
    std::uint16_t* output,U cp,U l,int strict) {
    input_event("type",type,l,input,count,2,cp,strict);
    *output=0x8765; mutation(); return variant&512 ? 0 : 1;
}
}
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    if(!VirtualAlloc(reinterpret_cast<void*>(B),0x3000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE))return 3;
    FILE* file=nullptr; if(fopen_s(&file,argv[1],"rb") || !file)return 4;
    std::fseek(file,0,SEEK_END);std::vector<unsigned char> exe(std::ftell(file));std::rewind(file);
    if(std::fread(exe.data(),1,exe.size(),file)!=exe.size())return 5;std::fclose(file);
    auto word=[&](U p){U v;std::memcpy(&v,exe.data()+p,4);return v;};
    const U pe=word(0x3c), count=exe[pe+6]|(exe[pe+7]<<8), optional=exe[pe+20]|(exe[pe+21]<<8);
    for(U i=0;i<count;++i){const U section=pe+24+optional+i*40,rva=word(section+12),size=word(section+16);
        if(rva<=0x1e52d8 && 0x1e52d8+514<=rva+size) {
            const U offset=word(section+20)+0x1e52d8-rva;
            original_table.assign(exe.begin()+offset,exe.begin()+offset+514);
        }
    }
    if(original_table.size()!=514)return 7;
    char left[2049],right[2049];
    while(scanf_s("%u %u %x %x %x %d %x %u %x %2048s %2048s",&id,&fn,&c,&mask,&locale,&width,&writer,&variant,&n,left,static_cast<unsigned>(sizeof(left)),right,static_cast<unsigned>(sizeof(right)))==11) {
        using namespace porsche;
        for(U i=0;i<0x3000;++i)reinterpret_cast<unsigned char*>(B)[i]=static_cast<unsigned char>(i*23u+id*7u+0x35u);
        std::memcpy(reinterpret_cast<void*>(TABLE-2),original_table.data(),514);
        std::memcpy(reinterpret_cast<void*>(ALT-2),original_table.data(),514);
        if(variant&256)for(U v:{1u,0x81u,0xffu})reinterpret_cast<unsigned char*>(TABLE)[v*2+1]|=0x80;
        const U first=FIRST+(id&3),second=variant&2048 ? first : variant&4096 ? first+1 : SECOND+((id>>2)&3);
        decode(first,left);decode(second,right);
        formatter_ctype_table_005e52d0=reinterpret_cast<const unsigned char*>(TABLE);
        formatter_float_character_width_005e54dc=width;
        formatter_text_locale_006afd80=locale;formatter_text_locale_writer_006c02e4=writer;
        formatter_text_locale_readers_006c02e8=static_cast<int>(variant&8192 ? 0x7fffffffu : variant&16384 ? 0xffffffffu : id*3u-17u);
        formatter_text_increment_005b2258=formatter_text_platform_increment;
        formatter_text_decrement_005b2254=formatter_text_platform_decrement;
        events.clear();reads.clear();U result;
        switch(fn) {
        case 0:result=formatter_float_lower_005a2248(c);break;
        case 1:result=formatter_text_lower_inner_005a22b7(c);break;
        case 2:result=formatter_text_upper_005a262c(c);break;
        case 3:result=formatter_text_upper_inner_005a269b(c);break;
        case 4:result=formatter_float_classify_005a2eae(c,mask);break;
        case 5:result=formatter_text_alpha_005a2c24(c);break;
        case 6:result=formatter_text_digit_005a2c52(c);break;
        case 7:result=formatter_text_space_005a2c7a(c);break;
        case 8:result=formatter_text_compare_n_005a2210(reinterpret_cast<const char*>(first),reinterpret_cast<const char*>(second),n);break;
        case 9:result=formatter_text_reject_span_005a2e70(reinterpret_cast<const char*>(first),reinterpret_cast<const char*>(second));break;
        default:result=reinterpret_cast<U>(formatter_text_find_last_005a2870(reinterpret_cast<const char*>(first),c));break;
        }
        std::printf("{\"case\":%u,\"result\":\"%08x\",\"events\":\"%s\",\"reads\":\"%s\",\"locale\":\"%08x\",\"writer\":\"%08x\",\"readers\":\"%08x\",\"width\":%d,\"table\":\"%08x\",\"decrement_changed\":%s,\"df\":%u,\"memory\":\"",
            id,result,events.c_str(),reads.c_str(),formatter_text_locale_006afd80,formatter_text_locale_writer_006c02e4,
            static_cast<U>(formatter_text_locale_readers_006c02e8),formatter_float_character_width_005e54dc,
            reinterpret_cast<U>(formatter_ctype_table_005e52d0),formatter_text_decrement_005b2254==alternate_decrement?"true":"false",(__readeflags()>>10)&1);
        for(U i=0;i<0x3000;++i)std::printf("%02x",reinterpret_cast<unsigned char*>(B)[i]);
        std::puts("\"}");
    }
}

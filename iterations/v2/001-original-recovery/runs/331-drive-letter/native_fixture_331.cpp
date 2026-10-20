#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "../327-resource-open-callback-evidence/resource_device_327.hpp"
using U=std::uint32_t;
static_assert(sizeof(void*)==4,"x86");
static const unsigned char original_bytes[111]={@BODY@};
static U length_value,letter,colon,upper_letter,upper_colon,search_hit,mutate_input,search_null;
static U calls,errors; static char* buffer_seen; static char* incoming; static char snapshot[261];
static U events[8];
static void record(U v) {if(calls>=8)ExitProcess(98);events[calls++]=v;}
namespace porsche {
std::uint32_t formatter_text_locale_006afd80=0;
std::uint32_t formatter_text_locale_writer_006c02e4=0;
std::int32_t formatter_text_locale_readers_006c02e8=0;
void __cdecl exit_registry_lock_api_005a4ba4(std::uint32_t) {ExitProcess(96);}
void __cdecl exit_registry_unlock_api_005a4c05(std::uint32_t) {ExitProcess(96);}
std::int32_t __cdecl formatter_text_lower_inner_005a22b7(std::int32_t) {ExitProcess(96);}
const char* __cdecl fixture_canonical_search_005a2780(const char*,int);
const char* __cdecl formatter_search_character_005a2780(const char* path,int c) {
    record(1);if(path!=incoming||c!=0x7c)++errors;
    if(search_null)return search_hit?reinterpret_cast<const char*>(0x1234):nullptr;
    return fixture_canonical_search_005a2780(path,c);
}
}
extern "C" DWORD WINAPI hook_full(LPCSTR path,DWORD size,LPSTR buffer,LPSTR* part) {
    record(2);
    if(size!=261||!buffer||!part||*part!=nullptr||
       reinterpret_cast<U>(part)>=reinterpret_cast<U>(buffer)&&reinterpret_cast<U>(part)<reinterpret_cast<U>(buffer)+261)++errors;
    if(incoming) {if(path!=incoming)++errors;}
    else if(std::strcmp(path,".")!=0)++errors;
    if(mutate_input&&incoming)incoming[0]='m';
    buffer_seen=buffer;
    for(U i=0;i<261;++i)buffer[i]=static_cast<char>((i*7+13)&255);
    buffer[0]=static_cast<char>(letter);buffer[1]=static_cast<char>(colon);buffer[260]=0;
    std::memcpy(snapshot,buffer,261);*part=buffer+259;
    return length_value;
}
extern "C" LPSTR WINAPI hook_upper(LPSTR buffer) {
    record(3);if(buffer!=buffer_seen||std::memcmp(buffer,snapshot,261)!=0)++errors;
    if(mutate_input&&incoming&&incoming[0]!='m')++errors;
    buffer[0]=static_cast<char>(upper_letter);buffer[1]=static_cast<char>(upper_colon);
    buffer[259]='Z';return reinterpret_cast<LPSTR>(0x5a5a1234);
}
extern "C" {
DWORD (WINAPI* full_path_slot)(LPCSTR,DWORD,LPSTR,LPSTR*)=hook_full;
LPSTR (WINAPI* upper_slot)(LPSTR)=hook_upper;
}
#pragma comment(linker,"/alternatename:__imp__fixture_GetFullPathNameA@16=_full_path_slot")
#pragma comment(linker,"/alternatename:__imp__fixture_CharUpperA@4=_upper_slot")
struct Result { U esp0,esp1,ebp0,ebp1,ebx0,ebx1,esi0,esi1,edi0,edi1,eax,n,err; U trace[8];char input[96]; };
static Result invoke(const void* fn,char* path) {
    Result r{}; calls=errors=0;buffer_seen=nullptr;incoming=path;
    __asm {
        lea eax,r
        mov [eax],esp
        mov [eax+8],ebp
        mov ebx,13579bdfh
        mov esi,2468ace0h
        mov edi,6a31c5e7h
        mov [eax+16],ebx
        mov [eax+24],esi
        mov [eax+32],edi
        push path
        mov ecx,fn
        call ecx
        add esp,4
        lea edx,r
        mov [edx+40],eax
        mov [edx+4],esp
        mov [edx+12],ebp
        mov [edx+20],ebx
        mov [edx+28],esi
        mov [edx+36],edi
    }
    r.n=calls;r.err=errors;for(U i=0;i<calls;++i)r.trace[i]=events[i];
    if(path)std::memcpy(r.input,path-16,96);
    return r;
}
static bool abi(const Result&r) {return r.esp0==r.esp1&&r.ebp0==r.ebp1&&r.ebx0==r.ebx1&&r.esi0==r.esi1&&r.edi0==r.edi1;}
static bool same(const Result&a,const Result&b,U expected,U n) {
    return abi(a)&&abi(b)&&!a.err&&!b.err&&(a.eax&255)==expected&&(b.eax&255)==expected&&a.n==n&&b.n==n&&
           std::memcmp(a.trace,b.trace,n*4)==0&&std::memcmp(a.input,b.input,96)==0;
}
int main() {
    auto* body=static_cast<unsigned char*>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
    if(!body)return 90;std::memcpy(body,original_bytes,111);
    if(body[17]!=0xe8||body[58]!=0xff||body[71]!=0xff)return 91;
    *reinterpret_cast<U*>(body+18)=reinterpret_cast<U>(&porsche::formatter_search_character_005a2780)-reinterpret_cast<U>(body+22);
    static const char dot[]=".";*reinterpret_cast<U*>(body+38)=reinterpret_cast<U>(dot);
    *reinterpret_cast<U*>(body+60)=reinterpret_cast<U>(&full_path_slot);
    *reinterpret_cast<U*>(body+73)=reinterpret_cast<U>(&upper_slot);
    DWORD old=0;if(!VirtualProtect(body,4096,PAGE_EXECUTE_READ,&old)||!FlushInstructionCache(GetCurrentProcess(),body,111))return 92;
    const U lengths[]={0,1,2,260,261,262,0x7fffffffu,0x80000000u,0xffffffffu};
    const U letters[]={0,1,'a','z',0x80,0xff};
    const char* paths[]={"file","C:\\a","a|b","|","","x\\a"};
    __declspec(align(16)) char arena[128]; U passed=0;
    for(U mode=0;mode<8;++mode)for(U len:lengths)for(U c:letters)for(U form=0;form<4;++form)for(U align=0;align<4;++align) {
        length_value=len;letter=c;colon=(form&1)?':':'x';upper_letter=(c+17)&255;upper_colon=(form&2)?':':'y';
        search_null=mode>=6;search_hit=mode==7;mutate_input=mode&1;
        std::memset(arena,0xa7,sizeof(arena));char* path=mode>=6?nullptr:arena+32+align;
        if(path)std::strcpy(path,paths[mode]);char backup[128];std::memcpy(backup,arena,128);
        bool hit=search_null?search_hit:(std::strchr(path,'|')!=nullptr);
        U expected=(!hit&&static_cast<std::int32_t>(len)>1&&upper_colon==':')?upper_letter:0;
        Result a=invoke(body,path);std::memcpy(arena,backup,128);
        Result b=invoke(reinterpret_cast<const void*>(&porsche::resource_drive_letter_005916a0),path);
        if(!same(a,b,expected,hit?1:3)) {std::printf("divergence mode=%u len=%08x c=%u form=%u align=%u al=%u/%u expected=%u errors=%u/%u calls=%u/%u\n",mode,len,c,form,align,a.eax&255,b.eax&255,expected,a.err,b.err,a.n,b.n);return 10;}
        ++passed;
    }
    std::printf("cases=%u failures=0 AL_ESP_nonvolatile=PASS API_order_mutable_buffers_input_guards=PASS\n",passed);
    return passed==6912?0:93;
}

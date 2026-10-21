#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "search_bindings_338.hpp"
using U=std::uint32_t;
static_assert(sizeof(void*)==4,"x86");
static U payload,expected_kind,expected_left,expected_right,call_count,errors,mutate;
static char arena[64];
static void observe(U kind,const char* left,const char* right) {
    ++call_count;
    if(kind!=expected_kind||reinterpret_cast<U>(left)!=expected_left||reinterpret_cast<U>(right)!=expected_right)++errors;
    if(mutate) {const_cast<char*>(left)[0]=0x12;const_cast<char*>(right)[0]=0x34;}
}
namespace porsche {
std::int32_t __cdecl formatter_search_compare_005ae3c0(const char* left,const char* right) {
    observe(1,left,right);std::int32_t result;std::memcpy(&result,&payload,4);return result;
}
const char* __cdecl formatter_search_substring_005a1e10(const char* left,const char* right) {
    observe(2,left,right);return reinterpret_cast<const char*>(payload);
}
}
struct Result {U esp0,esp1,ebp0,ebp1,ebx0,ebx1,esi0,esi1,edi0,edi1,eax;};
static Result invoke(const void* fn,U left,U right) {
    Result r{};
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
        push right
        push left
        mov ecx,fn
        call ecx
        add esp,8
        lea edx,r
        mov [edx+40],eax
        mov [edx+4],esp
        mov [edx+12],ebp
        mov [edx+20],ebx
        mov [edx+28],esi
        mov [edx+36],edi
    }
    return r;
}
static bool check(U kind,U left,U right,U value,U memory_mode) {
    expected_kind=kind;expected_left=left;expected_right=right;payload=value;
    mutate=memory_mode;errors=call_count=0;
    std::memset(arena,0xa7,64);
    const void* fn=kind==1?reinterpret_cast<const void*>(&porsche::compare_005ae3c0):
                            reinterpret_cast<const void*>(&porsche::render_settings_read_config_005a1e10);
    Result r=invoke(fn,left,right);
    bool memory_ok=true;
    for(U i=0;i<64;++i) {
        U expected=0xa7;
        if(memory_mode&&reinterpret_cast<U>(arena+i)==left)expected=0x12;
        if(memory_mode&&reinterpret_cast<U>(arena+i)==right)expected=0x34;
        if(static_cast<unsigned char>(arena[i])!=expected)memory_ok=false;
    }
    const bool pass=r.esp0==r.esp1&&r.ebp0==r.ebp1&&r.ebx0==r.ebx1&&r.esi0==r.esi1&&r.edi0==r.edi1&&
                    r.eax==value&&errors==0&&call_count==1&&memory_ok;
    if(!pass)std::printf("divergence kind=%u left=%08x right=%08x value=%08x got=%08x calls=%u errors=%u memory=%u\n",kind,left,right,value,r.eax,call_count,errors,memory_ok);
    return pass;
}
int main() {
    const U pointers[]={0,1,0x7fffffffu,0x80000000u,0xffffffffu,0x12345678u,0xfedcba98u};
    const U returns[]={0,1,0x7fffffffu,0x80000000u,0xffffffffu,0x01020304u,0xdeadbeefu,0x100};
    U passed=0;
    for(U kind=1;kind<=2;++kind)for(U left:pointers)for(U right:pointers)for(U value:returns) {
        if(!check(kind,left,right,value,0))return 10;++passed;
    }
    for(U kind=1;kind<=2;++kind)for(U same=0;same<2;++same)for(U value:returns) {
        if(!check(kind,reinterpret_cast<U>(arena+16),reinterpret_cast<U>(arena+(same?16:32)),value,1))return 10;++passed;
    }
    std::printf("cases=%u failures=0 full_EAX_ESP_nonvolatile_arguments_one_call_mutations_guards=PASS bridge_O2=PASS\n",passed);
    return passed==816?0:93;
}

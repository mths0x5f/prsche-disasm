#include "porsche/formatter_stdio.hpp"
#include "porsche/formatter_entry.hpp"
#include <Windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

namespace {
using U=std::uint32_t;
constexpr U BASE=0x24000000,IOB=0x25000000;
auto* arena=reinterpret_cast<unsigned char*>(BASE);
U seq,op,selector,index_value,flags_value,delta,remaining,size_value,character_result,malloc_mode,write_mode,variant,counter,temporary;
std::string events;
U addr(const void* p) {return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U get(const void* p) {U v;std::memcpy(&v,p,4);return v;}
void put(void* p,U v) {std::memcpy(p,&v,4);}
U loc(U p) {const U first=addr(porsche::formatter_iob_entries_005e54e8);if(p>=first-32 && p<first+672)return IOB+p-first;return p;}
std::string hx(U v) {char text[12];std::snprintf(text,sizeof(text),"%08x",v);return text;}
std::string hex(const void* data,unsigned n) {const auto* p=static_cast<const unsigned char*>(data);const char* digits="0123456789abcdef";std::string out;for(unsigned i=0;i<n;++i){out+=digits[p[i]>>4];out+=digits[p[i]&15];}return out;}
std::string normalized(const void* data,unsigned n) {std::vector<unsigned char> copy(static_cast<const unsigned char*>(data),static_cast<const unsigned char*>(data)+n);for(unsigned i=0;i+4<=n;i+=4)put(copy.data()+i,loc(get(copy.data()+i)));return hex(copy.data(),n);}
std::string state() {return normalized(porsche::formatter_iob_entries_005e54e8,96)+':'+normalized(arena+0x100,32)+':'+hx(porsche::formatter_output_allocations_006afcf8)+':'+hx(loc(addr(porsche::formatter_stdio_buffers_006afd60[0])))+':'+hx(loc(addr(porsche::formatter_stdio_buffers_006afd60[1])));}
porsche::FormatterOriginalDescriptor32* active() {using namespace porsche;if(op==0)return &formatter_iob_entries_005e54e8[1];if(selector==0)return &formatter_iob_entries_005e54e8[1];if(selector==1)return &formatter_iob_entries_005e54e8[2];if(selector==2)return reinterpret_cast<FormatterOriginalDescriptor32*>(arena+0x100);const U offsets[]={0,608,609,0xffffffffu,1,607};return reinterpret_cast<FormatterOriginalDescriptor32*>(addr(formatter_iob_entries_005e54e8)+offsets[(selector-3)%6]);}
void mutate(unsigned bit) {if(!(variant&bit))return;auto* d=active();if(selector>2 && op!=0)return;auto* raw=reinterpret_cast<unsigned char*>(d);put(raw+12,0xa5000082);put(raw+8,BASE+0x1100);put(raw,BASE+0x1120);put(raw+4,0x87654321);porsche::formatter_stdio_buffers_006afd60[0]=arena+0x3000;++porsche::formatter_output_allocations_006afcf8;}
}
namespace porsche {
U formatter_output_allocations_006afcf8=0;
void __cdecl exit_registry_lock_api_005a4ba4(U id) {events+="L:"+hx(id)+':'+state()+';';mutate(32);}
void __cdecl exit_registry_unlock_api_005a4c05(U id) {events+="U:"+hx(id)+':'+state()+';';}
void __stdcall formatter_lowio_critical_enter(void* p) {events+="E:"+hx(loc(addr(p)))+':'+state()+';';mutate(32);}
void __stdcall formatter_lowio_critical_leave(void* p) {events+="V:"+hx(loc(addr(p)))+':'+state()+';';}
U __cdecl cleanup_is_character_device_005abf35(U file) {events+="C:"+hx(file)+':'+hx(character_result)+':'+state()+';';mutate(1);return character_result;}
void* __cdecl exit_registry_malloc_005a3be5(U bytes) {void* result=malloc_mode?nullptr:arena+0x2000;events+="M:"+hx(bytes)+':'+hx(addr(result))+':'+state()+';';mutate(2);return result;}
int __cdecl formatter_cleanup_file_write_005a9e49(U file,const void* data,int length) {
    const U result=write_mode==0?static_cast<U>(length):write_mode==1?static_cast<U>(length)-1:write_mode==2?0xffffffffu:0;
    events+="W:"+hx(file)+':'+hx(loc(addr(data)))+':'+hx(static_cast<U>(length))+':'+hx(result)+':'+hex(data,static_cast<unsigned>(length))+':'+state()+';';mutate(4);return static_cast<int>(result);
}
int __cdecl formatter_core_005a4371(FormatterDescriptor005a0fbf* d,const char* format,const U* arguments) {
    events+="P:"+hx(loc(addr(d)))+':'+hex(format,static_cast<unsigned>(std::strlen(format))+1)+':';for(unsigned i=0;i<8;++i)events+=hx(arguments[i]);events+=':'+state()+';';
    auto* raw=reinterpret_cast<unsigned char*>(d);const U base=get(raw+8);
    if(base>=BASE && base+4<BASE+0x4000 || base>=addr(formatter_iob_entries_005e54e8) && base+4<addr(formatter_iob_entries_005e54e8)+640) {std::memcpy(reinterpret_cast<void*>(base),"ABCD",4);put(raw,base+4);put(raw+4,get(raw+4)-4);}
    mutate(8);if(variant&16)put(raw+12,get(raw+12)&~0x1000u);return static_cast<int>(index_value);
}
// Canonical storage references unused fatal callbacks; no replacement is callable.
void __cdecl formatter_default_float_failure_005abee8(const void*,char*,int,int,int) {std::abort();}
void __cdecl formatter_default_text_failure_005abee8(char*) {std::abort();}
}
namespace {
__declspec(noinline) U invoke(const void* function,U count,const U* args) {
    U result,before,after,saved_bx,saved_si,saved_di,flags;
    __asm {
        push ebx
        push esi
        push edi
        mov before,esp
        mov ecx,count
        mov edx,args
    next_argument:
        test ecx,ecx
        jz call_body
        dec ecx
        push dword ptr [edx+ecx*4]
        jmp next_argument
    call_body:
        mov ebx,12345678h
        mov esi,12345678h
        mov edi,12345678h
        cld
        call function
        mov result,eax
        mov saved_bx,ebx
        mov saved_si,esi
        mov saved_di,edi
        pushfd
        pop eax
        mov flags,eax
        mov ecx,count
        lea esp,[esp+ecx*4]
        mov after,esp
        pop edi
        pop esi
        pop ebx
    }
    if(before!=after || saved_bx!=0x12345678 || saved_si!=0x12345678 || saved_di!=0x12345678 || flags&0x400)std::abort();return result;
}
}
int main() {
    using namespace porsche;
    if(formatter_stdio_buffers_006afd60[0] || formatter_stdio_buffers_006afd60[1] || formatter_output_allocations_006afcf8)return 2;
    if(VirtualAlloc(arena,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE)!=arena)return 3;
    std::string payload;
    while(std::cin>>std::dec>>seq>>op>>std::hex>>selector>>index_value>>flags_value>>delta>>remaining>>size_value>>character_result>>malloc_mode>>write_mode>>variant>>counter>>temporary>>payload) {
        events.clear();for(U i=0;i<0x4000;++i)arena[i]=static_cast<unsigned char>(i*13+seq*7+0x21);
        auto* iob=reinterpret_cast<unsigned char*>(formatter_iob_entries_005e54e8);for(U i=0;i<640;++i)iob[i]=static_cast<unsigned char>(i*17+seq+0x31);
        for(std::size_t i=0;i<payload.size();i+=2)arena[0x500+i/2]=static_cast<unsigned char>(std::stoul(payload.substr(i,2),nullptr,16));
        formatter_output_allocations_006afcf8=counter;formatter_stdio_buffers_006afd60[0]=temporary&1?arena+0x3000:nullptr;formatter_stdio_buffers_006afd60[1]=temporary&2?arena+0x3100:nullptr;
        auto* d=active();if(selector<=2 || op==0) {auto* raw=reinterpret_cast<unsigned char*>(d);put(raw,BASE+0x1000+delta);put(raw+4,remaining);put(raw+8,BASE+0x1000);put(raw+12,flags_value);put(raw+16,0x11223344);put(raw+24,size_value);}
        const void* functions[]={reinterpret_cast<const void*>(formatter_stdio_printf_005a177b),reinterpret_cast<const void*>(formatter_stdio_lock_pointer_005a36ea),reinterpret_cast<const void*>(formatter_stdio_lock_index_005a3719),reinterpret_cast<const void*>(formatter_stdio_unlock_pointer_005a373c),reinterpret_cast<const void*>(formatter_stdio_unlock_index_005a376b),reinterpret_cast<const void*>(formatter_stdio_temporary_buffer_005a533e),reinterpret_cast<const void*>(formatter_stdio_finish_buffer_005a53cb),reinterpret_cast<const void*>(formatter_stdio_flush_005a76a1)};
        U args[9]{},count;
        if(op==0) {args[0]=BASE+0x500;for(unsigned i=0;i<8;++i)args[i+1]=get(arena+0x600+i*4);count=9;}
        else if(op==2 || op==4 || op==6) {args[0]=index_value;args[1]=addr(d);count=2;}
        else {args[0]=addr(d);count=1;}
        const U result=invoke(functions[op],count,args);
        std::printf("{\"case\":%u,\"result\":\"%08x\",\"events\":\"%s\",\"iob\":\"%s\",\"memory\":\"%s\",\"counter\":\"%08x\",\"buffers\":[\"%08x\",\"%08x\"]}\n",seq,op==0 || op==5 || op==7?result:0,events.c_str(),normalized(iob,640).c_str(),normalized(arena,0x4000).c_str(),formatter_output_allocations_006afcf8,loc(addr(formatter_stdio_buffers_006afd60[0])),loc(addr(formatter_stdio_buffers_006afd60[1])));
    }
}

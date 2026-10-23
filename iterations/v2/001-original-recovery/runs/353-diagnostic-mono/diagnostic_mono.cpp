#include "diagnostic_mono.hpp"
#include "porsche/formatter_entry.hpp"
#include "porsche/heap.hpp"
#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace porsche {
alignas(4) std::uint8_t diagnostic_mono_image_005e25dc[14]={
    0x02,0,0,0, 0,0,0x0b,0, 0x80,0x07,0,0, 0x07,0x08};
std::uint32_t diagnostic_mono_lock_006af140=0;
std::uint32_t diagnostic_mono_row_006af148=0;
namespace {
using U=std::uint32_t;
U load(U offset){U value;std::memcpy(&value,diagnostic_mono_image_005e25dc+offset,4);return value;}
void store(U offset,U value){std::memcpy(diagnostic_mono_image_005e25dc+offset,&value,4);}
void* pointer(U value){return reinterpret_cast<void*>(static_cast<std::uintptr_t>(value));}
U address(const void* value){return static_cast<U>(reinterpret_cast<std::uintptr_t>(value));}
std::uint8_t* display(){return static_cast<std::uint8_t*>(pointer(load(4)));}
void* lock(){return pointer(diagnostic_mono_lock_006af140);}
void ensure_lock(){if(!diagnostic_mono_lock_006af140)diagnostic_mono_lock_006af140=address(heap_lock_create_005321f0());}
}

// 005a299e has the same descriptor/limit/cleanup sequence as the accepted
// 005a0fbf raw formatter entry, including its opaque uninitialized tail.
int __cdecl application_diagnostic_mono_vsprintf_005a299e(char* output,
    const char* format,const U* arguments){
    return formatter_entry_raw_005a0fbf(output,format,arguments);
}

int __cdecl application_diagnostic_mono_format_00592a50(const char* format,...){
    if(static_cast<std::int32_t>(load(0))<2)return 0;
    ensure_lock();heap_enter_005322b0(lock());
    char buffer[256];
    std::va_list arguments;va_start(arguments,format);
    application_diagnostic_mono_vsprintf_005a299e(buffer,format,
        reinterpret_cast<const U*>(arguments));
    va_end(arguments);
    application_diagnostic_mono_write_00592b60(buffer);
    heap_leave_005322c0(lock());
    return 0;
}

int __cdecl application_diagnostic_mono_xy_format_00592ac0(
    std::int32_t x,std::int32_t y,const char* format,...){
    if(static_cast<std::int32_t>(load(0))<2)return 0;
    ensure_lock();heap_enter_005322b0(lock());
    if(x>=0&&x<80&&y>=0&&y<25)store(8,static_cast<U>((y*80+x)*2));
    char buffer[256];
    std::va_list arguments;va_start(arguments,format);
    application_diagnostic_mono_vsprintf_005a299e(buffer,format,
        reinterpret_cast<const U*>(arguments));
    va_end(arguments);
    application_diagnostic_mono_write_00592b60(buffer);
    heap_leave_005322c0(lock());
    return 0;
}

void __cdecl application_diagnostic_mono_scroll_00592d00(){
    if(static_cast<std::int32_t>(load(8))<4000)return;
    const U row=diagnostic_mono_row_006af148&0xffu;
    auto* base=display();
    heap_copy_dispatch_005323e0(base+row*160u,base+(row+1u)*160u,(24u-row)*160u);
    heap_fill_0053c290(base+0xf00,0,0xa0);
    store(8,0xf00);
}

void __cdecl application_diagnostic_mono_clear_00592d70(){
    if(static_cast<std::int32_t>(load(0))<2)return;
    ensure_lock();heap_enter_005322b0(lock());
    auto* base=display();
    for(U offset=0;offset<4000;offset+=4){U zero=0;std::memcpy(base+offset,&zero,4);}
    heap_leave_005322c0(lock());
}

void __cdecl application_diagnostic_mono_attribute_00592e00(U value){
    diagnostic_mono_image_005e25dc[12]=static_cast<std::uint8_t>(value);
}

void __cdecl application_diagnostic_mono_write_00592b60(const char* text){
    if(static_cast<std::int32_t>(load(0))<2)return;
    const U count=static_cast<U>(std::strlen(text));
    if(static_cast<std::int32_t>(count)<=0)return;
    std::uint8_t previous=0;
    for(U i=0;i<count;++i){
        U cursor=load(8);
        if(previous==0x0e){
            application_diagnostic_mono_attribute_00592e00(static_cast<std::uint8_t>(text[i]));
            previous=0;
            continue;
        }
        const U byte=static_cast<std::uint8_t>(text[i]);
        previous=static_cast<std::uint8_t>(byte);
        if(byte>=0x20){
            application_diagnostic_mono_scroll_00592d00();
            cursor=load(8);
            const std::uint16_t cell=static_cast<std::uint16_t>(
                (static_cast<U>(diagnostic_mono_image_005e25dc[12])<<8)|byte);
            std::memcpy(display()+cursor,&cell,2);
            store(8,cursor+2);
            continue;
        }
        if(byte==8){if(static_cast<std::int32_t>(cursor)>=2)store(8,cursor-2);}
        else if(byte==9){
            const U tab=diagnostic_mono_image_005e25dc[13];
            if(tab>1){
                const auto signed_cursor=static_cast<std::int32_t>(cursor);
                const auto row=signed_cursor/160;
                const auto column=(signed_cursor%160)/2;
                const auto next_tab=column/static_cast<std::int32_t>(tab)+1;
                const U next=((static_cast<U>(next_tab)*tab)+
                    static_cast<U>(row)*80u)*2u;
                store(8,next);
            }
        }else if(byte==10){
            const auto row=static_cast<std::int32_t>(cursor)/160;
            store(8,static_cast<U>(row+1)*160u);
            application_diagnostic_mono_scroll_00592d00();
        }else if(byte==11 || byte==12){
            if(byte==12)application_diagnostic_mono_clear_00592d70();
            store(8,(diagnostic_mono_row_006af148&0xffu)*160u);
        }
    }
}
}

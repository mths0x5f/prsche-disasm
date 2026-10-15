#include "porsche/formatter_stdio.hpp"
#include "porsche/formatter_entry.hpp"
#include <cstdarg>

namespace porsche {
void* formatter_stdio_buffers_006afd60[2]{};
namespace {
using U=std::uint32_t;
U address(const void* p) {return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
U read32(const void* p) {return *static_cast<const volatile U*>(p);}
std::uint16_t read16(const void* p) {return *static_cast<const volatile std::uint16_t*>(p);}
void write32(void* p,U v) {*static_cast<volatile U*>(p)=v;}
std::uint8_t* bytes(void* p) {return static_cast<std::uint8_t*>(p);}
void lock_pointer(FormatterOriginalDescriptor32* d,bool unlock) {
    const U p=address(d),first=address(formatter_iob_entries_005e54e8),last=first+19u*32u;
    if(p>=first && p<=last) {
        const U id=((p-first)>>5)+28;
        if(unlock)exit_registry_unlock_api_005a4c05(id);else exit_registry_lock_api_005a4ba4(id);
    } else {
        auto* critical=reinterpret_cast<void*>(static_cast<std::uintptr_t>(p+32));
        if(unlock)formatter_lowio_critical_leave(critical);else formatter_lowio_critical_enter(critical);
    }
}
}
void __cdecl formatter_stdio_lock_pointer_005a36ea(FormatterOriginalDescriptor32* d) {lock_pointer(d,false);}
void __cdecl formatter_stdio_unlock_pointer_005a373c(FormatterOriginalDescriptor32* d) {lock_pointer(d,true);}
void __cdecl formatter_stdio_lock_index_005a3719(std::int32_t index,FormatterOriginalDescriptor32* d) {
    if(index<20)exit_registry_lock_api_005a4ba4(static_cast<U>(index)+28);
    else formatter_lowio_critical_enter(reinterpret_cast<void*>(static_cast<std::uintptr_t>(address(d)+32)));
}
void __cdecl formatter_stdio_unlock_index_005a376b(std::int32_t index,FormatterOriginalDescriptor32* d) {
    if(index<20)exit_registry_unlock_api_005a4c05(static_cast<U>(index)+28);
    else formatter_lowio_critical_leave(reinterpret_cast<void*>(static_cast<std::uintptr_t>(address(d)+32)));
}
int __cdecl formatter_stdio_temporary_buffer_005a533e(FormatterOriginalDescriptor32* d) {
    auto* raw=bytes(d);
    if(!cleanup_is_character_device_005abf35(read32(raw+16)))return 0;
    U index;
    if(d==&formatter_iob_entries_005e54e8[1])index=0;
    else if(d==&formatter_iob_entries_005e54e8[2])index=1;
    else return 0;
    ++formatter_output_allocations_006afcf8;
    if(read16(raw+12)&0x10c)return 0;
    auto* slot=&formatter_stdio_buffers_006afd60[index];
    U buffer=read32(slot);
    if(!buffer) {
        buffer=address(exit_registry_malloc_005a3be5(0x1000));write32(slot,buffer);
        if(!buffer) {
            const U embedded=address(raw+20);
            write32(raw+8,embedded);write32(raw,embedded);write32(raw+24,2);write32(raw+4,2);
        } else {
            buffer=read32(slot);write32(raw+24,0x1000);write32(raw+8,buffer);write32(raw,buffer);write32(raw+4,0x1000);
        }
    } else {
        buffer=read32(slot);write32(raw+24,0x1000);write32(raw+8,buffer);write32(raw,buffer);write32(raw+4,0x1000);
    }
    *reinterpret_cast<volatile std::uint16_t*>(raw+12)=static_cast<std::uint16_t>(read16(raw+12)|0x1102);
    return 1;
}
int __cdecl formatter_stdio_flush_005a76a1(FormatterOriginalDescriptor32* d) {
    auto* raw=bytes(d);int result=0;
    const U flags=read32(raw+12);
    if((flags&3)==2 && (flags&0x108)) {
        const U base=read32(raw+8),length=read32(raw)-base;
        if(static_cast<std::int32_t>(length)>0) {
            const int written=formatter_cleanup_file_write_005a9e49(read32(raw+16),reinterpret_cast<const void*>(static_cast<std::uintptr_t>(base)),static_cast<std::int32_t>(length));
            if(static_cast<U>(written)==length) {
                const U current=read32(raw+12);
                if(current&0x80)write32(raw+12,current&~2u);
            } else {write32(raw+12,read32(raw+12)|0x20);result=-1;}
        }
    }
    const U base=read32(raw+8);write32(raw+4,0);write32(raw,base);
    return result;
}
void __cdecl formatter_stdio_finish_buffer_005a53cb(int installed,FormatterOriginalDescriptor32* d) {
    auto* raw=bytes(d);
    if(installed && (raw[13]&0x10)) {
        formatter_stdio_flush_005a76a1(d);
        *reinterpret_cast<volatile std::uint8_t*>(raw+13)&=0xee;
        write32(raw+24,0);write32(raw,0);write32(raw+8,0);
    }
}
int __cdecl formatter_stdio_printf_005a177b(const char* format,...) {
    auto* stream=&formatter_iob_entries_005e54e8[1];
    formatter_stdio_lock_index_005a3719(1,stream);
    const int installed=formatter_stdio_temporary_buffer_005a533e(stream);
    std::va_list arguments;va_start(arguments,format);
    const int result=formatter_core_005a4371(stream,format,reinterpret_cast<const U*>(arguments));
    va_end(arguments);
    formatter_stdio_finish_buffer_005a53cb(installed,stream);
    formatter_stdio_unlock_index_005a376b(1,stream);
    return result;
}
}

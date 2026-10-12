#include "porsche/formatter_output.hpp"

namespace porsche {
std::uint32_t formatter_output_allocations_006afcf8=0;
namespace {
const std::uint32_t error_pairs[90]={
#include "formatter_output_data.inc"
};
std::uint8_t* record(std::uint32_t id) {
    const auto index=static_cast<std::int32_t>(id)>>5;
    return const_cast<std::uint8_t*>(formatter_cleanup_handle_table_006c01e0[index])+(id&31u)*36u;
}
std::uint32_t word(const void* pointer) {return *static_cast<const volatile std::uint32_t*>(pointer);}
std::uint8_t flags(std::uint32_t id) {return *reinterpret_cast<const volatile std::uint8_t*>(record(id)+4);}
std::int32_t invalid() {
    *formatter_lowio_errno_005a669e()=9;
    *formatter_lowio_doserrno_005a66a7()=0;
    return -1;
}
}
std::int32_t* __cdecl formatter_output_map_error_005a662b(std::uint32_t error) {
    *formatter_lowio_doserrno_005a66a7()=error;
    unsigned index=0;
    while(index<45 && error_pairs[index*2]!=error)++index;
    auto* result=formatter_lowio_errno_005a669e();
    *result=index<45?static_cast<std::int32_t>(error_pairs[index*2+1]):
        error>=19 && error<=36?13:error>=188 && error<=202?8:22;
    return result;
}
std::int32_t __cdecl formatter_cleanup_file_aux_005a9ab8(std::uint32_t id,std::uint32_t offset,std::uint32_t origin) {
    if(id>=formatter_cleanup_handle_limit_006c02e0 || !(flags(id)&1))return invalid();
    formatter_lowio_lock_005ab726(id);
    const auto result=formatter_output_seek_inner_005a9b1d(id,offset,origin);
    formatter_lowio_unlock_005ab785(id);
    return result;
}
std::int32_t __cdecl formatter_output_seek_inner_005a9b1d(std::uint32_t id,std::uint32_t offset,std::uint32_t origin) {
    const auto handle=formatter_lowio_handle_005ab6e4(id);
    if(handle==0xffffffffu) {*formatter_lowio_errno_005a669e()=9;return -1;}
    const auto result=formatter_output_set_file_pointer(handle,static_cast<std::int32_t>(offset),nullptr,origin);
    const auto error=result==0xffffffffu?formatter_crt_get_last_error():0;
    if(error) {formatter_output_map_error_005a662b(error);return -1;}
    auto* flag=record(id)+4;
    *flag=static_cast<std::uint8_t>(*reinterpret_cast<const volatile std::uint8_t*>(flag)&0xfdu);
    return static_cast<std::int32_t>(result);
}
std::int32_t __cdecl formatter_cleanup_file_write_005a9e49(std::uint32_t id,const void* input,std::int32_t length) {
    if(id>=formatter_cleanup_handle_limit_006c02e0 || !(flags(id)&1))return invalid();
    formatter_lowio_lock_005ab726(id);
    const auto result=formatter_output_write_inner_005a9eae(id,input,length);
    formatter_lowio_unlock_005ab785(id);
    return result;
}
std::int32_t __cdecl formatter_output_write_inner_005a9eae(std::uint32_t id,const void* input,std::int32_t length) {
    if(!length)return 0;
    const auto count=static_cast<std::uint32_t>(length);
    auto* const source=static_cast<const std::uint8_t*>(input);
    const auto index=static_cast<std::int32_t>(id)>>5;
    const auto offset=(id&31u)*36u;
    auto* const bank_cell=formatter_cleanup_handle_table_006c01e0+index;
    auto current_record=[&]() {return *bank_cell+offset;};
    if(*reinterpret_cast<const volatile std::uint8_t*>(current_record()+4)&0x20)
        formatter_output_seek_inner_005a9b1d(id,0,2);
    std::uint32_t total=0,newlines=0,error=0;
    if(*reinterpret_cast<const volatile std::uint8_t*>(current_record()+4)&0x80) {
        std::uint32_t consumed=0;
        do {
            std::uint8_t scratch[1025];
            std::uint32_t used=0;
            while(consumed<count) {
                const auto value=*reinterpret_cast<const volatile std::uint8_t*>(source+consumed++);
                if(value==10) {++newlines;scratch[used++]=13;}
                scratch[used++]=value;
                if(used>=1024)break;
            }
            std::uint32_t written;
            if(!formatter_error_write_file(reinterpret_cast<void*>(word(current_record())),scratch,used,&written,nullptr)) {
                error=formatter_crt_get_last_error();break;
            }
            total+=written;
            if(static_cast<std::int32_t>(written)<static_cast<std::int32_t>(used))break;
            if(consumed>=count)break;
        } while(true);
    } else {
        std::uint32_t written;
        if(formatter_error_write_file(reinterpret_cast<void*>(word(current_record())),source,count,&written,nullptr))total=written;
        else error=formatter_crt_get_last_error();
    }
    if(total)return static_cast<std::int32_t>(total-newlines);
    if(error) {
        if(error==5) {*formatter_lowio_errno_005a669e()=9;*formatter_lowio_doserrno_005a66a7()=5;}
        else formatter_output_map_error_005a662b(error);
    } else {
        if((*reinterpret_cast<const volatile std::uint8_t*>(current_record()+4)&0x40) &&
            *reinterpret_cast<const volatile std::uint8_t*>(source)==0x1a)return 0;
        *formatter_lowio_errno_005a669e()=28;
        *formatter_lowio_doserrno_005a66a7()=0;
    }
    return -1;
}
std::int32_t __cdecl formatter_cleanup_prepare_descriptor_005abef1(FormatterOriginalDescriptor32* descriptor) {
    ++formatter_output_allocations_006afcf8;
    auto* allocated=static_cast<char*>(exit_registry_malloc_005a3be5(4096));
    descriptor->base=allocated;
    if(allocated) {descriptor->flags|=8;*reinterpret_cast<std::uint32_t*>(descriptor->opaque_tail+8)=4096;}
    else {descriptor->flags|=4;descriptor->base=reinterpret_cast<char*>(descriptor->opaque_tail+4);*reinterpret_cast<std::uint32_t*>(descriptor->opaque_tail+8)=2;}
    descriptor->remaining=0;descriptor->cursor=descriptor->base;
    return reinterpret_cast<std::int32_t>(descriptor->base);
}
int __cdecl formatter_wide_encode_boundary_005abf5e(char* output,std::uint32_t value) {
    formatter_text_increment_005b2258(&formatter_text_locale_readers_006c02e8);
    const auto decrement=formatter_text_decrement_005b2254;
    const bool writer=formatter_text_locale_writer_006c02e4!=0;
    if(writer) {decrement(&formatter_text_locale_readers_006c02e8);exit_registry_lock_api_005a4ba4(19);}
    const auto result=formatter_output_wide_inner_005abfb7(output,value);
    if(writer)exit_registry_unlock_api_005a4c05(19);
    else decrement(&formatter_text_locale_readers_006c02e8);
    return result;
}
int __cdecl formatter_output_wide_inner_005abfb7(char* output,std::uint32_t value) {
    if(!output)return 0;
    if(!formatter_text_locale_006afd80) {
        if(static_cast<std::uint16_t>(value)<=255) {*output=static_cast<char>(value);return 1;}
    } else {
        int used=0;
        const auto wide=static_cast<std::uint16_t>(value);
        const int result=formatter_locale_from_wide(formatter_locale_default_codepage_006afd90,0x220,&wide,1,
            output,formatter_float_character_width_005e54dc,nullptr,&used);
        if(result && !used)return result;
    }
    *formatter_lowio_errno_005a669e()=42;
    return -1;
}
}

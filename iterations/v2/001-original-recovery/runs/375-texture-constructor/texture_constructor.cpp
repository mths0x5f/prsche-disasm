#include "texture_constructor.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/formatter_entry.hpp"
#include "porsche/heap.hpp"
#include "porsche/files.hpp"
#include "porsche/splash_progress.hpp"
#include "porsche/startup_sequence.hpp"
#include <cstring>
namespace porsche {
// Original Porsche.exe00535700..00535947,00535380..00535400.
std::uint32_t texture_create_errors_005deb80=0;
const char texture_create_source_005bb660[]="\\real\\cmn\\createw.c";
const char texture_create_tag_005bb654[]="%dx%dx%d";
const char texture_create_dimensions_005bb5b8[]="WINDOW_create - INVALID WINDOW DIMENSIONS\nrequested: %dx%dx%d maximum: %dx%d\n";
const char texture_create_memory_005bb608[]="WINDOW_create - OUT OF MEMORY\nrequested: %dx%dx%d bytes: %d available: %d\n";
const char texture_create_depth_005bb674[]="WINDOW_create - INVALID DEPTH\nrequested: %dx%dx%d BPP MUST BE 1,4,8,15,16,24,OR 32\n";
namespace {
using U=std::uint32_t;using I=std::int32_t;using B=std::uint8_t;
U word(const void* p){U value;std::memcpy(&value,p,4);return value;}
void put(void* p,U value){std::memcpy(p,&value,4);}
void half(void* p,U value){const auto v=static_cast<std::uint16_t>(value);std::memcpy(p,&v,2);}
U address(const void* p){return static_cast<U>(reinterpret_cast<std::uintptr_t>(p));}
using Report=void (__cdecl*)(const char*,...);
Report report(){return reinterpret_cast<Report>(diagnostic_handler_005debf0);}
void diagnostic_line(U line){
    diagnostic_file_005deb74_set(texture_create_source_005bb660);
    application_diagnostic_line_005deb78=line;
}
}
U __cdecl texture_depth_format_00535380(U depth){
    switch(depth){
    case 1:return 0x79;case 4:return 0x7a;case 8:return 0x7b;
    case 15:case 0x22b:case 0x613:return 0x7e;
    case 16:case 0x235:return 0x78;case 24:case 0x378:return 0x7f;
    case 32:case 0x22b8:return 0x7d;case 0x115c:return 0x6d;
    default:return 0;
    }
}
void* __cdecl render_descriptor_allocate_00535700(U width,U height,U depth,U flags,U diagnostics){
    if(static_cast<I>(width)<0||static_cast<I>(width)>0x4000||
       static_cast<I>(height)<0||static_cast<I>(height)>0x2000){
        if(diagnostics){diagnostic_line(0x55);report()(texture_create_dimensions_005bb5b8,width,height,depth,0x4000,0x2000);}
        return nullptr;
    }
    if(depth==0){depth=splash_progress_format_005dead0;if(depth==0)depth=16;}
    const U format=texture_depth_format_00535380(depth);
    const U bits=render_descriptor_bits_00537f90(&format);
    const U storage_bits=bits==15?16:bits;
    if(format==0){
        if(diagnostics){diagnostic_line(0x66);report()(texture_create_depth_005bb674,width,height,depth);}
        return nullptr;
    }
    // Original signed IDIV, multiply and arithmetic shift; valid dimensions
    // and proved format table keep all these intermediates within int32.
    const I rounded=static_cast<I>((storage_bits*width+7u)&0xfffffff8u);
    const I pitch=((rounded/static_cast<I>(storage_bits))*static_cast<I>(storage_bits))>>3;
    const U bytes=static_cast<U>(pitch)*height+0x40u;
    char tag[16];
    formatter_entry_005a0fbf(tag,texture_create_tag_005bb654,width,height,depth);
    auto* result=static_cast<B*>(application_allocator_entry_00531f70(tag,bytes,flags));
    if(!result){
        if(diagnostics){
            const U errors=texture_create_errors_005deb80;
            diagnostic_line(0x83);texture_create_errors_005deb80=errors+1u;
            const U available=startup_sequence_value_00569a90();
            report()(texture_create_memory_005bb608,width,height,depth,bytes,available);
        }
        return nullptr;
    }
    heap_fill_0053c290(result,0,0x40);
    auto* sprite=result+0x30;
    const U previous=word(sprite);
    const float storage_float=static_cast<float>(storage_bits);U float_word;
    std::memcpy(&float_word,&storage_float,4);
    half(sprite+4,width);
    put(result+0x28,address(sprite));
    put(sprite,previous^((format^previous)&0xffu));
    put(result,0x57494e44);
    result[0x0c]=sprite[0];
    half(sprite+6,height);
    result[0x0f]=static_cast<B>((float_word>>23)+0x7eu);
    result[0x0d]=static_cast<B>(bits);
    put(result+0x24,static_cast<U>(pitch));put(result+0x2c,address(result+0x40));
    put(result+4,width);put(result+8,height);result[0x10]=0;
    result[0x0e]=static_cast<B>(storage_bits);
    put(result+0x14,0);put(result+0x18,0);put(result+0x1c,width);put(result+0x20,height);
    return result;
}
}

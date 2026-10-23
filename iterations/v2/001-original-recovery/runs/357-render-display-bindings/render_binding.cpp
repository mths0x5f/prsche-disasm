#include "porsche/render_display.hpp"
#include "porsche/render_loader.hpp"
#include <cstdint>

namespace porsche {
namespace {
template<class T> T slot(std::uint32_t index){
    return reinterpret_cast<T>(static_cast<std::uintptr_t>(render_thrash_exports_006bd910[index]));
}
template<class T> T address(std::uint32_t proc){
    return reinterpret_cast<T>(static_cast<std::uintptr_t>(proc));
}
using Get=std::uint32_t (__stdcall*)(std::uint32_t);
using Set=std::uint32_t (__stdcall*)(std::uint32_t,std::uint32_t);
using Zero=void (__stdcall*)();
using One=void (__stdcall*)(std::uint32_t);
using Quad=void (__stdcall*)(const void*,const void*,const void*,const void*);
using Rect=void (__stdcall*)(std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t,void*);
using About=const std::uint32_t* (__stdcall*)();
}
std::uint32_t __stdcall render_display_getstate_006bd984(std::uint32_t key){return slot<Get>(29)(key);}
void __stdcall render_display_setstate_006bd97c(std::uint32_t key,std::uint32_t value){(void)slot<Set>(27)(key,value);}
void __stdcall render_display_window_006bd9b0(std::uint32_t mode){slot<One>(40)(mode);}
void __stdcall render_display_set_texture_006bd954(std::uint32_t value){slot<One>(17)(value);}
void __stdcall render_display_clear_window_006bd91c(){slot<Zero>(3)();}
void __stdcall render_display_draw_quad_006bd9a8(const void* a,const void* b,const void* c,const void* d){slot<Quad>(38)(a,b,c,d);}
void __stdcall render_display_flush_006bd970(){slot<Zero>(24)();}
void __stdcall render_display_sync_006bd978(std::uint32_t zero){slot<One>(26)(zero);}
void __stdcall render_display_read_rect_006bd96c(std::uint32_t x,std::uint32_t y,std::uint32_t width,std::uint32_t height,void* output){slot<Rect>(23)(x,y,width,height,output);}
void __cdecl render_loader_set_state_006bd97c(std::uint32_t proc,std::uint32_t key,std::uint32_t value){(void)address<Set>(proc)(key,value);}
const std::uint32_t* __cdecl render_loader_about_006bd934(std::uint32_t proc){return address<About>(proc)();}
}

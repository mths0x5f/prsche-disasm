#pragma once
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/context_move.hpp"
namespace porsche {
extern std::uint32_t formatter_small_capacity_006c01c0;
extern std::uint32_t formatter_small_pending_group_006c01c4;
extern std::uint8_t* formatter_small_cursor_006c01c8;
extern std::uint8_t* formatter_small_pending_006c01cc;
int __cdecl formatter_small_initialize_005aa96c();
std::uint8_t* __cdecl formatter_small_new_header_005ab009();
std::int32_t __cdecl formatter_small_commit_005ab0ba(std::uint8_t*);
int __cdecl formatter_small_resize_005ab1b5(std::uint8_t*,void*,std::uint32_t);
int __cdecl formatter_small_heap_initialize_005a96fa(std::uint32_t);
void* __cdecl formatter_small_copy_005a7ad0(void*,const void*,std::uint32_t);
// Canonical exit-registry declarations for realloc and allocation-size are reused.
void* __stdcall formatter_small_heap_reallocate(std::uint32_t,std::uint32_t,void*,std::uint32_t);
std::uint32_t __stdcall formatter_small_heap_size(std::uint32_t,std::uint32_t,const void*);
std::uint32_t __stdcall formatter_small_heap_create(std::uint32_t,std::uint32_t,std::uint32_t);
int __stdcall formatter_small_heap_destroy(std::uint32_t);
void* __stdcall formatter_small_virtual_allocate(void*,std::uint32_t,std::uint32_t,std::uint32_t);
int __stdcall formatter_small_virtual_free(void*,std::uint32_t,std::uint32_t);
}

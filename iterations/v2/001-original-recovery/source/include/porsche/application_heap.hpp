#pragma once
#include <cstdint>
#include "porsche/shared_runtime_globals.hpp"

namespace porsche {
// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 0059ed40 and 0059ed90 are the original VirtualAlloc/VirtualFree wrappers.
extern std::uint32_t& application_page_size_006af3f8;
extern std::uint8_t& application_heap_initialized_006af3f4;
extern void*& application_primary_arena_006af3b4;
extern std::int32_t& application_object_heap_006af3fc;
extern std::uint8_t (&application_heap_records)[0x8c0];
extern void* (&application_queue_indices)[16];
void* __cdecl application_page_alloc_0059ed40(std::uint32_t* bytes);
std::uint32_t __cdecl application_page_release_0059ed90(void* address);
void __cdecl startup_heap_0059e9d0(std::uint32_t primary_bytes,
    std::uint32_t object_bytes,std::uint32_t third,std::uint32_t fourth);
void __cdecl startup_queue_0059edb0(std::uint32_t count,std::uint32_t slot);

// Controlled OS boundaries. They must be supplied by the platform/fixture.
std::uint32_t __cdecl application_system_page_size();
void* __cdecl application_virtual_alloc(void* address,std::uint32_t bytes,
                                           std::uint32_t allocation_type,std::uint32_t protection);
std::uint32_t __cdecl application_virtual_free(void* address,std::uint32_t bytes,
                                                  std::uint32_t free_type);
void __cdecl application_os_start(std::uint32_t);
void __cdecl application_fill(void*,std::uint32_t,std::uint32_t);
void* __cdecl application_lock_create();
void __cdecl application_lock_enter(void*);
void __cdecl application_lock_leave(void*);
void __cdecl application_heap_commit(void*,std::uint32_t);
std::int32_t __cdecl application_object_start(std::uint32_t,const char*,std::uint32_t,
                                              std::uint32_t,std::uint32_t);
void __cdecl application_memory_diagnostic(std::uint32_t);
void __cdecl application_secondary_start();
void __cdecl application_queue_kind(std::uint32_t,std::uint32_t);
void __cdecl application_printf_start(std::uint32_t,const char*);
void __cdecl application_heap_kind(std::uint32_t,std::uint32_t);
void __cdecl application_heap_finish(std::uint32_t,std::uint32_t,std::uint32_t);
void* __cdecl application_queue_allocate(std::uint32_t,std::uint32_t,void*);
}

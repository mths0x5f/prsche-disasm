#pragma once
#include <cstdint>

namespace porsche {
// 005aef80 primary FE heap and 0059ebc0 optional object heap.
extern void* application_default_arena_005deb98;
extern void* (&application_other_arenas_006af3b8)[15];
extern char application_object_heap_name_005e8e50[32];
std::int32_t __cdecl application_heap_callback_005aef70();
void __cdecl application_heap_commit(void* arena,std::uint32_t bytes);
std::int32_t __cdecl application_object_start(std::uint32_t bytes,const char* label,
    std::uint32_t queue_slot,std::uint32_t locked,std::uint32_t quantum);
}

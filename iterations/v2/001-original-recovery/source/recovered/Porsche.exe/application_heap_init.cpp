#include "porsche/application_heap_init.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/application_heap_state.hpp"
#include "porsche/heap.hpp"
#include <cstddef>

namespace porsche {
void* application_default_arena_005deb98=nullptr;
char application_object_heap_name_005e8e50[32]{};

// 005aef70..005aef72: callback stored by primary heap initialization.
std::int32_t __cdecl application_heap_callback_005aef70(){return 0;}

// 005aef80..005aefca: primary arena is heap zero and heap one aliases it.
void __cdecl application_heap_commit(void* arena,std::uint32_t bytes){
    // 005c250c contains the original four-byte "RAM\0" label.
    heap_init_005697f0(0,"RAM",arena,static_cast<std::int32_t>(bytes),
        8,0x40,0,0,0,0,1,reinterpret_cast<void*>(&application_heap_callback_005aef70));
    heaps_006b4f20[1]=heaps_006b4f20[0];
    if(!application_default_arena_005deb98)application_default_arena_005deb98=arena;
}

// 00569a70..00569a8b scans heap slots [3, 16) and returns 16 if full.
static std::uint32_t object_heap_slot_00569a70(){
    std::uint32_t index=3;
    while(index<16 && heaps_006b4f20[index])++index;
    return index;
}

// 0059ebc0..0059ec39. The caller's label argument is unused. Both global
// stores precede the allocation failure check, as in the original body.
std::int32_t __cdecl application_object_start(std::uint32_t bytes,const char*,
    std::uint32_t queue_slot,std::uint32_t locked,std::uint32_t quantum){
    const auto index=object_heap_slot_00569a70();
    if(queue_slot){
        application_heap_store(application_heap_address(application_heap_contexts.selectors,
            0u-queue_slot*4u),index);
    }
    void* arena=application_page_alloc_0059ed40(&bytes);
    application_heap_store(application_heap_arena_cell(index),application_heap_word(arena));
    if(!arena)return -1;
    heap_init_005697f0(index,application_object_heap_name_005e8e50,arena,
        static_cast<std::int32_t>(bytes),quantum,0x20,0,0,0,0,
        static_cast<std::uint8_t>(locked)?1:0,nullptr);
    return static_cast<std::int32_t>(index);
}
}

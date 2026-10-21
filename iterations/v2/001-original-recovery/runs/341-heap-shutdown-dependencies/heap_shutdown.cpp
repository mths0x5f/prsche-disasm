#include "porsche/application_heap_state.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"

namespace porsche {

// Porsche.exe ddd748fd, 0059ee30..0059eeab. The record and its lock
// address are selected before entry. The free callback and final lock value
// are deliberately loaded again across the callback boundary.
void __cdecl application_heap_queue_clean_0059ee30(std::uint32_t selector) {
    void* record=application_heap_address(application_heap_contexts.current,
        0x28u-selector*0x8cu);
    application_lock_enter(application_heap_pointer(application_heap_load(record)));
    auto node=application_heap_load(application_heap_address(record,8));
    while(node) {
        const auto previous=application_heap_load(application_heap_address(record,4));
        const auto next=application_heap_load(application_heap_address(
            application_heap_pointer(node),4));
        application_heap_store(application_heap_address(application_heap_pointer(node),4),previous);
        application_heap_store(application_heap_address(record,4),node);
        node=next;
    }
    node=application_heap_load(application_heap_address(record,4));
    while(node) {
        const auto next=application_heap_load(application_heap_address(
            application_heap_pointer(node),4));
        using Free=std::uint32_t (__cdecl*)(void*);
        const auto callback=reinterpret_cast<Free>(application_heap_pointer(
            application_heap_load(application_heap_address(application_heap_contexts.current,8))));
        callback(application_heap_pointer(node));
        node=next;
    }
    for(std::uint32_t i=0;i<16;++i)
        application_heap_store(application_heap_address(record,0xcu+i*4u),0);
    application_lock_leave(application_heap_pointer(application_heap_load(record)));
}

// Porsche.exe ddd748fd, 005699f0..00569a37. A lock-destroy callback may
// replace the global heap slot; the original clears the captured slot.
std::uint32_t __cdecl application_heap_destroy_005699f0(std::uint32_t id) {
    const auto index=id&15u;
    auto* heap=heaps_006b4f20[index];
    if(!heap)return 0;
    const auto lock=application_heap_load(application_heap_address(heap,0x38));
    if(lock)heap_lock_destroy_005322d0(application_heap_pointer(lock));
    heap_fill_0053c290(heap,0,0x40);
    heaps_006b4f20[index]=nullptr;
    return 1;
}
}

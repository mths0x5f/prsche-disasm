#include "heap_slot_release_304.hpp"
#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
namespace porsche {
std::uint32_t __cdecl heap_slot_release_005699f0(std::uint32_t id) {
    const auto index=id&0xfu;
    auto* slots=reinterpret_cast<OriginalHeap* volatile*>(heaps_006b4f20);
    OriginalHeap* const heap=slots[index];
    if(!heap) return 0;
    void* const lock=*reinterpret_cast<void* volatile*>(reinterpret_cast<std::uint8_t*>(heap)+0x38);
    if(lock) heap_lock_destroy_005322d0(lock);
    // ESI retains the original heap across both callbacks; EDI retains the slot.
    heap_fill_0053c290(heap,0,0x40);
    slots[index]=nullptr;
    return 1;
}
}

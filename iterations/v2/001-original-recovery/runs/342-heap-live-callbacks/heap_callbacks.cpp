#include "porsche/application_heap_state.hpp"
#include "porsche/heap.hpp"
#include <cstdint>
#include <cstring>

// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Exact bodies and relocation-backed entries: supplemental/heap-live-callbacks-342.jsonl.
namespace porsche {
namespace {
std::uint32_t load32(std::uint32_t address) {
    return application_heap_load(application_heap_pointer(address));
}
std::uint16_t load16(std::uint32_t address) {
    std::uint16_t value;
    std::memcpy(&value,application_heap_pointer(address),sizeof(value));
    return value;
}
std::uint8_t load8(std::uint32_t address) {
    return *static_cast<const std::uint8_t*>(application_heap_pointer(address));
}
}

// 00556680..0055668a: the two-byte load is zero-extended into EAX.
std::uint32_t __cdecl application_heap_tag_00556680(const void* allocation) {
    return load16(application_heap_word(allocation)-14u);
}

// 00569ad0..00569b09: size comparison is signed. The 0x4253 check occurs
// only after a block beats the current maximum; preserve that scan order.
std::uint32_t __cdecl application_heap_measure_00569ad0(std::uint32_t index) {
    std::uint32_t current=application_heap_word(heaps_006b4f20[index&15u])+16u;
    std::uint32_t selected=0;
    std::int32_t maximum=0;
    for(;;) {
        current=load32(current+16u);
        const auto size=static_cast<std::int32_t>(load32(current+4u));
        if(size<=maximum) continue;
        if(load16(current)==0x4253u) break;
        selected=current;
        maximum=size;
    }
    return selected?load32(selected+4u):0u;
}

// 005aef20..005aef6f: a flagged containing block skips to the next heap.
// All comparisons and the end-address addition use x86 unsigned DWORDs.
void* __cdecl application_heap_block_005aef20(void* address) {
    const auto candidate=application_heap_word(address);
    for(std::uint32_t index=0;index<16u;++index) {
        auto* heap=heaps_006b4f20[index];
        if(!heap) continue;
        const auto low=load32(application_heap_word(heap)+8u);
        auto block=load32(low+8u);
        while(block) {
            const auto begin=block+16u;
            const auto end=begin+load32(block+4u);
            if(candidate>=begin && candidate<end) {
                if((load8(block+3u)&0xc0u)==0)
                    return application_heap_pointer(begin);
                break;
            }
            block=load32(block+8u);
        }
    }
    return nullptr;
}
}

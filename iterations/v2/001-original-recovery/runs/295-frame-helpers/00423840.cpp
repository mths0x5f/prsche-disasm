#include "../290-frame-service-cluster/frame_service_290.hpp"

namespace porsche {
namespace {
std::uint32_t word(std::uint32_t address, unsigned offset) {
    return *reinterpret_cast<const std::uint32_t*>(static_cast<std::uintptr_t>(address) + offset);
}
}

void __thiscall FrameIterator_290::advance_00423840() {
    auto* current = reinterpret_cast<std::uint32_t*>(this);
    std::uint32_t node = *current;
    std::uint32_t next = word(node, 0x0c);
    if (next) {
        *current = next;
        while (word(next, 8)) {
            next = word(next, 8);
            *current = next;
        }
        return;
    }
    next = word(node, 4);
    while (node == word(next, 0x0c)) {
        *current = next;
        next = word(next, 4);
        node = *current;
    }
    if (word(*current, 0x0c) != next) *current = next;
}
}

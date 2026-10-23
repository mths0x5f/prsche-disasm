#pragma once
#include "../361-startup-device-pool/startup_pool.hpp"
#include <cstdint>

namespace porsche {
// An explicit view over two independently owned native slots. The original
// queue ABI takes adjacent DWORDs; canonical pool globals are separate objects.
class AsyncQueueSlot {
    std::uint32_t* word_ = nullptr;
    void** pointer_ = nullptr;
public:
    explicit AsyncQueueSlot(std::uint32_t& word) : word_(&word) {}
    explicit AsyncQueueSlot(void*& pointer) : pointer_(&pointer) {}
    std::uint32_t get() const {
        return word_ ? *word_ : static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(*pointer_));
    }
    void set(std::uint32_t value) const {
        if (word_) *word_ = value;
        else *pointer_ = reinterpret_cast<void*>(static_cast<std::uintptr_t>(value));
    }
};
struct AsyncQueueView { AsyncQueueSlot head, tail; };
AsyncQueueView async_incoming_queue();
AsyncQueueView async_free_queue();
// Typed source ABI adapters, not binary aliases of the adjacent-DWORD ABI.
void __cdecl async_enqueue_00563c30(AsyncQueueView, std::uint32_t* record);
std::uint32_t* __cdecl async_dequeue_00563c70(AsyncQueueView);
void __cdecl async_dispatch_00563cc0(std::uint32_t* record);
} // namespace porsche

#include "async_callbacks.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/heap.hpp"

namespace porsche {
// Porsche.exe SHA ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00563bd0/00563c30/00563c70/00563cc0, complete bodies, 330 original bytes.
static_assert(sizeof(void*) == 4, "original async records use Win32 pointers");
namespace {
std::uint32_t address(const void* pointer) {
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(pointer));
}
std::uint32_t* record_at(std::uint32_t value) {
    return reinterpret_cast<std::uint32_t*>(static_cast<std::uintptr_t>(value));
}
}
AsyncQueueView async_incoming_queue() {
    return {AsyncQueueSlot(async_pool_head_006a5bc8), AsyncQueueSlot(async_pool_tail_006a5bcc)};
}
AsyncQueueView async_free_queue() {
    return {AsyncQueueSlot(async_pool_first_006a5bd0), AsyncQueueSlot(async_pool_last_006a5bd4)};
}
void __cdecl async_enqueue_00563c30(AsyncQueueView queue, std::uint32_t* record) {
    heap_enter_005322b0(async_pool_lock_006a5be8);
    if (queue.head.get() == 0) queue.head.set(address(record));
    else record_at(queue.tail.get())[1] = address(record);
    queue.tail.set(address(record));
    record[1] = 0;
    heap_leave_005322c0(async_pool_lock_006a5be8);
}
std::uint32_t* __cdecl async_dequeue_00563c70(AsyncQueueView queue) {
    heap_enter_005322b0(async_pool_lock_006a5be8);
    auto* record = record_at(queue.head.get());
    void* const leave_lock = async_pool_lock_006a5be8;
    if (record) queue.head.set(record[1]);
    // Original does not clear a singleton's stale tail or the removed link.
    heap_leave_005322c0(leave_lock);
    return record;
}
void __cdecl async_dispatch_00563cc0(std::uint32_t* record) {
    heap_enter_005322b0(async_pool_lock_006a5be8);
    const std::uint32_t state = record[3];
    if (state == 1) record[3] = 2;
    heap_leave_005322c0(async_pool_lock_006a5be8);
    if (state == 1) {
        if (record[4] > 1u) free_00531f90(record_at(record[4]));
        record[0] &= 0xffu;
        record[6] = 0;
        async_enqueue_00563c30(async_free_queue(), record);
    }
}
std::uint32_t __cdecl async_pool_callback_00563bd0(std::uint32_t, std::uint32_t) {
    while (auto* record = async_dequeue_00563c70(async_incoming_queue())) {
        if (record[3] == 0) {
            const std::uint32_t saved_id = record[0];
            reinterpret_cast<void (__cdecl*)(std::uint32_t)>(record_at(record[5]))(saved_id);
            record[0] = saved_id & 0xffu;
            async_enqueue_00563c30(async_free_queue(), record);
        } else async_dispatch_00563cc0(record);
    }
    return 0;
}
} // namespace porsche

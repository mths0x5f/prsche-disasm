#include "heap_shutdown_418.hpp"

namespace porsche {
namespace {

void*& arena_slot_006af3b4(std::int32_t index) {
    return index == 0
        ? application_primary_arena_006af3b4
        : application_other_arenas_006af3b8[index - 1];
}

} // namespace

// 0055ec30..0055ec43 (20 bytes)
void __cdecl printf_shutdown_0055ec30() {
    if (printf_initialized_006a57cc != 0u) {
        printf_initialized_006a57cc = 0u;
    }
}

// 005678f0..005679e7 (248 bytes)
void __cdecl application_pool_shutdown_005678f0() {
    if (devices_006a5c7c == nullptr) {
        return;
    }

    for (IoNode* node = io_pop_00580790(&free_auxiliary_006a5c38);
         node != nullptr;
         node = io_pop_00580790(&free_auxiliary_006a5c38)) {
        void* handle = *reinterpret_cast<void**>(
            reinterpret_cast<std::uint8_t*>(node) + 0x0cu);
        file_physical_close_00592290(handle);
        file_object_free_0056e640(node);
    }

    file_shutdown_006a5c80 = 1u;

    for (std::uint32_t offset = 0u; offset < 0xe00u; offset += 0x70u) {
        auto* dev = reinterpret_cast<FileDevice*>(
            reinterpret_cast<std::uint8_t*>(devices_006a5c7c) + offset);
        if (dev->initialized != 0u) {
            void* queued_ev = dev->queued_event;
            file_event_signal_0055fb30(queued_ev);
            while (*reinterpret_cast<volatile std::uint32_t*>(&dev->initialized) != 0u) {
                file_sleep_0055f740(0u);
            }
            file_close_event_0055fc10(queued_ev);
            file_signal_close_0055fc80(dev->completed_event);
            network_worker_queue_dispose_005806c0(&dev->completed);
            network_worker_queue_dispose_005806c0(&dev->queued);
        }
    }

    file_object_free_0056e640(free_operation_arena_006a5c54);
    file_object_free_0056e640(devices_006a5c7c);
    network_worker_queue_dispose_005806c0(&free_operations_006a5c58);
    network_worker_queue_dispose_005806c0(&free_auxiliary_006a5c38);
    heap_lock_destroy_005322d0(application_pool_lock_006a5c78);
    devices_006a5c7c = nullptr;
}

// 005699f0..00569a37 (72 bytes)
std::int32_t __cdecl heap_destroy_slot_005699f0(std::uint32_t slot) {
    const std::uint32_t idx = slot & 0x0fu;
    OriginalHeap* heap = heaps_006b4f20[idx];
    OriginalHeap** cell = &heaps_006b4f20[idx];
    if (heap == nullptr) {
        return 0;
    }
    if (heap->lock != nullptr) {
        heap_lock_destroy_005322d0(heap->lock);
    }
    heap_fill_0053c290(heap, 0u, 0x40u);
    *cell = nullptr;
    return 1;
}

// 0059ee30..0059eeab (124 bytes)
void __cdecl queue_drain_0059ee30(std::int32_t slot) {
    auto* state = static_cast<std::uint8_t*>(heap_state_005e4fe8);
    auto* record = state - (slot * 0x8c) + 0x28;
    heap_enter_005322b0(*reinterpret_cast<void**>(record));

    void* node = *reinterpret_cast<void**>(record + 8);
    while (node != nullptr) {
        void* head4 = *reinterpret_cast<void**>(record + 4);
        void** next_ptr = reinterpret_cast<void**>(
            static_cast<std::uint8_t*>(node) + 4);
        void* curr = node;
        node = *next_ptr;
        *next_ptr = head4;
        *reinterpret_cast<void**>(record + 4) = curr;
    }

    void* drain_node = *reinterpret_cast<void**>(record + 4);
    while (drain_node != nullptr) {
        auto* current_state = static_cast<std::uint8_t*>(heap_state_005e4fe8);
        void* curr = drain_node;
        drain_node = *reinterpret_cast<void**>(
            static_cast<std::uint8_t*>(curr) + 4);
        using ReleaseFn = void(__cdecl*)(void*);
        auto release_fn = *reinterpret_cast<ReleaseFn*>(current_state + 8);
        release_fn(curr);
    }

    auto* clear_words = reinterpret_cast<std::uint32_t*>(record + 0x0c);
    for (std::uint32_t i = 0u; i < 0x10u; ++i) {
        clear_words[i] = 0u;
    }

    heap_leave_005322c0(*reinterpret_cast<void**>(record));
}

// 0059eb20..0059ebbe (159 bytes)
void __cdecl platform_flush_0059eb20() {
    if (application_heap_initialized_006af3f4 == 0u) {
        return;
    }

    application_pool_shutdown_005678f0();
    printf_shutdown_0055ec30();

    const std::int32_t obj_heap = application_object_heap_006af3fc;
    std::int32_t* selector = heap_selector_005e4fec;
    for (std::uint32_t i = 0u; i < 16u; ++i) {
        if (selector[i] == obj_heap) {
            queue_drain_0059ee30(-static_cast<std::int32_t>(i));
            heap_selector_005e4fec[i] = 0;
            break;
        }
    }

    heap_destroy_slot_005699f0(static_cast<std::uint32_t>(obj_heap));
    void* arena = arena_slot_006af3b4(obj_heap);
    platform_virtual_free(arena, 0u, 0x8000u);

    const std::int32_t reloaded_obj_heap = application_object_heap_006af3fc;
    arena_slot_006af3b4(obj_heap) = nullptr;
    application_primary_arena_006af3b4 = nullptr;
    heap_state_005e4fe8 = default_heap_state_005e3e18;
    arena_slot_006af3b4(reloaded_obj_heap) = nullptr;
}

} // namespace porsche

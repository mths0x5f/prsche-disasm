#include "app_main_subsystem_advanced_303.hpp"

namespace porsche {

// =============================================================================
// Function 1: 00531f90 (270 bytes) - Heap Pool Block Deallocator
// =============================================================================
int CALL_CDECL heap_pool_block_free_00531f90(void* user_ptr) {
    if (user_ptr == nullptr) {
        return 1;
    }

    auto* block = reinterpret_cast<HeapBlockHeader*>(static_cast<char*>(user_ptr) - 0x10);
    std::uint32_t pool_idx = block->flags & 0x0f;
    HeapPoolDescriptor* pool = g_heap_pools_006b4f20[pool_idx];
    void* lock = pool->lock;
    if (lock != nullptr) {
        lock_acquire_005322b0(lock);
    }

    HeapBlockHeader* next = block->next_phys;
    HeapBlockHeader* prev = block->prev_phys;

    // Coalesce forward with next physical block if free
    if ((next->flags & 0x4000) != 0) {
        HeapBlockHeader* fn = next->free_next;
        HeapBlockHeader* fp = next->free_prev;
        next->flags &= 0xbfff;
        next->magic = 0;
        fn->free_prev = fp;
        fp->free_next = fn;

        HeapBlockHeader* nn = next->next_phys;
        block = next;
        prev->next_phys = block;
        block->prev_phys = prev;
        nn->prev_phys = block;
    }

    // Coalesce backward with previous physical block if free
    if ((prev->flags & 0x4000) != 0) {
        HeapBlockHeader* fn = prev->free_next;
        HeapBlockHeader* fp = prev->free_prev;
        prev->flags &= 0xbfff;
        prev->magic = 0;
        prev = prev->prev_phys;
        fn->free_prev = fp;
        fp->free_next = fn;

        block->prev_phys = prev;
        prev->next_phys = block;
    }

    // Insert into ordered free list (bidirectional search from sentinel)
    HeapBlockHeader* cur = &pool->free_head;
    HeapBlockHeader* free_prev_node = cur->free_prev;
    HeapBlockHeader* free_next_node = cur->free_next;
    std::size_t raw_size = reinterpret_cast<std::uintptr_t>(block->prev_phys) - reinterpret_cast<std::uintptr_t>(block) - 0x10;

    std::uintptr_t limit = (reinterpret_cast<std::uintptr_t>(free_next_node) - reinterpret_cast<std::uintptr_t>(free_prev_node)) / 2 + reinterpret_cast<std::uintptr_t>(free_prev_node);

    HeapBlockHeader* ins_prev;
    HeapBlockHeader* ins_next;

    if (reinterpret_cast<std::uintptr_t>(block) <= limit) {
        ins_prev = cur;
        do {
            ins_prev = ins_prev->free_prev;
        } while (reinterpret_cast<std::uintptr_t>(block) > reinterpret_cast<std::uintptr_t>(ins_prev));
        ins_next = ins_prev->free_next;
    } else {
        ins_next = cur;
        do {
            ins_next = ins_next->free_next;
        } while (reinterpret_cast<std::uintptr_t>(block) < reinterpret_cast<std::uintptr_t>(ins_next));
        ins_prev = ins_next->free_prev;
    }

    block->flags |= 0x4000;
    block->free_prev = ins_prev;
    block->free_next = ins_next;
    block->size = static_cast<std::uint32_t>(raw_size);
    ins_next->free_prev = block;
    ins_prev->free_next = block;
    block->magic = 0x4246;

    if (lock != nullptr) {
        lock_release_005322c0(lock);
    }
    return 1;
}

// =============================================================================
// Function 2: 004a6840 (279 bytes) - Display Device Mode Transition Manager
// =============================================================================
void CALL_CDECL display_device_transition_004a6840(std::uint32_t mode, std::uint32_t arg2) {
    std::uint32_t state = g_val_00657c98;
    g_val_00657c9c = 0;
    if (state == 3) {
        g_val_00657c94 = 1;
    }
    g_val_00655d38 = state;
    g_val_00655d3c = 0;
    g_val_00655d34 = mode;

    void* buf = heap_pool_alloc_00531ca0(g_str_tag_005d13ec, 0x40000, 0);
    g_val_00655d44 = buf;

    for (int i = 0; i < 8; ++i) {
        g_devices_006564a0[i].field_00 = -1;
        g_devices_006564a0[i].field_08 = 0;
    }

    if (display_mode_probe_004a66b0() != 0) {
        if (static_cast<std::int32_t>(mode) > 0) {
            display_init_mode_004ae100(mode, arg2, g_str_tag_005d13f8);
        }
        if (g_val_00657c94 == 0) {
            g_val_005d1734 = 1;
            display_subsystem_004a8b80();
            return;
        }
        display_subsystem_004ae2b0();
        display_subsystem_004ab4b0();
        display_subsystem_00565890();
        heap_pool_block_free_00531f90(g_val_00655d44);
        g_val_00655d44 = nullptr;
        g_val_005d1734 = 0;
        return;
    }

    heap_pool_block_free_00531f90(g_val_00655d44);
    g_val_00655d44 = nullptr;
    g_val_00655d3c = 0;
    g_val_00657c9c = 0;
    g_val_00655d34 = 0;
    g_val_005d1734 = 0;
    g_val_00657c94 = 1;
    g_val_00657c98 = 3;
    g_val_00655d38 = 3;
}

// =============================================================================
// Function 3: 004b67b0 (303 bytes) - Pre-Simulation-Tick Loop Pipeline
// =============================================================================
void CALL_CDECL app_loop_pre_tick_pipeline_004b67b0() {
    PreTickTargetSubsystem* sub = g_ptr_0069ed0c;
    sub->handle_04->step_00536080();
    pipe_0044dfb0();
    pipe_0056a490();
    pipe_00516950();
    pipe_00413cf0();
    pipe_00427a60();
    phase_notify_004a4a70(1);
    phase_notify_004a4a70(2);
    pipe_00516950();
    g_val_00606ac0 = 0;
    g_val_00606ac4 = 0;
    pipe_004a4700();
    pipe_004b0d70();
    pipe_004affd0();
    pipe_004b0d70();
    pipe_004b0d70();
    pipe_00516950();
    pipe_004b0d70();
    pipe_00468fb0();
    phase_notify_004a4a70(4);
    phase_notify_004a4a70(5);
    pipe_004b0d70();
    pipe_00471b70();
    phase_notify_004a4a70(6);
    pipe_004b0d70();
    pipe_004a8cd0();
    pipe_004b0d70();
    phase_notify_004a4a70(7);
    pipe_004b0d70();
    pipe_00414db0();
    pipe_004b0d70();
    pipe_004690d0();
    pipe_004b0d70();
    pipe_00434a90();
    pipe_00424460();
    pipe_004b0d70();
    pipe_00415dc0();
    pipe_004b0fa0();
    pipe_004121b0();
    pipe_004b0fa0();
    std::uint32_t val = pipe_00569a90();
    heap_trace_log_005a177b(g_str_005d6e3c, val);

    InputSubsystem_303* input = g_input_subsystem_00628c70;
    if (input != nullptr && input->queue_08 != nullptr && input->flag_bf == 0) {
        input_poll_update_0048cdf0();
    }

    phase_notify_004a4a70(10);
    pipe_004b0fa0();
    pipe_0044df10(g_data_00657444);
    pipe_004691c0();
}

// =============================================================================
// Function 4: 004b4b80 (331 bytes) - Window / Engine Event Filter & Dispatcher
// =============================================================================
void CALL_CDECL window_event_filter_dispatch_004b4b80(const std::uint32_t* msg) {
    std::uint32_t msg_id = msg[0];

    if (msg_id >= 0x21e) {
        std::uint32_t arg1 = msg[1];
        std::uint32_t arg2 = msg[2];
        const EventRoutingEntry* route = g_event_routes_005d1e40;
        std::uint8_t* dest = nullptr;
        while (route->id != 0) {
            if (route->id == msg_id) {
                dest = route->destination_buffer;
            }
            route++;
        }
        if (dest != nullptr) {
            std::uint32_t offset = (arg1 * 11) << 7; // arg1 * 1408
            *reinterpret_cast<std::uint32_t*>(dest + offset) = arg2;
        }
        return;
    }

    if (msg_id >= 0x14e) {
        std::uint32_t param = msg[1];
        g_event_history_005e9130[msg_id] = param;
        std::uint32_t handler_idx = param & 0xff;
        auto fn = g_event_callbacks_005cc5d0[handler_idx].callback;
        if (fn != nullptr) {
            fn(static_cast<std::uint32_t>(static_cast<std::int32_t>(param) >> 8));
        }
        return;
    }

    const EventRoutingEntry* route = g_event_routes_005d1e40;
    std::uint8_t* dest = nullptr;
    while (route->id != 0) {
        if (route->id == msg_id) {
            dest = route->destination_buffer;
        }
        route++;
    }
    if (dest == nullptr) {
        return;
    }

    if (msg_id >= 0x142) {
        const std::uint32_t* src = msg + 1;
        if (msg_id >= 0x147) {
            std::uint32_t stride_idx = *src;
            dest += (stride_idx * 11) << 7;
            src++;
        }
        std::int32_t count = static_cast<std::int32_t>(*src);
        if (count > 0) {
            const std::uint32_t* items = src + 1;
            auto* out_words = reinterpret_cast<std::uint32_t*>(dest);
            for (std::int32_t i = 0; i < count; ++i) {
                out_words[i] = items[i];
            }
        }
        return;
    }

    if (msg_id >= 0x10e) {
        const std::uint32_t* src = msg + 1;
        if (msg_id >= 0x13a) {
            std::uint32_t stride_idx = *src;
            dest += (stride_idx * 11) << 7;
            src++;
        }
        const char* in_str = reinterpret_cast<const char*>(src);
        char* out_str = reinterpret_cast<char*>(dest);
        while (true) {
            char c = *in_str++;
            *out_str++ = c;
            if (c == '\0') {
                break;
            }
        }
        return;
    }

    // msg_id < 0x10e:
    *reinterpret_cast<std::uint32_t*>(dest) = msg[1];
}

// =============================================================================
// Function 5: 004b68f0 (337 bytes) - Post-Simulation-Tick Loop Pipeline
// =============================================================================
void CALL_CDECL app_loop_post_tick_pipeline_004b68f0() {
    pipe_004690f0();
    pipe_00516950();

    std::int32_t count = g_count_00658080;
    if (count > 0) {
        for (std::int32_t i = 0; i < count; ++i) {
            PostTickTargetObject* target = g_ptrs_005e8b34[i];
            PostTickSubObject* sub = target->sub_558;

            // Copy name_17c
            const char* s1 = sub->name_17c;
            char* d1 = target->name_b78;
            while (*s1 != '\0') {
                *d1++ = *s1++;
            }
            *d1 = '\0';

            target->field_b6c = sub->field_00;
            target->field_b70 = sub->field_08;
            target->field_b74 = target->field_52c;

            // Copy text_534
            const char* s2 = sub->text_534;
            char* d2 = target->text_bb8;
            while (*s2 != '\0') {
                *d2++ = *s2++;
            }
            *d2 = '\0';

            // Copy 150 dwords (600 bytes)
            std::uint32_t* dst_slot = &g_data_005e75a0[i * 150];
            const std::uint32_t* src_slot = target->payload_ad4;
            for (std::size_t j = 0; j < 150; ++j) {
                dst_slot[j] = src_slot[j];
            }
        }
    }

    pipe_00413fd0();
    pipe_004a8a80();
    pipe_004afe50();
    heap_trace_log_005a177b(g_str_005d6e68, 0);
    pipe_004a4760();
    pipe_00516950();
    pipe_00414f80();
    pipe_00471c40();
    pipe_004642f0();
    pipe_00425330();
    pipe_00412cd0();
    pipe_00412e60();
    heap_trace_log_005a177b(g_str_005d6e60, 0);
}

} // namespace porsche

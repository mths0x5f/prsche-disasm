#include "porsche/network_lifecycle.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/file_events.hpp"
#include "porsche/heap_locks.hpp"
#include "porsche/startup_services.hpp"
#include <cstring>

namespace porsche {
void* network_lifecycle_session_00628c74 = nullptr;
void* network_lifecycle_member_00628c7c = nullptr;
std::array<std::uint32_t, 8> network_lifecycle_callbacks_006b7c20{};

namespace {
using U = std::uint32_t;
U load(const void* p, U offset = 0) {
    U v; std::memcpy(&v, static_cast<const std::uint8_t*>(p) + offset, 4); return v;
}
void store(void* p, U offset, U value) {
    std::memcpy(static_cast<std::uint8_t*>(p) + offset, &value, 4);
}
std::uint8_t byte(const void* p, U offset) { return static_cast<const std::uint8_t*>(p)[offset]; }
void setbyte(void* p, U offset, std::uint8_t value) { static_cast<std::uint8_t*>(p)[offset] = value; }
void* pointer(U value) { return reinterpret_cast<void*>(static_cast<std::uintptr_t>(value)); }
U address(const void* p) { return static_cast<U>(reinterpret_cast<std::uintptr_t>(p)); }
std::int32_t signed_bits(U value) { std::int32_t v; std::memcpy(&v, &value, 4); return v; }

// Original manager pointer is reloaded for each node. The pool pointer is
// then captured across enter/leave, while its mutable lock and head reread.
void recycle(void* pool, void* node, U offset) {
    heap_enter_005322b0(pointer(load(pool)));
    store(node, 4, load(pool, offset));
    store(pool, offset, address(node));
    heap_leave_005322c0(pointer(load(pool)));
}
void recycle_list(void* object, U offset, U pool_offset) {
    void* head = pointer(load(object, offset));
    void* node = pointer(load(head));
    while (node != head) {
        auto* pool = static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8()) + 0x28;
        void* old = node;
        node = pointer(load(node));
        recycle(pool, old, pool_offset);
        head = pointer(load(object, offset));
    }
    head = pointer(load(object, offset));
    store(head, 0, address(head));
    head = pointer(load(object, offset));
    store(head, 4, address(head));
    // Reload manager after resetting the sentinel, as in the original.
    auto* pool = static_cast<std::uint8_t*>(application_context_heap_state_005e4fe8()) + 0x28;
    recycle(pool, pointer(load(object, offset)), pool_offset);
}
}

// 00560180..005601a6. First match only; callback 0 still matches an empty
// slot. No compaction or callback invocation occurs.
void __cdecl network_lifecycle_remove_callback_00560180(U callback_va) {
    for (auto& slot : network_lifecycle_callbacks_006b7c20) {
        if (slot == callback_va) { slot = 0; return; }
    }
}

// 004935c0..00493711. The two circular lists recycle their nodes and their
// sentinels into different original size-class heads (+10 and +14).
void __fastcall application_network_member_destroy_004935c0(void* receiver, void*) {
    heap_enter_005322b0(pointer(load(receiver, 0x14)));
    network_lifecycle_unregister_00561110(0x00493320u);
    if (load(receiver, 0x1c) != 0) {
        network_lifecycle_device_stop_00561b50();
        free_00531f90(pointer(load(receiver, 0x1c)));
    }
    if (byte(receiver, 0x10) != 0) {
        network_lifecycle_device_cancel_00561730(load(receiver, 8));
        setbyte(receiver, 0x10, 0);
    }
    network_lifecycle_device_release_005617d0(load(receiver, 8));
    free_00531f90(pointer(load(receiver, 0x20)));
    network_lifecycle_member_00628c7c = nullptr;
    heap_leave_005322c0(pointer(load(receiver, 0x14)));
    heap_lock_destroy_005322d0(pointer(load(receiver, 0x14)));
    recycle_list(receiver, 4, 0x10);
    recycle_list(receiver, 0, 0x14);
}

// 0048e9c0..0048eb1a. The global network used to send B1 can differ from
// receiver; the original dereferences it even on its null-rejection path.
std::uint32_t __fastcall network_lifecycle_reset_0048e9c0(void* receiver, void*) {
    if (byte(receiver, 0xc7) != 0) {
        network_lifecycle_close_transport_0048c580();
        setbyte(receiver, 0xc7, 0);
    }
    if (byte(receiver, 0xc2) != 0) {
        if (load(receiver, 0x28) != 2) {
            auto* global = startup_network_00628c70;
            U destination = 0xfffffffeu;
            if (global && load(global, 8) != 0 && byte(global, 0xbf) == 0)
                destination = load(global, 0xdc);
            application_network_message_0048c870(pointer(load(global, 0xc)), nullptr,
                0xb1, destination, 0x80000000u, 0, 0);
            network_lifecycle_wait_0053c380(signed_bits(timer_rate_005deb48) / 2);
        }
        network_lifecycle_stop_session_00492260();
    }
    void* member = pointer(load(receiver, 0x14));
    if (member) {
        application_network_member_destroy_004935c0(member, nullptr);
        application_release_0059f050(member);
        store(receiver, 0x14, 0);
    }
    void* cell = pointer(load(receiver, 0x10));
    heap_enter_005322b0(pointer(load(cell)));
    setbyte(receiver, 0xc3, 1);
    heap_leave_005322c0(pointer(load(cell)));
    if (byte(receiver, 0x106) != 0) {
        network_lifecycle_remove_callback_00560180(0x0048ee90u);
        setbyte(receiver, 0x106, 0);
    }
    void* message = pointer(load(receiver, 0xc));
    if (message) {
        application_release_0059f050(message);
        store(receiver, 0xc, 0);
    }
    void* connection = pointer(load(receiver, 8));
    if (connection) {
        network_lifecycle_connection_destroy_0048aed0(connection, nullptr);
        application_release_0059f050(connection);
        store(receiver, 8, 0);
    }
    if (byte(receiver, 0xc2) != 0) {
        void* session = network_lifecycle_session_00628c74;
        if (session) {
            network_lifecycle_session_destroy_00491fc0(session, nullptr);
            application_release_0059f050(session);
            network_lifecycle_session_00628c74 = nullptr;
        }
    }
    network_lifecycle_clear_lists_0048e790(receiver, nullptr);
    store(receiver, 0x24, 0);
    setbyte(receiver, 0xc0, 0); setbyte(receiver, 0xc6, 0); setbyte(receiver, 0xbf, 0);
    store(receiver, 0xe0, 0); setbyte(receiver, 0xc2, 0);
    const U tick = network_lifecycle_tick_count_0048a9a0() << 5u;
    store(receiver, 0x1c, tick);
    return tick;
}
void __fastcall application_network_reset_0048e9c0(void* receiver, void*) {
    (void)network_lifecycle_reset_0048e9c0(receiver, nullptr);
}
} // namespace porsche

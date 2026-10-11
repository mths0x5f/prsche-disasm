#include "porsche/context_effects.hpp"
#include <cstring>

namespace porsche {
namespace {
using U = std::uint32_t;
U load(const void* base, U offset) {
    U value; std::memcpy(&value, reinterpret_cast<const void*>(
        reinterpret_cast<U>(base) + offset), 4); return value;
}
void store(void* base, U offset, U value) {
    std::memcpy(reinterpret_cast<void*>(reinterpret_cast<U>(base) + offset), &value, 4);
}
void* pool(U mode) {
    return reinterpret_cast<void*>(reinterpret_cast<U>(application_context_heap_state_005e4fe8())
        - mode * 140u + 0x28u);
}
void pooled_release(void* state, void* block, U bytes) {
    heap_enter_005322b0(reinterpret_cast<void*>(load(state, 0)));
    const U offset = ((bytes - 1u) >> 3u) * 4u + 0xcu;
    store(block, 4, load(state, offset));
    store(state, offset, reinterpret_cast<U>(block));
    heap_leave_005322c0(reinterpret_cast<void*>(load(state, 0)));
}
}

// 0059ecb0..0059ecca: current manager +4 is the allocation callback.
void* __cdecl application_context_member_block_0059ecb0(U bytes, U heap, U source_va) {
    using Allocate = void* (__cdecl*)(const char*, U, U);
    void* state = application_context_heap_state_005e4fe8();
    const auto allocate = reinterpret_cast<Allocate>(load(state, 4));
    return allocate(reinterpret_cast<const char*>(source_va), bytes, heap);
}

// 0059ecd0..0059ecdf: current manager +8 is the release callback.
void __cdecl context_table_release_0059ecd0(void* block) {
    using Release = void (__cdecl*)(void*);
    void* state = application_context_heap_state_005e4fe8();
    reinterpret_cast<Release>(load(state, 8))(block);
}

// 004211d0..0042125d: unsigned size test; zero retains the original
// wrapped size-class arithmetic rather than receiving a synthetic guard.
void* __cdecl application_context_member_storage_004211d0(U bytes, U mode) {
    void* state = pool(mode);
    if (bytes > 0x100u) {
        // The selector accessor loads the pointer's value. Mode subtraction
        // must happen before that value load, so use the actual pointer cell.
        void* selector = context_selector_pointer_005e4fec();
        return application_context_member_block_0059ecb0(bytes,
            load(selector, 0u - mode * 4u), 0x005cbdb4u);
    }
    heap_enter_005322b0(reinterpret_cast<void*>(load(state, 0)));
    const U kind = (bytes - 1u) >> 3u;
    const U offset = kind * 4u + 0xcu;
    if (load(state, offset) == 0) {
        (void)application_context_new_head_0059eeb0(kind, mode);
    }
    void* block = reinterpret_cast<void*>(load(state, offset));
    store(state, offset, load(block, 4));
    heap_leave_005322c0(reinterpret_cast<void*>(load(state, 0)));
    return block;
}

void __cdecl application_context_clear_004237d0(void* block, U bytes, U mode) {
    void* state = pool(mode);
    if (bytes > 0x100u) { context_table_release_0059ecd0(block); return; }
    pooled_release(state, block, bytes);
}

void __cdecl application_context_member_destroy_block_00441200(void* block, U bytes) {
    void* state = pool(0);
    if (bytes > 0x100u) { context_table_release_0059ecd0(block); return; }
    pooled_release(state, block, bytes);
}

void __cdecl context_free_00424000(void* block, U bytes) {
    if (bytes == 0) return;
    void* state = pool(0);
    if (bytes > 0x100u) { context_table_release_0059ecd0(block); return; }
    pooled_release(state, block, bytes);
}

// 005262e0..00526344: child before sibling; sibling captured after child
// callback and before range release. Manager reloaded on every node.
void __fastcall application_context_unlink_005262e0(void* root, void*, U key) {
    void* node = reinterpret_cast<void*>(key);
    while (node) {
        application_context_unlink_005262e0(root, nullptr, load(node, 0xc));
        void* range = reinterpret_cast<void*>(load(node, 0x10));
        const U sibling = load(node, 8);
        if (range) context_free_00424000(range, load(node, 0x18) - reinterpret_cast<U>(range));
        void* state = pool(0);
        heap_enter_005322b0(reinterpret_cast<void*>(load(state, 0)));
        store(node, 4, load(state, 0x18));
        store(state, 0x18, reinterpret_cast<U>(node));
        heap_leave_005322c0(reinterpret_cast<void*>(load(state, 0)));
        node = reinterpret_cast<void*>(sibling);
    }
}
}

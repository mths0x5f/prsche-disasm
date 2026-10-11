#include "porsche/context_ranges.hpp"
#include <cstring>

namespace porsche {
namespace {
using U = std::uint32_t;
U load(U address) { U value; std::memcpy(&value, reinterpret_cast<void*>(address), 4); return value; }
void store(U address, U value) { std::memcpy(reinterpret_cast<void*>(address), &value, 4); }
U manager() { return reinterpret_cast<U>(application_context_heap_state_005e4fe8()); }
void release_pool(U state, U block, U bytes) {
    heap_enter_005322b0(reinterpret_cast<void*>(load(state)));
    const U offset = 0xcu + ((bytes - 1u) >> 3u) * 4u;
    store(block + 4u, load(state + offset));
    store(state + offset, block);
    heap_leave_005322c0(reinterpret_cast<void*>(load(state)));
}
}

// 00529c20 captures second.words[0] before its two forward-copy calls.
void __cdecl application_context_compare_ranges_00529c20(
    ApplicationContextRange16 first, ApplicationContextRange16 second, U) {
    const U captured_last = second.words[0];
    ApplicationContextRange16 second_copy, first_copy;
    application_context_copy_range_005299d0(&second_copy, nullptr, &second);
    application_context_copy_range_005299d0(&first_copy, nullptr, &first);
    context_range_walk_00529c50(first_copy, second_copy, captured_last);
}

#if !defined(CONTEXT_RANGES_EXTERNAL_WALK)
// 00529c50 performs the original iterator traversal, including node loads
// on exact end equality. It writes no memory and has no EAX return contract.
void __cdecl context_range_walk_00529c50(
    ApplicationContextRange16 first, ApplicationContextRange16 last, U) {
    U current = first.words[0];
    const U target = last.words[0];
    if (current == target) return;
    U end = first.words[2], node = first.words[3];
    do {
        current += 4u;
        if (current == end) {
            // Keep the original reads even though traversal has no stores or
            // return value. Win32 x86 supports the source's DWORD access.
            current = *reinterpret_cast<volatile const U*>(node + 4u);
            node += 4u;
            end = current + 0x200u;
        }
    } while (current != target);
}
#endif

// 004e4560: scalar deleting destructor; +8 is captured before callbacks.
void* __fastcall application_context_release_node_004e4560(
    void* member, void*, U flags) {
    const U object = reinterpret_cast<U>(member);
    const U block = load(object), bytes = load(object + 8u) - block;
    if (block && bytes) {
        const U state = manager() + 0x28u;
        if (bytes > 0x100u) context_table_release_0059ecd0(reinterpret_cast<void*>(block));
        else release_pool(state, block, bytes);
    }
    if (flags & 1u) (void)application_release_0059f050(member);
    return member;
}

// 004d7da0: count-zero test precedes a wrapping multiply by 32. There is
// deliberately no synthetic test for a zero result after that multiply.
void __cdecl application_context_notify_node_004d7da0(void* block, U count) {
    if (count == 0) return;
    const U bytes = count << 5u;
    const U state = manager() + 0x28u;
    if (bytes > 0x100u) context_table_release_0059ecd0(block);
    else release_pool(state, reinterpret_cast<U>(block), bytes);
}

// 0059eeb0: refill using existing page lists or a fixed 4096-byte request.
// Page-size global controls subdivision, independently of allocation size.
void __cdecl application_context_new_head_0059eeb0(U kind, U mode) {
    const U state = manager() - 140u * mode + 0x28u;
    heap_enter_005322b0(reinterpret_cast<void*>(load(state)));
    const U available_page = load(state + 4u);
    const U page_size = application_page_size_006af3f8;
    const U stride = kind * 8u + 8u;
    if (!available_page) {
        const U primary = manager() + 0x28u;
        const U selector = application_context_heap_selector_005e4fec();
        heap_enter_005322b0(reinterpret_cast<void*>(load(primary)));
        const U page = reinterpret_cast<U>(application_context_member_block_0059ecb0(
            0x1000u, selector, 0x005e5064u));
        store(page + 4u, load(primary + 4u));
        const U lock = load(primary);
        store(primary + 4u, page);
        heap_leave_005322c0(reinterpret_cast<void*>(lock));
    }
    U page = load(state + 4u);
    const U prior_used = load(state + 8u);
    const U next_page = load(page + 4u);
    store(state + 4u, next_page);
    store(page + 4u, prior_used);
    store(state + 8u, page);
    const U blocks = (page_size - 8u) / stride;
    page += 8u;
    for (U i = 0; i != blocks; ++i) {
        store(page + 4u, load(state + 0xcu + kind * 4u));
        store(state + 0xcu + kind * 4u, page);
        page += stride;
    }
    heap_leave_005322c0(reinterpret_cast<void*>(load(state)));
}
}

#include "porsche/application_heap_state.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/application_heap_init.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_main.hpp"
#include "porsche/application_pool.hpp"
#include "porsche/context_effects.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/heap.hpp"
#include "porsche/install_paths.hpp"

namespace porsche {
ApplicationHeapRuntime application_heap_runtime{};
// These casts produce static DIR32 data relocations with MSVC x86, not dynamic
// initialization. Seven default slots must share the same zero-body address.
ApplicationHeapContexts application_heap_contexts{
    {{reinterpret_cast<std::uint32_t>(application_heap_runtime.selectors),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0),
      reinterpret_cast<std::uint32_t>(&application_heap_identity_0059e9b0),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0), 0,
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0),
      reinterpret_cast<std::uint32_t>(&application_heap_zero_0059e9c0)}, {}},
    {{reinterpret_cast<std::uint32_t>(application_heap_runtime.selectors),
      reinterpret_cast<std::uint32_t>(&application_allocator_entry_00531f70),
      reinterpret_cast<std::uint32_t>(&free_00531f90),
      reinterpret_cast<std::uint32_t>(&resize_00569640),
      reinterpret_cast<std::uint32_t>(&application_heap_block_005aef20), 0,
      reinterpret_cast<std::uint32_t>(&install_paths_size_00556640),
      reinterpret_cast<std::uint32_t>(&heap_name_00556650),
      reinterpret_cast<std::uint32_t>(&application_heap_tag_00556680),
      reinterpret_cast<std::uint32_t>(&application_heap_measure_00569ad0)}, {}},
    &application_heap_contexts.defaults, application_heap_runtime.selectors
};
std::uint32_t& application_page_size_006af3f8 = application_heap_runtime.page;
std::uint8_t& application_heap_initialized_006af3f4 = application_heap_runtime.initialized;
void*& application_primary_arena_006af3b4 = application_heap_runtime.primary_arena;
std::int32_t& application_object_heap_006af3fc = application_heap_runtime.object_heap;
std::uint8_t (&application_heap_records)[0x8c0] = application_heap_contexts.live.records;
void* (&application_queue_indices)[16] = application_heap_runtime.selectors;
void* (&application_other_arenas_006af3b8)[15] = application_heap_runtime.other_arenas;

void* __cdecl application_heap_identity_0059e9b0(void* value, std::int32_t) {
    return value;
}
std::uint32_t __cdecl application_heap_zero_0059e9c0(...) { return 0; }
void* application_context_heap_state_005e4fe8() { return application_heap_contexts.current; }
void* context_selector_pointer_005e4fec() { return application_heap_contexts.selectors; }
std::uint32_t application_context_heap_selector_005e4fec() {
    return application_heap_load(application_heap_contexts.selectors);
}

// 0059eb20..0059ebbe. The accepted Run311 JMP wrapper owns 004a54e0.
// Both selector and object-ID reloads after callbacks are observable.
void __cdecl application_heap_shutdown_0059eb20() {
    if (!application_heap_initialized_006af3f4) return;
    application_pool_shutdown_005678f0();
    application_heap_secondary_stop_0055ec30();
    const auto id = static_cast<std::uint32_t>(application_object_heap_006af3fc);
    auto* selector = static_cast<void*>(application_heap_contexts.selectors);
    for (std::uint32_t i = 0; i != 16; ++i) {
        if (application_heap_load(application_heap_address(selector, i * 4u)) == id) {
            application_heap_queue_clean_0059ee30(0u - i);
            application_heap_store(application_heap_address(application_heap_contexts.selectors,
                i * 4u), 0);
            break;
        }
    }
    (void)application_heap_destroy_005699f0(id);
    auto* arena = application_heap_pointer(application_heap_load(application_heap_arena_cell(id)));
    (void)application_virtual_free(arena, 0, 0x8000);
    const auto reloaded_id = static_cast<std::uint32_t>(application_object_heap_006af3fc);
    application_heap_store(application_heap_arena_cell(id), 0);
    application_primary_arena_006af3b4 = nullptr;
    application_heap_contexts.current = &application_heap_contexts.defaults;
    application_heap_store(application_heap_arena_cell(reloaded_id), 0);
}
void __cdecl platform_flush_0059eb20() { application_heap_shutdown_0059eb20(); }
}

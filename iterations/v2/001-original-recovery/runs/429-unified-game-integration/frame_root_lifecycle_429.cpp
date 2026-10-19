// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Run 429: corrected copy of Run 419's frame root lifecycle (00471b70, 00471c40).
//  - Storage: 00628940/00628960/00628964 now come from frame_root_block_429.asm,
//    one block 00628940..00628a64 with the original offsets. The old section
//    "pfroot" placed the path buffer 8 bytes after the root instead of 4 (upstream
//    review of PR 19). The block also keeps the unbounded track-name copy and the
//    "%s%s%s" path inside original memory: the path buffer is not a 256-byte
//    object in the original, since 006289e4..00628a20 are other cells.
//  - Callees with a canonical owner use it instead of a new C name for the same
//    VA: 0059ef90, 0059f050 (application_alloc.hpp), 005a0fbf (formatter_entry.hpp),
//    005a177b (formatter_stdio.hpp), and the 005e8e50 string (application_heap_init.hpp).
//    The rest (0059fd90, 005323a0, 00657444, 0065b2b8, 00628bc0) has no recovered
//    owner and stays an explicit boundary.
#include "../419-frame-root-lifecycle/frame_root_lifecycle_419.hpp"

#include <cstdint>
#include <cstddef>

#include "porsche/application_alloc.hpp"
#include "porsche/application_heap_init.hpp"
#include "porsche/formatter_entry.hpp"
#include "porsche/formatter_stdio.hpp"

namespace porsche {

// Unrecovered callees and cells (no canonical owner yet).
extern "C" {
    extern const char g_track_source_name_00657444[64];
    extern const char* g_path_prefix_0065b2b8;
    extern void* g_bworld_context_00628bc0;
    void __cdecl error_log_0059fd90(const char* format, const char* name);
    float __cdecl bworld_init_subsystem_005323a0(void* p1, void* p2);
}

// 00471b70 (198 bytes): BWorld_Init
void __cdecl frame_root_init_00471b70() {
    // 00471b72..00471b97: repne scasb + rep movsd/movsb from 00657444 to 00628940.
    // The original copy has no bound, and upstream Run 301 proved a source of 32
    // bytes or more reaches the root cell and then the following buffer. Because
    // the three objects are one contiguous block here, that effect is reproduced
    // instead of being lost; it is deliberate, not an oversight.
    const char* src = g_track_source_name_00657444;
    char* dst = g_frame_root_track_name_00628940;
    while (*src != '\0') {
        *dst++ = *src++;
    }
    *dst = '\0';

    // 00471b99: operator new(0x3c)
    void* mem = startup_network_allocate_0059ef90(0x3c);
    void* root = nullptr;
    if (mem != nullptr) {
        // 00471ba9: construct object via 004874a0
        auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(mem);
        root = proxy->construct_004874a0();
        frame_service_root_00628960 = reinterpret_cast<std::uint32_t>(root);
    } else {
        frame_service_root_00628960 = 0;
    }

    // 00471bbf..00471bda: format path "%s%s%s" into 00628964
    formatter_entry_005a0fbf(
        g_frame_root_formatted_path_00628964,
        "%s%s%s",
        g_path_prefix_0065b2b8,
        g_frame_root_track_name_00628940,
        application_object_heap_name_005e8e50
    );

    // 00471bdf..00471bed: load track
    root = reinterpret_cast<void*>(frame_service_root_00628960);
    auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(root);
    std::uint8_t ok = proxy->load_track_004876e0(g_frame_root_formatted_path_00628964);
    if (!ok) {
        // 00471bf6..00471c05: push 00657444, push 005cfe84 (the full format string)
        error_log_0059fd90("ERROR - Couldn't load track: '%s'\n", g_track_source_name_00657444);
    }

    // 00471c08..00471c21: the original reads [00628bc0] and its +0 and +0x0c
    // fields with no null check, then calls 005323a0(+0x0c + 4, +0 * 80 + +0x0c - 0x4c).
    auto* bworld_ctx = reinterpret_cast<std::uint32_t*>(g_bworld_context_00628bc0);
    const std::uint32_t val3 = bworld_ctx[3];
    const std::uint32_t val0 = bworld_ctx[0];
    const std::uint32_t p2 = ((val0 * 5u) << 4) + val3 - 0x4cu;
    const std::uint32_t p1 = val3 + 4u;
    // 00471c2b: the caller pops the x87 value 005323a0 leaves in ST0 (fstp st(0)).
    // Only that pop is proven; the float type is the narrowest return that makes
    // the compiler emit it.
    static_cast<void>(bworld_init_subsystem_005323a0(reinterpret_cast<void*>(p1), reinterpret_cast<void*>(p2)));

    // 00471c26..00471c32: trace log "...done Init BWorld.\n"
    formatter_stdio_printf_005a177b("...done Init BWorld.\n");
}

// 00471c40 (65 bytes): BWorld_DeInit
void __cdecl frame_root_teardown_00471c40() {
    // 00471c41..00471c46: trace log "BWorld_DeInit..."
    formatter_stdio_printf_005a177b("BWorld_DeInit...");

    // 00471c4b..00471c65: destruct and free root object if present
    void* root = reinterpret_cast<void*>(frame_service_root_00628960);
    if (root != nullptr) {
        auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(root);
        proxy->destruct_00487590();
        application_release_0059f050(root);
    }

    // 00471c68..00471c77: clear 00628960 and log "done.\n"
    frame_service_root_00628960 = 0;
    formatter_stdio_printf_005a177b("done.\n");
}

} // namespace porsche

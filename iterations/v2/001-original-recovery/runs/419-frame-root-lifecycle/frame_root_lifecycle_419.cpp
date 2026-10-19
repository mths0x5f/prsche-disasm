#include "frame_root_lifecycle_419.hpp"

#include <cstdint>
#include <cstddef>

namespace porsche {

// Contiguous layout in writable memory matching .data
#pragma pack(push, 1)
struct FrameRootStorageLayout {
    char track_name_00628940[32];
    void* service_root_00628960;
    char formatted_path_00628964[256];
};
#pragma pack(pop)

static FrameRootStorageLayout g_storage_layout;

char g_frame_root_track_name_00628940[32];
void* g_frame_service_root_00628960 = nullptr;
char g_frame_root_formatted_path_00628964[256];

// External callee prototypes matching the original binary
extern "C" {
    extern const char g_track_source_name_00657444[64];
    extern const char* g_path_prefix_0065b2b8;
    extern const char g_default_sound_device_005e8e50[32];
    extern void* g_bworld_context_00628bc0;

    void* __cdecl memory_allocate_0059ef90(std::uint32_t size);
    int __cdecl string_format_005a0fbf(char* dest, const char* fmt, ...);
    void __cdecl error_log_0059fd90(const char* prefix, const char* name);
    void __cdecl bworld_init_subsystem_005323a0(void* p1, void* p2);
    void __cdecl trace_log_005a177b(const char* msg, ...);
    void __cdecl memory_free_0059f050(void* ptr);
}

// 00471b70 (198 bytes): BWorld_Init
void __cdecl frame_root_init_00471b70() {
    // 00471b72..00471b97: repne scasb + rep movsd/movsb from 00657444 to 00628940
    const char* src = g_track_source_name_00657444;
    char* dst = g_frame_root_track_name_00628940;
    while (*src != '\0') {
        *dst++ = *src++;
    }
    *dst = '\0';

    // 00471b99: operator new(0x3c)
    void* mem = memory_allocate_0059ef90(0x3c);
    void* root = nullptr;
    if (mem != nullptr) {
        // 00471ba9: construct object via 004874a0
        auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(mem);
        root = proxy->construct_004874a0();
        g_frame_service_root_00628960 = root;
    } else {
        g_frame_service_root_00628960 = nullptr;
    }

    // 00471bbf..00471bda: format path "%s%s%s" into 00628964
    string_format_005a0fbf(
        g_frame_root_formatted_path_00628964,
        "%s%s%s",
        g_path_prefix_0065b2b8,
        g_frame_root_track_name_00628940,
        g_default_sound_device_005e8e50
    );

    // 00471bdf..00471bed: load track
    root = g_frame_service_root_00628960;
    auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(root);
    std::uint8_t ok = proxy->load_track_004876e0(g_frame_root_formatted_path_00628964);
    if (!ok) {
        // 00471bf6..00471c05: report error "ERROR - Couldn't load track: '"
        error_log_0059fd90("ERROR - Couldn't load track: '", g_track_source_name_00657444);
    }

    // 00471c08..00471c21: compute offsets from 00628bc0 and call 005323a0
    auto* bworld_ctx = reinterpret_cast<std::uint32_t*>(g_bworld_context_00628bc0);
    if (bworld_ctx != nullptr) {
        std::uint32_t val0 = bworld_ctx[0];
        std::uint32_t val3 = bworld_ctx[3]; // offset +0x0c
        std::uint32_t p1 = val3 + 4;
        std::uint32_t p2 = (val0 * 5) << 4; // val0 * 80
        p2 = p2 + val3 - 0x4c;
        bworld_init_subsystem_005323a0(reinterpret_cast<void*>(p1), reinterpret_cast<void*>(p2));
    }

    // 00471c26..00471c32: trace log "...done Init BWorld.\n"
    trace_log_005a177b("...done Init BWorld.\n");
}

// 00471c40 (65 bytes): BWorld_DeInit
void __cdecl frame_root_teardown_00471c40() {
    // 00471c41..00471c46: trace log "BWorld_DeInit..."
    trace_log_005a177b("BWorld_DeInit...");

    // 00471c4b..00471c65: destruct and free root object if present
    void* root = g_frame_service_root_00628960;
    if (root != nullptr) {
        auto* proxy = reinterpret_cast<FrameServiceObjectProxy*>(root);
        proxy->destruct_00487590();
        memory_free_0059f050(root);
    }

    // 00471c68..00471c77: clear 00628960 and log "done.\n"
    g_frame_service_root_00628960 = nullptr;
    trace_log_005a177b("done.\n");
}

} // namespace porsche

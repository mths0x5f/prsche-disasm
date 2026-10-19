#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// Original global storage layout:
// 00628940: buffer preceding root (holds copied track name string, 32 bytes)
// 00628960: root pointer cell (single 32-bit pointer)
// 00628964: buffer following root (holds formatted string "%s%s%s", e.g. path)
extern char g_frame_root_track_name_00628940[32];
extern void* g_frame_service_root_00628960;
extern char g_frame_root_formatted_path_00628964[256];

struct FrameServiceObjectProxy {
    void* __thiscall construct_004874a0();
    std::uint8_t __thiscall load_track_004876e0(const char* path);
    void __thiscall destruct_00487590();
};

// 00471b70 (198 bytes): BWorld_Init / frame root lifecycle initializer
// Copies track name string from 00657444 to 00628940, allocates 0x3c bytes for root,
// constructs it via 004874a0, formats path, and initializes BWorld.
void __cdecl frame_root_init_00471b70();

// 00471c40 (65 bytes): BWorld_DeInit / frame root lifecycle teardown
// Logs "BWorld_DeInit...", destructs root via 00487590, frees it via 0059f050,
// zeroes 00628960, and logs "done.".
void __cdecl frame_root_teardown_00471c40();

// Alias for startup_sequence / game link
inline void __cdecl startup_sequence_call_00471b70() {
    frame_root_init_00471b70();
}

inline void __cdecl pipe_00471c40() {
    frame_root_teardown_00471c40();
}

} // namespace porsche

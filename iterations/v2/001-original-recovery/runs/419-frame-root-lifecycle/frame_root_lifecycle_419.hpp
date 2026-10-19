#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// Original global storage at 00628940..00628a63, recovered as ONE contiguous
// block so the adjacency the original relies on is real rather than described:
//   00628940  char[32]        buffer preceding the root (copied track name)
//   00628960  uint32_t        the root pointer cell itself
//   00628964  char[256]       buffer following the root (formatted "%s%s%s")
//
// The root cell is `frame_service_root_00628960`, the exact symbol Run 290's
// frozen frame_service_290.hpp declares, so the Run 290 consumer 00471b60
// reads the same object that 00471b70 writes. Do not introduce a second cell
// for this address: upstream Run 296 showed that a standalone pointer loses
// the shared memory relationship, and upstream Run 301 showed the preceding
// copy can reach this cell.
//
// The three objects are placed in one writable section in declaration order.
// That placement is a toolchain property, not a language guarantee, so the
// native fixture asserts the 0/32/36 offsets before any behavioural case runs.
extern char g_frame_root_track_name_00628940[32];
extern std::uint32_t frame_service_root_00628960;
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

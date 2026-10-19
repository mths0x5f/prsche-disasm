// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
#pragma once

#include <cstdint>

#include "porsche/application_audio_lifecycle.hpp"  // canonical audio backend declarations
#include "porsche/heap_locks.hpp"                   // platform_*_critical_section

namespace porsche {

// ---------------------------------------------------------------------------
// Audio backend lock: one Win32 CRITICAL_SECTION at 006b1800 plus a byte
// nesting counter at 006b499f.
//
// Storage boundaries: none of these cells is defined here. The counter sits 3
// bytes after audio_system_active_006b499c and 5 bytes before the channel
// count at 006b49a4, so the backend state looks like one block; defining loose
// cells before that layout is proven would repeat the 00628960 mistake.
// ---------------------------------------------------------------------------
extern std::uint8_t audio_backend_lock_cs_006b1800[24];   // CRITICAL_SECTION
extern std::uint8_t audio_backend_lock_depth_006b499f;    // nesting counter

// Pool header pointer written by 0058aa90 and read by 0058aac0.
extern std::uint32_t audio_backend_pool_006b4a18;

// Channel table read by 0058ff10: element count (signed 16-bit) and a pointer
// to an array of 0x70-byte records whose first dword is a channel handle.
extern std::int16_t audio_backend_channel_count_006b49a4;
extern std::uint32_t audio_backend_channels_006b4a00;

// Lock primitives over 006b1800. 0058e2d0 and 0058e2e0 are declared by the
// canonical application_audio_device.hpp under the names "start"/"stop"; the
// bodies are InitializeCriticalSection / DeleteCriticalSection.
void __cdecl audio_backend_enter_0058e2f0();   // EnterCriticalSection
void __cdecl audio_backend_leave_0058e300();   // LeaveCriticalSection

// Declared identically by Run 400's frame_loop_clusters_400.hpp.
void __cdecl audio_backend_lock_005896d0();
void __cdecl audio_backend_unlock_005896f0();

// Recovered in Run 400; 0058ff10 calls it once per channel record.
std::int32_t __cdecl audio_channel_stop_00565d60(std::uint32_t handle);

// Pool header fields that 0058aa90 writes, at base+0x00..+0x10. Only what the
// two recovered bodies prove is named; the pool algorithm itself is not here.
struct AudioBackendPoolHeader_421 {
    std::uint32_t first_aligned;   // +0x00  (base + 0x1b) & ~3
    std::uint32_t end_marker;      // +0x04  base + size - 8
    std::uint32_t size;            // +0x08  size passed to 0058aa90
    std::uint32_t limit;           // +0x0c  size - 3 - 0x20
    std::uint32_t cursor;          // +0x10  size - 3 at init
};
static_assert(sizeof(AudioBackendPoolHeader_421) == 0x14, "pool header prefix");

} // namespace porsche

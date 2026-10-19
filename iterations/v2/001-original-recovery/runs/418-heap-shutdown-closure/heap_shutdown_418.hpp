#pragma once

#include <cstdint>

#include "porsche/application_heap.hpp"
#include "porsche/application_heap_init.hpp"
#include "porsche/application_pool.hpp"
#include "porsche/file_events.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/file_worker.hpp"
#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
#include "porsche/network_workers_members.hpp"

namespace porsche {

extern std::uint32_t printf_initialized_006a57cc;
extern std::uint8_t default_heap_state_005e3e18[0x8e8];
extern void* heap_state_005e4fe8;
extern std::int32_t* heap_selector_005e4fec;

// 0055ec30 (20 bytes): clears 006a57cc when nonzero.
void __cdecl printf_shutdown_0055ec30();

// 005678f0 (248 bytes): drains 006a5c38, stops 32 FileDevice workers, frees pool arenas/queues/lock.
void __cdecl application_pool_shutdown_005678f0();

// 005699f0 (72 bytes): destroys lock at +0x38, zeroes 0x40-byte OriginalHeap, clears heaps_006b4f20[slot & 0xf].
std::int32_t __cdecl heap_destroy_slot_005699f0(std::uint32_t slot);

// 0059ee30 (124 bytes): merges +8 list into +4, invokes [005e4fe8]+8 on each node, zeroes 16 DWORDs at +0xc.
void __cdecl queue_drain_0059ee30(std::int32_t slot);

// 0059eb20 (159 bytes): full heap/pool/printf/queue/arena teardown guarded by 006af3f4.
void __cdecl platform_flush_0059eb20();

} // namespace porsche

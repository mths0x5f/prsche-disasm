#pragma once
#include <cstdint>

namespace porsche {

// Porsche.exe 00563ad0 owns these BSS words; consumers at 00563bd0..00563d30
// share the same storage. This header is the sole owner declaration.
extern void* async_pool_base_006a5bc0;
extern std::uint32_t async_pool_head_006a5bc8;
extern std::uint32_t async_pool_tail_006a5bcc;
extern void* async_pool_first_006a5bd0;
extern void* async_pool_last_006a5bd4;
extern std::uint32_t async_pool_priority_006a5bd8;
extern std::uint32_t async_pool_capacity_006a5be0;
extern std::uint32_t async_pool_active_006a5be4;
extern void* async_pool_lock_006a5be8;

// Original 00563bd0 is a separate, unrecovered scheduler callback.
std::uint32_t __cdecl async_pool_callback_00563bd0(std::uint32_t, std::uint32_t);
void __cdecl startup_subsystem_00563ad0(std::uint32_t count,
    std::uint32_t priority, std::uint32_t allocation_flags);

} // namespace porsche

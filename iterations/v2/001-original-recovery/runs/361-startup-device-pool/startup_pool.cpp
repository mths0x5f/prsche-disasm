#include "startup_pool.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/files.hpp"
#include "porsche/heap.hpp"
#include "porsche/shared_runtime_globals.hpp"
#include "porsche/window_scheduler.hpp"

#include <cstdint>

namespace porsche {

// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00563ad0..00563bca. The BSS allocation has no existing production owner.
static_assert(sizeof(void*) == 4, "original pool uses Win32 pointers");
void* async_pool_base_006a5bc0 = nullptr;
std::uint32_t async_pool_head_006a5bc8 = 0;
std::uint32_t async_pool_tail_006a5bcc = 0;
void* async_pool_first_006a5bd0 = nullptr;
void* async_pool_last_006a5bd4 = nullptr;
std::uint32_t async_pool_priority_006a5bd8 = 0;
std::uint32_t async_pool_capacity_006a5be0 = 0;
std::uint32_t async_pool_active_006a5be4 = 0;
void* async_pool_lock_006a5be8 = nullptr;

namespace {
void put(std::uintptr_t address, std::uint32_t value) {
    *reinterpret_cast<std::uint32_t*>(address) = value;
}
void diagnostic(std::uint32_t line,const char* message) {
    class_error_file_005deb74 = 0x005bcfa0u;
    class_error_line_005deb78 = line;
    diagnostic_handler_005debf0(message);
}
}

void __cdecl startup_subsystem_00563ad0(std::uint32_t count,
    std::uint32_t priority, std::uint32_t allocation_flags) {
    if (async_pool_base_006a5bc0) {
        diagnostic(0x21au,"initasync - already initialized\n");
        return;
    }
    if (static_cast<std::int32_t>(count) > 0x100) {
        diagnostic(0x220u,"initasync - too many async request blocks specified\n");
        return;
    }

    // ESI*44 is a wrapping x86 32-bit calculation. The original has no
    // count-zero or allocation-failure guard; callers use 30 at startup.
    const std::uint32_t bytes=count*44u;
    async_pool_priority_006a5bd8=priority;
    async_pool_capacity_006a5be0=count;
    auto* base=static_cast<std::uint8_t*>(
        allocate_00531ca0("ASYNCREQ",static_cast<std::int32_t>(bytes),allocation_flags));
    const auto address=reinterpret_cast<std::uintptr_t>(base);
    async_pool_base_006a5bc0=base;
    async_pool_first_006a5bd0=base;
    async_pool_last_006a5bd4=reinterpret_cast<void*>(address+bytes-44u);
    async_pool_head_006a5bc8=0;
    async_pool_tail_006a5bcc=0;
    async_pool_active_006a5be4=0;
    async_pool_lock_006a5be8=heap_lock_create_005321f0();

    for (std::uint32_t i=0;i<count && static_cast<std::int32_t>(i)<static_cast<std::int32_t>(count);++i) {
        const auto cell=address+i*44u;
        put(cell,i);
        put(cell+4u,static_cast<std::uint32_t>(cell+44u));
        put(cell+0x18u,0);
    }
    put(address+bytes-40u,0);
    (void)window_scheduler_register_005365e0(async_pool_callback_00563bd0,1,1);
}

} // namespace porsche

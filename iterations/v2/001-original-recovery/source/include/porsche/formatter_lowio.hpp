#pragma once
#include "porsche/formatter_bootstrap.hpp"
#include "porsche/exit_registry.hpp"
#include <cstddef>

namespace porsche {
struct FormatterLowioStartupInfo32 {
    std::uint8_t prefix[50];
    std::uint16_t reserved_bytes;
    const std::uint8_t* reserved;
    std::uint32_t standard_handles[3];
};
static_assert(offsetof(FormatterLowioStartupInfo32, reserved_bytes) == 50);
static_assert(offsetof(FormatterLowioStartupInfo32, reserved) == 52);
static_assert(sizeof(FormatterLowioStartupInfo32) == 68);

std::uint32_t __cdecl formatter_lowio_initialize_005a953e();
std::int32_t __cdecl formatter_lowio_allocate_005ab4c6();
std::int32_t __cdecl formatter_lowio_attach_005ab5e9(std::uint32_t, std::uint32_t handle);
std::int32_t __cdecl formatter_lowio_detach_005ab665(std::uint32_t);
std::uint32_t __cdecl formatter_lowio_handle_005ab6e4(std::uint32_t);
void __cdecl formatter_lowio_lock_005ab726(std::uint32_t);
void __cdecl formatter_lowio_unlock_005ab785(std::uint32_t);

// Original lowio OS and per-thread error boundaries remain explicit.
void __stdcall formatter_lowio_startup_info(FormatterLowioStartupInfo32*);
std::uint32_t __stdcall formatter_lowio_file_type(std::uint32_t handle);
std::uint32_t __stdcall formatter_lowio_get_standard(std::int32_t);
std::uint32_t __stdcall formatter_lowio_set_count(std::uint32_t);
int __stdcall formatter_lowio_set_standard(std::int32_t, std::uint32_t handle);
void __stdcall formatter_lowio_critical_initialize(void*);
void __stdcall formatter_lowio_critical_enter(void*);
void __stdcall formatter_lowio_critical_leave(void*);
std::int32_t* __cdecl formatter_lowio_errno_005a669e();
std::uint32_t* __cdecl formatter_lowio_doserrno_005a66a7();
} // namespace porsche

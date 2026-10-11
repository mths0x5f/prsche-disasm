#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/formatter_lowio.hpp"

namespace porsche {
// Exact original Kernel32 IAT identities: Run152 verification.json/iat_imports.
static_assert(sizeof(STARTUPINFOA)==sizeof(FormatterLowioStartupInfo32));
static_assert(offsetof(STARTUPINFOA,cbReserved2)==offsetof(FormatterLowioStartupInfo32,reserved_bytes));
static_assert(offsetof(STARTUPINFOA,lpReserved2)==offsetof(FormatterLowioStartupInfo32,reserved));
static_assert(offsetof(STARTUPINFOA,hStdInput)==offsetof(FormatterLowioStartupInfo32,standard_handles));
void __stdcall formatter_lowio_startup_info(FormatterLowioStartupInfo32* info) {
    ::GetStartupInfoA(reinterpret_cast<STARTUPINFOA*>(info));
}
std::uint32_t __stdcall formatter_lowio_file_type(std::uint32_t handle) {
    return ::GetFileType(reinterpret_cast<HANDLE>(handle));
}
std::uint32_t __stdcall formatter_lowio_get_standard(std::int32_t selector) {
    return reinterpret_cast<std::uint32_t>(::GetStdHandle(static_cast<DWORD>(selector)));
}
std::uint32_t __stdcall formatter_lowio_set_count(std::uint32_t count) {
    return ::SetHandleCount(count);
}
int __stdcall formatter_lowio_set_standard(std::int32_t selector,std::uint32_t handle) {
    return ::SetStdHandle(static_cast<DWORD>(selector),reinterpret_cast<HANDLE>(handle));
}
void __stdcall formatter_lowio_critical_initialize(void* lock) {
    ::InitializeCriticalSection(static_cast<CRITICAL_SECTION*>(lock));
}
void __stdcall formatter_lowio_critical_enter(void* lock) {
    ::EnterCriticalSection(static_cast<CRITICAL_SECTION*>(lock));
}
void __stdcall formatter_lowio_critical_leave(void* lock) {
    ::LeaveCriticalSection(static_cast<CRITICAL_SECTION*>(lock));
}
} // namespace porsche

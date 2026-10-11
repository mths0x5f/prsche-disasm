#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/formatter_text.hpp"

namespace porsche {
// Porsche.exe ddd748fdbe6d: exact Kernel32 IATs, Run157/158 reports.
static_assert(sizeof(void*) == 4 && sizeof(LONG) == sizeof(std::int32_t));
void* __stdcall formatter_crt_heap_allocate(std::uint32_t heap, std::uint32_t flags, std::uint32_t bytes) {
    return ::HeapAlloc(reinterpret_cast<HANDLE>(heap), flags, bytes); // 005b21dc
}
int __stdcall formatter_crt_heap_free(std::uint32_t heap, std::uint32_t flags, void* pointer) {
    return ::HeapFree(reinterpret_cast<HANDLE>(heap), flags, pointer); // 005b2098
}
std::uint32_t __stdcall formatter_crt_tls_allocate() { return ::TlsAlloc(); } // 005b212c
void* __stdcall formatter_crt_tls_get(std::uint32_t index) { return ::TlsGetValue(index); } // 005b2128
int __stdcall formatter_crt_tls_set(std::uint32_t index, void* value) { return ::TlsSetValue(index, value); } // 005b2124
std::uint32_t __stdcall formatter_crt_get_last_error() { return ::GetLastError(); } // 005b213c
void __stdcall formatter_crt_set_last_error(std::uint32_t value) { ::SetLastError(value); } // 005b21a4
std::uint32_t __stdcall formatter_crt_thread_id() { return ::GetCurrentThreadId(); } // 005b2074
std::int32_t __stdcall formatter_text_platform_increment(std::int32_t* value) {
    return ::InterlockedIncrement(reinterpret_cast<LONG*>(value)); // 005b2258
}
std::int32_t __stdcall formatter_text_platform_decrement(std::int32_t* value) {
    return ::InterlockedDecrement(reinterpret_cast<LONG*>(value)); // 005b2254
}
}

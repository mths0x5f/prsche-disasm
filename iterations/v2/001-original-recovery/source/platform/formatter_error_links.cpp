#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/formatter_bootstrap.hpp"
#include "porsche/formatter_strings.hpp"
#include "porsche/exit_registry.hpp"
#include <cstring>

namespace porsche {
// Original IAT005b2050/005b205c: preserve lazy library/symbol resolution.
void* __stdcall formatter_dialog_load_library(const char* name) {
    return ::LoadLibraryA(name);
}
void* __stdcall formatter_dialog_get_proc_address(void* module,const char* name) {
    return reinterpret_cast<void*>(::GetProcAddress(static_cast<HMODULE>(module),name));
}
// Original IAT005b2064/005b20e4/005b21f0, respectively; preserve BOOL/DWORD.
std::uint32_t __stdcall formatter_error_module_name(void* module,char* name,
    std::uint32_t capacity) {
    return ::GetModuleFileNameA(static_cast<HMODULE>(module),name,capacity);
}
void* __stdcall formatter_error_std_handle(std::int32_t selector) {
    return ::GetStdHandle(static_cast<DWORD>(selector));
}
int __stdcall formatter_error_write_file(void* handle,const void* data,
    std::uint32_t bytes,std::uint32_t* written,void* overlapped) {
    static_assert(sizeof(DWORD)==sizeof(std::uint32_t));
    return ::WriteFile(static_cast<HANDLE>(handle),data,bytes,
        reinterpret_cast<DWORD*>(written),static_cast<OVERLAPPED*>(overlapped));
}
void __cdecl exit_registry_fatal_005a2e22(std::uint32_t message) {
    int value;std::memcpy(&value,&message,sizeof value);
    formatter_fatal_005a2e22(value);
}
} // namespace porsche

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/render_loader.hpp"
#include "porsche/formatter_strings.hpp"
#include "porsche/window_create.hpp"
#include "porsche/file_events.hpp"
#include <cstdint>

static_assert(sizeof(void*)==4,"Original renderer import transport is x86");
namespace porsche {
std::uint32_t __cdecl render_win_load_library_005b2050(const char* name){
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(formatter_dialog_load_library(name)));
}
std::uint32_t __cdecl render_win_get_proc_005b205c(std::uint32_t module,const char* name){
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(
        formatter_dialog_get_proc_address(reinterpret_cast<void*>(static_cast<std::uintptr_t>(module)),name)));
}
void __cdecl render_win_free_library_005b2088(std::uint32_t module){
    (void)::FreeLibrary(reinterpret_cast<HMODULE>(static_cast<std::uintptr_t>(module)));
}
std::uint32_t __cdecl render_win_get_module_005b2138(const char* name){
    return static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(window_module_handle(name)));
}
void __cdecl render_win_disable_thread_calls_005b21b4(std::uint32_t module){
    (void)::DisableThreadLibraryCalls(reinterpret_cast<HMODULE>(static_cast<std::uintptr_t>(module)));
}
std::uint32_t __cdecl render_win_last_error_005b213c(){return platform_last_error();}
}

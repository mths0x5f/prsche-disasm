#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/application_instance.hpp"
#include "porsche/startup_services.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/formatter_strings.hpp"
#include "porsche/formatter_text.hpp"
#include "porsche/file_threads.hpp"
#include "porsche/heap.hpp"
#include "porsche/file_events.hpp"

static_assert(sizeof(void*)==4,"Original startup transport is x86");
namespace porsche {
void* __cdecl application_instance_create_mutex(void* security_attributes,
    std::uint32_t initial_owner,const char* name){
    return ::CreateMutexA(static_cast<SECURITY_ATTRIBUTES*>(security_attributes),
        static_cast<BOOL>(initial_owner),name);
}
std::uint32_t __cdecl application_instance_get_last_error(){return platform_last_error();}
std::uint32_t __stdcall startup_module_filename(void* module,char* buffer,std::uint32_t capacity){
    return formatter_error_module_name(module,buffer,capacity);
}
std::int32_t __cdecl startup_drive_character_005a2c24(std::int32_t c){
    return formatter_text_alpha_005a2c24(c);
}
void __cdecl application_os_start(std::uint32_t count){thread_init_0055f320(count);}
void* __cdecl application_lock_create(){return heap_lock_create_005321f0();}
}

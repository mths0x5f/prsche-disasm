#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstddef>
#include "../361-startup-device-pool/startup_device.hpp"
#include "porsche/startup_input.hpp"
#include "porsche/window_create.hpp"

// Original DINPUT.dll named import, not DirectInput8 or a lazy loader.
extern "C" __declspec(dllimport) std::int32_t __stdcall DirectInputCreateA(
    void*,std::uint32_t,void**,void*);
// The generated import library carries the original undecorated DLL export.
// Alias only the import POINTER cell; the caller remains four-argument stdcall.
#pragma comment(linker,"/alternatename:__imp__DirectInputCreateA@16=__imp__DirectInputCreateA")
static_assert(sizeof(void*)==4,"Original platform bindings require x86");
static_assert(sizeof(porsche::StartupPoint)==sizeof(POINT));
static_assert(alignof(porsche::StartupPoint)==alignof(POINT));
static_assert(offsetof(porsche::StartupPoint,x)==offsetof(POINT,x));
static_assert(offsetof(porsche::StartupPoint,y)==offsetof(POINT,y));

namespace porsche {
std::uint32_t __stdcall startup_directinput_create_0056e940(
        void* instance,std::uint32_t version,void** output,void* outer){
    return static_cast<std::uint32_t>(::DirectInputCreateA(instance,version,output,outer));
}
std::int32_t __stdcall startup_input_direct_input_create(
        void* instance,std::uint32_t version,void** output,void* outer){
    return static_cast<std::int32_t>(startup_directinput_create_0056e940(instance,version,output,outer));
}
std::uint32_t __stdcall startup_get_cursor_pos(StartupPoint* point){
    return static_cast<std::uint32_t>(::GetCursorPos(reinterpret_cast<POINT*>(point)));
}
std::uint32_t __stdcall startup_screen_to_client(void* hwnd,StartupPoint* point){
    return static_cast<std::uint32_t>(::ScreenToClient(static_cast<HWND>(hwnd),reinterpret_cast<POINT*>(point)));
}
void* __stdcall startup_input_get_module_handle(){return window_module_handle(nullptr);}
}

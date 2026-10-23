#pragma once
#include <cstdint>

namespace porsche {

// Original DirectInput state at Porsche.exe 0069e078..0069e0a4.
extern std::uint32_t startup_mouse_mode_0069e078;
extern std::uint32_t startup_mouse_slot0_0069e07c;
extern std::uint32_t startup_mouse_slot1_0069e080;
extern std::uint32_t startup_mouse_slot2_0069e084;
extern std::uint8_t startup_mouse_flags_0069e088[4];
extern void* startup_directinput_0069e098;
extern void* startup_mouse_device_0069e09c;
extern std::uint32_t startup_mouse_initialized_0069e0a0;
extern std::uint32_t startup_mouse_exit_registered_0069e0a4;

struct StartupGuid {std::uint32_t a;std::uint16_t b,c;std::uint8_t d[8];};
struct StartupPoint {std::int32_t x,y;};

// Exact original callees: retained as extern until their bodies/platform
// transports are separately proven. 0056e940 is the DINPUT.DLL thunk.
void __cdecl startup_frame_init_00572690();
std::uint32_t __stdcall startup_directinput_create_0056e940(
    void*,std::uint32_t,void**,void*);
void __cdecl startup_directinput_cleanup_00537070();
std::uint32_t __cdecl startup_mouse_mode_005370c0(std::uint32_t,std::uint32_t);
std::uint32_t __stdcall startup_get_cursor_pos(StartupPoint*);
std::uint32_t __stdcall startup_screen_to_client(void*,StartupPoint*);
std::uint32_t __cdecl startup_mouse_callback_00537020(std::uint32_t,std::uint32_t,
    std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t);
void __cdecl startup_mouse_exit_005370b0();

std::uint32_t __cdecl startup_subsystem_result_00536e50();
void __cdecl startup_subsystem_00536e50();
}

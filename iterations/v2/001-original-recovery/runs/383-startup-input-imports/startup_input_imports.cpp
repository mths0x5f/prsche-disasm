#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <mmsystem.h>
#include "porsche/startup_subsystems.hpp"
static_assert(sizeof(void*)==4,"Original startup bindings require x86");
static_assert(sizeof(UINT_PTR)==sizeof(std::uint32_t));
static_assert(sizeof(JOYCAPSA)==0x194,"Original ANSI joystick capability buffer");
namespace porsche {
std::uint32_t __cdecl startup_get_keyboard_type(std::uint32_t kind){
    return static_cast<std::uint32_t>(::GetKeyboardType(static_cast<int>(kind)));
}
std::int32_t __cdecl startup_joy_get_num_devs(){
    return static_cast<std::int32_t>(::joyGetNumDevs());
}
std::uint32_t __cdecl startup_joy_get_dev_caps(std::uint32_t id,void* caps,std::uint32_t bytes){
    return ::joyGetDevCapsA(static_cast<UINT_PTR>(id),static_cast<JOYCAPSA*>(caps),bytes);
}
}

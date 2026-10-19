#include "porsche/startup_input.hpp"
#include "porsche/startup_subsystems.hpp"
#include <windows.h>
#include <mmsystem.h>

// Platform adapters only. The calling recovered routines stay in
// recovered/Porsche.exe; these forward to the exact imports the original uses.
// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.

namespace porsche {

// 0x0055fd47..0x0055fd49 (startup_input_initialize_0055fcf0): push 0; call
// [0x005b2138] = KERNEL32!GetModuleHandleA(NULL).
void* __stdcall startup_input_get_module_handle() {
    return ::GetModuleHandleA(nullptr);
}

// 0x0055fd3b..0x0055fd50: DirectInputCreateA(GetModuleHandleA(NULL), 0x500,
// &cell_006a5b14, NULL) through the import thunk 0x0056e940 = jmp [0x005b202c],
// DINPUT.dll!DirectInputCreateA.
//
// Deviation, platform only: current Windows SDKs ship dinput8.lib but no
// dinput.lib, so the same DINPUT.dll export is resolved on first use instead of
// at load time. Where the original EXE would fail to load without DINPUT.dll,
// this returns E_FAIL from the call; arguments and the DLL entry are unchanged.
std::int32_t __stdcall startup_input_direct_input_create(void* instance, std::uint32_t version,
                                                          void** direct_input, void* outer) {
    using Create = HRESULT(WINAPI*)(HINSTANCE, DWORD, void**, void*);
    static Create create = [] {
        HMODULE dll = ::LoadLibraryA("dinput.dll");
        return dll ? reinterpret_cast<Create>(::GetProcAddress(dll, "DirectInputCreateA")) : nullptr;
    }();
    if (!create) {
        return static_cast<std::int32_t>(E_FAIL);
    }
    return static_cast<std::int32_t>(create(static_cast<HINSTANCE>(instance), version, direct_input, outer));
}

// 0x00564e71: mov esi,[0x005b2298] = USER32!GetKeyboardType, called twice by
// startup_keyboard_detect_00564e70.
std::uint32_t __cdecl startup_get_keyboard_type(std::uint32_t kind) {
    return static_cast<std::uint32_t>(::GetKeyboardType(static_cast<int>(kind)));
}

// 0x00564abe: call [0x005b2354] = WINMM!joyGetNumDevs
// (startup_joystick_enumerate_00564ab0).
std::int32_t __cdecl startup_joy_get_num_devs() {
    return static_cast<std::int32_t>(::joyGetNumDevs());
}

// 0x00564ad0: mov edi,[0x005b2358] = WINMM!joyGetDevCapsA, called per device.
std::uint32_t __cdecl startup_joy_get_dev_caps(std::uint32_t id, void* caps, std::uint32_t bytes) {
    return ::joyGetDevCapsA(id, static_cast<LPJOYCAPSA>(caps), bytes);
}

} // namespace porsche

#pragma once
#include <cstdint>
namespace porsche {
// New storage only: 005deab8 is file-backed zero; 006a644c is loader-zeroed.
extern std::uint32_t startup_cursor_z_005deab8;
extern std::uint32_t startup_frame_counter_006a644c;
// Opaque DWORD address transport. No homogeneous callback ABI is asserted.
extern std::uintptr_t startup_frame_callback_005debe0;
extern std::uintptr_t startup_frame_callback_005debe4;
extern std::uintptr_t startup_frame_callback_005debe8;
std::uint32_t __cdecl startup_frame_copy_00572640();
void __cdecl startup_frame_increment_00572670();
void __cdecl startup_frame_decrement_00572680();
void __cdecl startup_frame_init_00572690();
}

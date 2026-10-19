#pragma once
#include <cstddef>
#include <cstdint>

namespace porsche {
// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// DirectInput COM entries used by 0x0056fd00/0x0056fd30; stdcall is proven by
// their RET stack cleanup in the original vtable calls.
using InputPoll = std::uint32_t (__stdcall*)(void*);
using InputAcquire = std::uint32_t (__stdcall*)(void*);
using InputGetState = std::uint32_t (__stdcall*)(void*, std::uint32_t, void*);
struct InputVtable {
    void* other_00[7];
    InputAcquire acquire_1c;
    void* other_20;
    InputGetState get_state_24;
    void* other_28[15];
    InputPoll poll_64;
};
struct InputDevice { InputVtable* vtable; };
struct InputSlot {
    InputDevice* device;
    std::uint32_t flags_04;
    std::uint32_t type_08;
    std::uint8_t state_0c[0x100];
};
static_assert(sizeof(InputVtable) == 0x68 && offsetof(InputVtable, acquire_1c) == 0x1c &&
              offsetof(InputVtable, get_state_24) == 0x24 && offsetof(InputVtable, poll_64) == 0x64);
static_assert(sizeof(InputSlot) == 0x10c && offsetof(InputSlot, type_08) == 8 &&
              offsetof(InputSlot, state_0c) == 0xc);

extern std::int32_t input_count_0069cb0c;
extern InputSlot input_slots_006be040[32];

std::uint32_t __cdecl input_poll_0056fd00(InputDevice* device);
std::uint32_t __cdecl input_read_0056fd30(InputDevice* device, std::uint32_t size, void* destination);
std::uint32_t __cdecl input_poll_read_0056fce0(InputDevice* device, void* destination, std::uint32_t size);
// \real\patch3\pc\input.c "_getstate" (0x00532e10..0x00532f34, 293 bytes):
// modes 1, 2, 6 and 8 and both diagnostics are recovered (Run 423). Negative and
// >= 32 indices stay typed boundaries: the original performs no bound check
// beyond the signed count, so it reads outside the 32-slot array, into memory
// whose layout is not recovered (the mode-2 buffer below ends 4 bytes before the
// slots).
void* __cdecl fe_input_getstate_00532e10(std::uint32_t index, std::uint32_t mode);
void* __cdecl input_negative_index_00532e10(std::int32_t index, std::uint32_t mode);
void* __cdecl input_unmapped_index_00532e10(std::uint32_t index, std::uint32_t mode);
// 0x006bde20: 0x21c-byte capabilities buffer filled by 0x0056fdb0 for mode 2 and
// returned to the caller, 0x220 bytes before input_slots_006be040. Storage
// boundary until that block's layout is recovered.
extern std::uint8_t input_caps_buffer_006bde20[0x21c];
}

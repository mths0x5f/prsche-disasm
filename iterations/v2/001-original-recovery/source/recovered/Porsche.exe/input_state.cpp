#include "porsche/input_state.hpp"
#include "porsche/files.hpp"         // diagnostic_handler_005debf0
#include "porsche/input_buffer.hpp"  // input_caps_0056fdb0, input_property_mode8_0056fff0

namespace porsche {
std::int32_t input_count_0069cb0c;
InputSlot input_slots_006be040[32];
// 006bde20: mode-2 capabilities buffer. Its only users are 00532e10 (address)
// and 0056fdb0, which clears exactly 0x21c bytes; zero-fill .data like the slots.
// The original places it 0x220 bytes before the slots; that distance is not
// reproduced, and only the unrecovered negative-index path could depend on it.
std::uint8_t input_caps_buffer_006bde20[0x21c];

static bool lost(std::uint32_t result) {
    return result == 0x8007000cu || result == 0x8007001eu;
}

std::uint32_t __cdecl input_poll_0056fd00(InputDevice* device) {
    auto result = device->vtable->poll_64(device);
    if (lost(result)) {
        result = device->vtable->acquire_1c(device);
        if (result == 0) result = device->vtable->poll_64(device);
    }
    return result;
}

std::uint32_t __cdecl input_read_0056fd30(InputDevice* device, std::uint32_t size, void* destination) {
    auto result = device->vtable->get_state_24(device, size, destination);
    if (lost(result)) {
        result = device->vtable->acquire_1c(device);
        if (result == 0) result = device->vtable->get_state_24(device, size, destination);
    }
    return result;
}

std::uint32_t __cdecl input_poll_read_0056fce0(InputDevice* device, void* destination, std::uint32_t size) {
    input_poll_0056fd00(device);
    return input_read_0056fd30(device, size, destination);
}

namespace {
constexpr const char* kInputSource = "\\real\\patch3\\pc\\input.c";   // 0x005bb2f8

// The diagnostic handler is a cdecl printf-style sink: the invalid-mode path
// pushes the format and the mode and pops 8 bytes, the other path pops 4.
using DiagnosticPrintf = void(__cdecl*)(const char*, ...);
}

// 0x00532e10 (293 bytes), "_getstate" in \real\patch3\pc\input.c.
// The count is read once on entry (ebx) and the slot device is tested before the
// mode is dispatched through the 8-entry table at 0x00532f38.
void* __cdecl fe_input_getstate_00532e10(std::uint32_t raw_index, std::uint32_t mode) {
    const auto index = static_cast<std::int32_t>(raw_index);
    const std::int32_t count = input_count_0069cb0c;
    if (index >= count) return nullptr;
    // The original signed compare admits negative indices and reads before
    // 0x006be040. That adjacent memory is outside this bounded slot unit.
    if (index < 0) return input_negative_index_00532e10(index, mode);
    if (index >= 32) return input_unmapped_index_00532e10(raw_index, mode);
    auto& slot = input_slots_006be040[index];
    if (!slot.device) return nullptr;
    // InputSlot::device and InputBufferDevice are two views of the same
    // DirectInput device pointer.
    auto* buffer_device = reinterpret_cast<InputBufferDevice*>(slot.device);
    switch (mode) {
    case 1:                                    // 0x00532ed6: the device count
        return reinterpret_cast<void*>(static_cast<std::uintptr_t>(static_cast<std::uint32_t>(count)));
    case 2:                                    // 0x00532ede: fill and return the caps buffer
        if (input_caps_0056fdb0(buffer_device, input_caps_buffer_006bde20) != 0) return nullptr;
        return input_caps_buffer_006bde20;
    case 6: {                                  // 0x00532e5b: read the device state
        std::uint32_t size;
        switch (slot.type_08 & 0xffu) {        // table at 0x00532f58
        case 1: case 4: size = 0x50; break;
        case 2: size = 0x10; break;
        case 3: size = 0x100; break;
        default:                               // 0x00532eae
            diagnostic_file_005deb74_set(kInputSource);
            diagnostic_line_005deb78 = 0x1fa;
            diagnostic_handler_005debf0("[INPUT] _getstate, Internal error in devicetype\n");
            return nullptr;
        }
        input_poll_read_0056fce0(slot.device, slot.state_0c, size);
        return &slot.type_08;
    }
    case 8:                                    // 0x00532efb: device property
        return reinterpret_cast<void*>(static_cast<std::uintptr_t>(
            input_property_mode8_0056fff0(buffer_device)));
    default:                                   // 0x00532f0a: modes 3, 4, 5, 7 and outside 1..8
        diagnostic_file_005deb74_set(kInputSource);
        diagnostic_line_005deb78 = 0x219;
        reinterpret_cast<DiagnosticPrintf>(diagnostic_handler_005debf0)(
            "[INPUT] - Invalid getstate (%d)\n", mode);
        return nullptr;
    }
}
}

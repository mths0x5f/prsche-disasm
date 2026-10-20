// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00568e90..00568eb2 (35B), 00591760..0059177a (27B).
#include "resource_device_327.hpp"

namespace porsche {

std::uint32_t __cdecl resource_device_prefix_full_00591760(const char* path) {
    const std::uint32_t letter = resource_drive_letter_005916a0(path);
    return letter == 0 ? 0u : letter - 0x40u;
}

// Typed adapter for the existing 005919a0 caller, whose original MOV stores AL.
// This is another view of the same body, not another recovered original VA.
std::uint8_t __cdecl disk_path_device_00591760(const char* path) {
    return static_cast<std::uint8_t>(resource_device_prefix_full_00591760(path));
}

std::uint32_t __cdecl file_device_name_00568e90(const char* path) {
    if (formatter_search_character_005a2780(path, 0x7c) != nullptr) {
        return 0;
    }
    return resource_device_prefix_full_00591760(path);
}

} // namespace porsche

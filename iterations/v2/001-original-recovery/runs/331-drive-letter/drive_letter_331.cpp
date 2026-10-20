#include <windows.h>
#include "../327-resource-open-callback-evidence/resource_device_327.hpp"

namespace porsche {

// Porsche.exe ddd748fdbe6d:005916a0..0059170e (111 bytes).
std::uint8_t __cdecl resource_drive_letter_005916a0(const char* path) {
    char* file_part = const_cast<char*>(formatter_search_character_005a2780(path, 0x7c));
    if (file_part != nullptr)
        return 0;
    if (path == nullptr)
        path = "."; // Original read-only bytes at005cd1f4:2e00.
    char full_path[0x105];
    const DWORD length = GetFullPathNameA(path, 0x105, full_path, &file_part);
    CharUpperA(full_path);
    if (static_cast<std::int32_t>(length) > 1 && full_path[1] == ':')
        return static_cast<std::uint8_t>(full_path[0]);
    return 0;
}

} // namespace porsche

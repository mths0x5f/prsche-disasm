#include "resource_open_313.hpp"

namespace porsche {

void* __cdecl resource_open_0059d8e0(const char* name, std::uint32_t flags) {
    char path[260];
    if (file_roots_enabled_006af370 == 0) {
        const char* source = name;
        char* target = path;
        do {
            *target++ = *source;
        } while (*source++ != '\0');
        return file_open_00561ca0(path, flags);
    }

    // Porsche.exe 005cc588 is the null-terminated literal "%s%s".
    formatter_entry_005a0fbf(path, "%s%s", file_root_006af168, name);
    if (file_exists_00561b80(path) != 0)
        return file_open_00561ca0(path, flags);

    if (file_fallback_006af26c[0] != '\0') {
        formatter_entry_005a0fbf(path, "%s%s", file_fallback_006af26c, name);
        if (file_exists_00561b80(path) != 0)
            return file_open_00561ca0(path, flags);
    }

    // Reload callback after the earlier calls: they may change the cell.
    if (missing_file_006afbe4 != nullptr)
        missing_file_006afbe4(name, -2);
    return nullptr;
}

void* __cdecl game_setup_resource_file_open_0059d8e0(const char* path,
                                                       std::uint32_t flags) {
    return resource_open_0059d8e0(path, flags);
}

void* __cdecl splash_progress_load_resource_0059d8e0(const char* path,
                                                       std::uint32_t flags) {
    return resource_open_0059d8e0(path, flags);
}

} // namespace porsche

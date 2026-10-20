#pragma once

#include "porsche/disk_open.hpp"
#include "porsche/files.hpp"
#include "porsche/formatter_search.hpp"

namespace porsche {

// Original 005916a0 defines AL, not the upper 24 bits of EAX. Its Win32
// GetFullPathNameA/CharUpperA implementation remains an explicit boundary.
std::uint8_t __cdecl resource_drive_letter_005916a0(const char* path);

// One full-width core for the original 00591760 body. Its existing disk
// consumer uses only AL through disk_path_device_00591760; 00568e90 forwards
// the full EAX value, so calling the byte-return view there would truncate it.
std::uint32_t __cdecl resource_device_prefix_full_00591760(const char* path);

} // namespace porsche

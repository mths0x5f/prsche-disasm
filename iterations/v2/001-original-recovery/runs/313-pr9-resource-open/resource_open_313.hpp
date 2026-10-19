#pragma once

#include "porsche/files.hpp"
#include "porsche/formatter_entry.hpp"
#include "porsche/game_setup.hpp"
#include "porsche/splash_progress.hpp"

namespace porsche {

// 00561ca0 is an unrecovered pointer-returning boundary (CALL at 0059d927).
void* __cdecl file_open_00561ca0(const char* path, std::uint32_t flags);

void* __cdecl resource_open_0059d8e0(const char* path, std::uint32_t flags);

} // namespace porsche

#pragma once

#include "porsche/files.hpp"
#include "porsche/resource_leaf.hpp"

namespace porsche {

// Original request constructor 00568260 is not recovered here. The third
// argument is the request context forwarded to operation_allocate_005682a0.
std::uint32_t __cdecl request_exists_00568260(
    const char* path, std::uint32_t group, void* context);

// 00533f00..00533f33: construct, wait, and return the raw completion DWORD.
std::int32_t __cdecl resource_exists_request_00533f00(
    const char* path, std::uint32_t group);

// file_exists_00561b80 is declared by its canonical files.hpp contract.

} // namespace porsche

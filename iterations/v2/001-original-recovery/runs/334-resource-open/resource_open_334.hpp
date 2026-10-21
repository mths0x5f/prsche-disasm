#pragma once

#include "porsche/resource_dispatch.hpp"

#include <cstdint>

namespace porsche {

// Consumer contract at00561d59..00561d60: three cdecl arguments, raw EAX pointer.
// This declares a storage boundary only. No production cell/provider is added.
using ResourceOpenTransform = void* (__cdecl*)(
    void* buffer, const char* saved_path, std::uint32_t saved_flags);
extern ResourceOpenTransform resource_open_transform_006ad750;
static_assert(sizeof(ResourceOpenTransform) == 4, "original x86 callback cell");

// The dispatcher transports a raw DWORD through its existing int32 callback
// signature. Return bits are preserved; this is not a pointer-function cast.
std::int32_t __cdecl resource_open_callback_00561ce0(
    std::uint32_t group, void* context);
void* __cdecl file_open_00561ca0(const char* path, std::uint32_t flags);

} // namespace porsche

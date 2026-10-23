#pragma once

#include <cstdint>

namespace porsche {

// Original cdecl entries, Porsche.exe 005b0100/005b02c0/005b0480.
// The core variants expose the original advanced EAX for native comparison.
void* __cdecl heap_copy_x87_005b0100_core(void*, const void*, std::uint32_t);
void* __cdecl heap_copy_mmx_005b02c0_core(void*, const void*, std::uint32_t);
void* __cdecl heap_copy_sse_005b0480_core(void*, const void*, std::uint32_t);
void __cdecl heap_copy_005b0100(void*, const void*, std::uint32_t);
void __cdecl heap_copy_005b02c0(void*, const void*, std::uint32_t);
void __cdecl heap_copy_005b0480(void*, const void*, std::uint32_t);

} // namespace porsche


#pragma once

#include "porsche/heap.hpp"

namespace porsche {

// Original Porsche.exe ddd748fd... callees. These remain separate recovery
// boundaries; the dispatcher must not replace them with host memset.
void __cdecl heap_fill_sse_005b0b00(void* destination, std::uint32_t value, std::uint32_t bytes);
void __cdecl heap_fill_mmx_005b0a40(void* destination, std::uint32_t value, std::uint32_t bytes);
void __cdecl heap_fill_scalar_005b0980(void* destination, std::uint32_t value, std::uint32_t bytes);

} // namespace porsche

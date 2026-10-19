#pragma once

#include "../312-pr7-fill-dispatch/0053c290.hpp"

namespace porsche {

// Typed EAX result view of the one original 005b0a40 body. The Run312 game
// contract remains the void heap_fill_mmx_005b0a40 adapter.
void* __cdecl heap_fill_mmx_005b0a40_core(void* destination,
    std::uint32_t value, std::uint32_t bytes);

} // namespace porsche

#pragma once

#include "../312-pr7-fill-dispatch/0053c290.hpp"

namespace porsche {

// Typed view of original EAX; the canonical void dispatch target above calls it.
void* __cdecl heap_fill_sse_005b0b00_core(void* destination,
    std::uint32_t value, std::uint32_t bytes);

} // namespace porsche

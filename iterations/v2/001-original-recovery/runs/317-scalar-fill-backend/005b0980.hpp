#pragma once

#include "../312-pr7-fill-dispatch/0053c290.hpp"

namespace porsche {

// Typed execution core for the original 005b0980 EAX result. It models the
// same single PE function as the void adapter declared by Run312, not a second
// original function or a separate game entry point.
void* __cdecl heap_fill_scalar_005b0980_core(void* destination,
    std::uint32_t value, std::uint32_t bytes);

} // namespace porsche

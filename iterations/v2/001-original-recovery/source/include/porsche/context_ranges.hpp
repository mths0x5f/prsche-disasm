#pragma once
#include "porsche/context_effects.hpp"
#include "porsche/application_alloc.hpp"
#include "porsche/application_heap.hpp"

namespace porsche {
void __cdecl context_range_walk_00529c50(ApplicationContextRange16 first,
    ApplicationContextRange16 last, std::uint32_t captured_last);
}

#pragma once
#include "porsche/application_context_base.hpp"

namespace porsche {
void* __cdecl context_selector_pointer_005e4fec();
// Original pooled-free helpers. 004237d0's third argument is a pool mode;
// its inherited name "clear" does not describe its original behavior.
void __cdecl context_free_00424000(void* block, std::uint32_t bytes);
void __cdecl context_table_release_0059ecd0(void* block);
// 0059eeb0 is an unresolved pool-refill service in this packet.
// 004211d0 reloads the selected list head and ignores incidental EAX.
}

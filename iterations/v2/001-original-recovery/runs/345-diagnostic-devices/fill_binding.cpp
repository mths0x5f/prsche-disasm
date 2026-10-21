#include "porsche/application_heap.hpp"
#include "porsche/heap.hpp"

namespace porsche {
// Original 0059ea10 calls 0053c290. Its canonical Run312 dispatcher and
// Run317/319/320 backends are already linked and accepted by Run321.
void __cdecl application_fill(void* destination, std::uint32_t value,
                              std::uint32_t bytes) {
    heap_fill_0053c290(destination, value, bytes);
}
}

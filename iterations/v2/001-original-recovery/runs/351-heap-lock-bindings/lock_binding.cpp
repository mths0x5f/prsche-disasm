#include "porsche/application_heap.hpp"
#include "porsche/heap.hpp"

namespace porsche {
// Typed application boundary for the accepted original lock providers.
void __cdecl application_lock_enter(void* lock) {
    heap_enter_005322b0(lock);
}
void __cdecl application_lock_leave(void* lock) {
    heap_leave_005322c0(lock);
}
}

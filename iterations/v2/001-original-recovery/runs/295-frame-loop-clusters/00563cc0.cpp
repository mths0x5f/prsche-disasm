#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __cdecl stream_slot_finalize_00563cc0(StreamSlot_295* slot) {
    heap_enter_005322b0(stream_queue_lock_006a5be8);
    const std::uint32_t state = slot->state_0c;
    if (state == 1u) {
        slot->state_0c = 2u;
    }
    heap_leave_005322c0(stream_queue_lock_006a5be8);
    if (state == 1u) {
        if (slot->buffer_10 > 1u) {
            free_00531f90(reinterpret_cast<void*>(static_cast<std::uintptr_t>(slot->buffer_10)));
        }
        slot->id &= 0xffu;
        slot->operation_18 = 0u;
        stream_queue_push_00563c30(&stream_free_queue_006a5bd0, slot);
    }
}
} // namespace porsche

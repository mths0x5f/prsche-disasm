#include "frame_loop_clusters_295.hpp"

namespace porsche {
std::uint32_t __cdecl stream_completion_pump_00563bd0(std::uint32_t, std::uint32_t) {
    StreamSlot_295* slot = stream_queue_pop_00563c70(&stream_completed_queue_006a5bc8);
    if (slot == nullptr) {
        return 0u;
    }
    do {
        if (slot->state_0c != 0u) {
            stream_slot_finalize_00563cc0(slot);
        } else {
            const std::uint32_t id = slot->id;
            slot->callback_14(id);
            slot->id = id & 0xffu;
            stream_queue_push_00563c30(&stream_free_queue_006a5bd0, slot);
        }
        slot = stream_queue_pop_00563c70(&stream_completed_queue_006a5bc8);
    } while (slot != nullptr);
    return 0u;
}
} // namespace porsche

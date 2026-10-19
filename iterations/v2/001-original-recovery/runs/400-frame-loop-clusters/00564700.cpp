#include "frame_loop_clusters_400.hpp"

namespace porsche {
void __cdecl stream_slot_cancel_00564700(std::uint32_t handle) {
    StreamSlot_400* slot = stream_slot_resolve_00564750(handle);
    if (slot != nullptr && slot->state_0c == 0u) {
        const std::uint32_t op = slot->operation_18;
        slot->state_0c = 1u;
        file_operation_cancel_00567cf0(op);
        if (op == 0u && slot->callback_14 == nullptr) {
            stream_slot_finalize_00563cc0(slot);
        }
    }
}
} // namespace porsche

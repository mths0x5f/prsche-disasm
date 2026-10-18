#include "frame_loop_clusters_295.hpp"

namespace porsche {
StreamSlot_295* __cdecl stream_slot_resolve_00564750(std::uint32_t handle) {
    const std::int32_t index = static_cast<std::int32_t>(handle & 0xffu);
    if (static_cast<std::int32_t>(handle) < 0x100 || index >= stream_slot_count_006a5be0) {
        return nullptr;
    }
    StreamSlot_295* slot = stream_slots_006a5bc0 + index;
    return slot->id == handle ? slot : nullptr;
}
} // namespace porsche

#include "frame_loop_clusters_400.hpp"

namespace porsche {
void __cdecl stream_queue_push_00563c30(StreamQueue_400* queue, StreamSlot_400* slot) {
    heap_enter_005322b0(stream_queue_lock_006a5be8);
    if (queue->head == nullptr) {
        queue->head = slot;
    } else {
        queue->tail->next = slot;
    }
    queue->tail = slot;
    slot->next = nullptr;
    heap_leave_005322c0(stream_queue_lock_006a5be8);
}
} // namespace porsche

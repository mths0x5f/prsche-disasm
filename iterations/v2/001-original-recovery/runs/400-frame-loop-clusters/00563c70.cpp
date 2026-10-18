#include "frame_loop_clusters_400.hpp"

namespace porsche {
StreamSlot_400* __cdecl stream_queue_pop_00563c70(StreamQueue_400* queue) {
    heap_enter_005322b0(stream_queue_lock_006a5be8);
    StreamSlot_400* head = queue->head;
    if (head == nullptr) {
        heap_leave_005322c0(stream_queue_lock_006a5be8);
        return nullptr;
    }
    queue->head = head->next;
    heap_leave_005322c0(stream_queue_lock_006a5be8);
    return head;
}
} // namespace porsche

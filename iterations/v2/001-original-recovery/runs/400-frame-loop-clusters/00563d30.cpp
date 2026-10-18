#include "frame_loop_clusters_400.hpp"

namespace porsche {
void __cdecl application_main_function_00563d30() {
    if (stream_slots_006a5bc0 == nullptr) {
        return;
    }
    std::int32_t count = stream_slot_count_006a5be0;
    for (std::int32_t i = 0; i < count; ++i) {
        stream_slot_cancel_00564700(stream_slots_006a5bc0[i].id);
        count = stream_slot_count_006a5be0;
    }
    for (;;) {
        bool any_pending = false;
        if (count > 0) {
            const StreamSlot_400* table = stream_slots_006a5bc0;
            for (std::int32_t i = 0; i < count; ++i) {
                if (table[i].operation_18 != 0u) {
                    any_pending = true;
                }
            }
        }
        if (!any_pending) {
            break;
        }
        if (file_current_thread_0055f780(0u) != 0) {
            timed_callbacks_005366e0(0u);
        }
        file_sleep_0055f740(0u);
        count = stream_slot_count_006a5be0;
    }
    if (stream_archive_handle_006a5be4 != nullptr) {
        close_00533da0(stream_archive_handle_006a5be4, 0x64u);
        stream_archive_handle_006a5be4 = nullptr;
    }
    window_scheduler_remove_005366a0(&stream_completion_pump_00563bd0);
    stream_completion_pump_00563bd0(0u, 0u);
    heap_lock_destroy_005322d0(stream_queue_lock_006a5be8);
    free_00531f90(stream_slots_006a5bc0);
    stream_slots_006a5bc0 = nullptr;
}
} // namespace porsche

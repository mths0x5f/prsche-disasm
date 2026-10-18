#include "frame_loop_clusters_400.hpp"

namespace porsche {
void __cdecl application_main_function_00412030() {
    if (frame_control_enabled_005e940c != 0u) {
        frame_control_slot_release_005338d0(
            static_cast<std::int32_t>(frame_control_table_005e9420[frame_control_index_005e9410].slot_04));
        frame_control_slot_release_005338d0(
            static_cast<std::int32_t>(frame_control_table_005e9420[frame_control_index_005e9410].slot_02));
        frame_control_slot_release_005338d0(
            static_cast<std::int32_t>(frame_control_table_005e9420[frame_control_index_005e9410].slot_00));
        frame_control_slot_release_005338d0(
            static_cast<std::int32_t>(frame_control_table_005e9420[frame_control_index_005e9410].slot_06));
    }
}
} // namespace porsche

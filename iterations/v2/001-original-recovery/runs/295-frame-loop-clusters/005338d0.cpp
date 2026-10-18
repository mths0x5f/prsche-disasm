#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __cdecl frame_control_slot_release_005338d0(std::int32_t slot) {
    if (slot >= 0 && slot < 32) {
        auto& entry = frame_control_slots_0069cb90[slot];
        if (entry.state_0c != 0xffffffffu) {
            void* const device = entry.device_08;
            const auto vtable = *reinterpret_cast<std::uintptr_t const*>(device);
            const auto release = *reinterpret_cast<void(__stdcall* const*)(void*)>(vtable + 0x20u);
            release(device);
            entry.active_00 = 0u;
        }
    }
}
} // namespace porsche

#include "frame_loop_clusters_400.hpp"

namespace porsche {
std::int32_t __cdecl audio_channel_stop_00565d60(std::uint32_t handle) {
    if (audio_system_active_006b499c == 0u) {
        return -10;
    }
    audio_backend_lock_005896d0();
    const std::int32_t channel = audio_backend_find_channel_00589d20(handle);
    if (channel >= 0) {
        std::uint32_t voice_slot = 0xffffffffu;
        while (audio_backend_next_voice_00590340(channel, &voice_slot) != 0u) {
            audio_backend_stop_voice_0058a8b0(voice_slot);
        }
    }
    audio_backend_unlock_005896f0();
    return channel;
}
} // namespace porsche

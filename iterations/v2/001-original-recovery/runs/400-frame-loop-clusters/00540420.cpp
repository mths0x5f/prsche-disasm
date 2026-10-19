#include "frame_loop_clusters_400.hpp"
#include <cstring>

namespace porsche {
void __thiscall RenderMovieBridge_00540420::destroy_00540420() {
    auto* base = reinterpret_cast<const std::uint8_t*>(this);
    VirtualDeleteSlot0_400* inner = nullptr;
    std::memcpy(&inner, base + 4, sizeof(inner));
    if (inner != nullptr) {
        inner->delete_slot0(1u);
    }
    game_setup_movie_service_0069ed0c = nullptr;
}
} // namespace porsche

#include "frame_loop_clusters_295.hpp"
#include <cstring>

namespace porsche {
void __cdecl render_teardown_registry_0047f190() {
    auto* root = static_cast<std::uint8_t*>(render_registry_root_00628bac);
    if (root != nullptr) {
        RenderVector12_295* vec = nullptr;
        std::memcpy(&vec, root + 0xa4, sizeof(vec));
        if (vec != nullptr) {
            const std::uint32_t end = vec->end;
            for (std::uint32_t item = vec->begin; item != end; item += 4u) {
                render_registry_item_noop_00514990(
                    reinterpret_cast<void*>(static_cast<std::uintptr_t>(item)));
            }
            const std::uint32_t first = vec->begin;
            const std::int32_t count = static_cast<std::int32_t>(vec->capacity_end - first) >> 2;
            if (count != 0) {
                application_context_member_destroy_block_00441200(
                    reinterpret_cast<void*>(static_cast<std::uintptr_t>(first)),
                    static_cast<std::uint32_t>(count << 2));
            }
            application_release_0059f050(vec);
        }
        application_release_0059f050(root);
        render_registry_root_00628bac = nullptr;
        return;
    }
    render_registry_root_00628bac = nullptr;
}
} // namespace porsche

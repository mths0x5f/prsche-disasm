#include "frame_loop_clusters_400.hpp"
#include <cstring>

namespace porsche {
namespace {
template <typename T>
T read_ptr(const std::uint8_t* base, std::size_t offset) {
    T ptr;
    std::memcpy(&ptr, base + offset, sizeof(ptr));
    return ptr;
}
} // namespace

void __cdecl application_main_function_00467740() {
    render_teardown_prefix_004b7140();
    render_teardown_secondary_00465e20();
    auto* display = reinterpret_cast<std::uint8_t*>(render_display_00628130);
    if (display != nullptr) {
        auto* sub_7c = read_ptr<RenderSubobject_00538d80*>(display, 0x7c);
        if (sub_7c != nullptr) {
            sub_7c->destroy_00538d80();
            application_release_0059f050(sub_7c);
        }
        auto* sub_70 = read_ptr<VirtualDeleteSlot0_400*>(display, 0x70);
        if (sub_70 != nullptr) {
            sub_70->delete_slot0(1u);
        }
        auto* sub_6c = read_ptr<RenderMovieBridge_00540420*>(display, 0x6c);
        if (sub_6c != nullptr) {
            sub_6c->destroy_00540420();
            application_release_0059f050(sub_6c);
        }
        reinterpret_cast<RenderChannel_00466500*>(display + 0x34)->destroy_00466500();
        reinterpret_cast<RenderChannel_00466500*>(display + 0x14)->destroy_00466500();
        application_release_0059f050(display);
    }
    render_display_00628130 = nullptr;
    render_teardown_registry_0047f190();
    auto* core = reinterpret_cast<VirtualDeleteSlot1_400*>(render_core_0065b39c);
    if (core != nullptr) {
        core->delete_slot1(1u);
    }
}
} // namespace porsche

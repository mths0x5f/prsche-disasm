#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __thiscall RenderSubobject_00538d80::destroy_00538d80() {
    auto* base = reinterpret_cast<std::uint8_t*>(this);
    reinterpret_cast<RenderBufferCell_00539eb0*>(base + 0x5c)->release_00539eb0();
    reinterpret_cast<RenderBufferCell_00539eb0*>(base)->release_00539eb0();
}
} // namespace porsche

#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __cdecl application_main_function_00425780() {
    auto* vec = frame_callback_vector_0060c9f4;
    const std::int32_t count = static_cast<std::int32_t>(vec->end - vec->begin) >> 3;
    for (std::int32_t i = 0; i < count; ++i) {
        const std::uint32_t offset = static_cast<std::uint32_t>(i) * 8u;
        auto* obj = *reinterpret_cast<FrameCallbackObject_295* const*>(
            static_cast<std::uintptr_t>(frame_callback_vector_0060c9f4->begin + offset));
        if (obj->poll_18() != 0u) {
            auto* notify_obj = *reinterpret_cast<FrameCallbackObject_295* const*>(
                static_cast<std::uintptr_t>(frame_callback_vector_0060c9f4->begin + offset));
            notify_obj->notify_14(0u);
        }
    }
    auto* compact = frame_compact_vector_0060c9c4;
    const std::uint32_t end_before = compact->end;
    const std::uint32_t begin_before = compact->begin;
    const std::uint32_t delta = static_cast<std::uint32_t>(
        (static_cast<std::int32_t>(end_before - begin_before) >> 3) << 3);
    compact->end = end_before - delta;
}
} // namespace porsche

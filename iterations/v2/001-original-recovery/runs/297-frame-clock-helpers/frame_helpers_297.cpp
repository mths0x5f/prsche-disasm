#include "frame_helpers_297.hpp"

namespace porsche {

std::uint32_t __cdecl frame_clock_predicate_0046d960() {
    const VectorHeader* vec = frame_clock_vector_00628178;
    return static_cast<std::uint32_t>(vec->end - vec->begin);
}

VectorHeader* __cdecl frame_clock_get_items_0046d9b0() {
    return frame_clock_items_vector_00628168;
}

void __cdecl frame_clock_adjust_rate_004659e0(std::uint32_t channel_index, std::uint32_t rate) {
    channel_timer_006280f0 = 0u;
    channel_timer_006280e0 = 0u;
    channel_timer_006280e4 = 0u;
    channel_timer_00606ad4 = 0u;
    channel_timer_006280ec = 0u;
    channel_timer_006280e8 = 0u;
    channel_timer_00628100 = 0u;
    channel_timer_006280fc = 0u;
    channel_timer_006280f8 = 0u;

    if ((global_channel_states_00627f40[channel_index].flags & 1u) == 0u) {
        channel_init_or_reset_00465790(channel_index, rate);
    }
}

void __cdecl application_main_function_00471b60() {
    global_render_context_00628960->step_00487e20();
}

void __cdecl application_main_function_004a54e0() {
    platform_flush_0059eb20();
}

void __cdecl application_main_function_004a54b0() {
    flush_subsystem_004b7070();
    SubsystemContext_00628c70* sub = global_subsystem_00628c70;
    if (sub != nullptr) {
        sub->release_0048ff30();
        memory_free_0059f050(sub);
        global_subsystem_00628c70 = nullptr;
    }
}

} // namespace porsche

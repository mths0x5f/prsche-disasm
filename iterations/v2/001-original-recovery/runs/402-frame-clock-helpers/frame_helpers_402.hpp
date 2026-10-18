#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// -----------------------------------------------------------------------------
// Functions 1 & 2: 0046d960 (17 PE bytes) and 0046d9b0 (6 PE bytes)
// Frame clock dynamic array size predicate and item buffer accessor.
// -----------------------------------------------------------------------------
struct VectorHeader {
    std::uint32_t* begin;
    std::uint32_t* end;
    std::uint32_t* capacity;
};

extern VectorHeader* frame_clock_vector_00628178;
extern VectorHeader* frame_clock_items_vector_00628168;

std::uint32_t __cdecl frame_clock_predicate_0046d960();
VectorHeader* __cdecl frame_clock_get_items_0046d9b0();

// -----------------------------------------------------------------------------
// Function 3: 004659e0 (116 PE bytes)
// Frame rate timer reset & channel rate initialization dispatch.
// -----------------------------------------------------------------------------
struct ChannelState_00627f40 {
    std::uint8_t flags;
    std::uint8_t pad[0x10b]; // stride 268 = 0x10c bytes
};

extern ChannelState_00627f40 global_channel_states_00627f40[16];

extern std::uint32_t channel_timer_006280f0;
extern std::uint32_t channel_timer_006280e0;
extern std::uint32_t channel_timer_006280e4;
extern std::uint32_t channel_timer_00606ad4;
extern std::uint32_t channel_timer_006280ec;
extern std::uint32_t channel_timer_006280e8;
extern std::uint32_t channel_timer_00628100;
extern std::uint32_t channel_timer_006280fc;
extern std::uint32_t channel_timer_006280f8;

void __cdecl channel_init_or_reset_00465790(std::uint32_t channel_index, std::uint32_t rate);
void __cdecl frame_clock_adjust_rate_004659e0(std::uint32_t channel_index, std::uint32_t rate);

// -----------------------------------------------------------------------------
// Function 4: 00471b60 (11 PE bytes)
// Render context step forwarder from app_main.
// -----------------------------------------------------------------------------
struct RenderContext_00628960 {
    void __thiscall step_00487e20();
};
extern RenderContext_00628960* global_render_context_00628960;
void __cdecl application_main_function_00471b60();

// -----------------------------------------------------------------------------
// Function 5: 004a54e0 (5 PE bytes)
// Platform flush thunk forwarder from app_main.
// -----------------------------------------------------------------------------
void __cdecl platform_flush_0059eb20();
void __cdecl application_main_function_004a54e0();

// -----------------------------------------------------------------------------
// Function 6: 004a54b0 (44 PE bytes)
// Subsystem cleanup & release sequence from app_main.
// -----------------------------------------------------------------------------
struct SubsystemContext_00628c70 {
    std::uint32_t dummy;
    void __thiscall release_0048ff30();
};
extern SubsystemContext_00628c70* global_subsystem_00628c70;

void __cdecl flush_subsystem_004b7070();
void __cdecl memory_free_0059f050(void* ptr);

void __cdecl application_main_function_004a54b0();

} // namespace porsche

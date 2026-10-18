#pragma once

#include "porsche/application_main.hpp"
#include <cstdint>

namespace porsche {

// Target function 00413ea0 (296 body bytes in Porsche.exe)
// Dispatches simulation clock & frame step updates based on frame mode 005e99f4.
void __cdecl application_main_function_00413ea0();

// Global data cells touched by 00413ea0
extern std::uint32_t frame_clock_mode_005e99f4;
extern std::uint32_t frame_clock_counter_005e99f8;
extern std::uint32_t frame_clock_flag_005e99fc;
extern std::uint32_t frame_clock_step_accum_005e9a00;
extern std::uint32_t frame_clock_substep_005e9a04;

extern std::uint32_t frame_clock_rate_00606850;
extern std::uint32_t frame_clock_subticks_00606854;
extern std::uint32_t frame_clock_ticks_00606858;
extern std::uint32_t frame_clock_flags_00606860;
extern std::uint32_t frame_clock_state_00606864;
extern std::uint32_t frame_clock_var_00606868;
extern std::uint32_t frame_clock_var_0060686c;
extern std::uint32_t frame_clock_var_00606870;

// Arena buffer 005ed848 (0x6400 * 4 = 0x19000 bytes)
extern std::uint32_t frame_clock_arena_005ed848[0x6400];

// Session state 006573e8 and system tick cell 0065741c
extern std::uint32_t frame_clock_session_state_006573e8;
extern std::uint32_t frame_clock_tick_cell_0065741c;

// Context entity vector (count at 005e8bfc, table pointers at 005e8c00)
struct FrameClockEntityContext {
    std::uint8_t pad_00[0x10e4];
    std::uint32_t clock_value_10e4;
};

extern std::int32_t frame_clock_entity_count_005e8bfc;
extern FrameClockEntityContext* frame_clock_entities_005e8c00[64];

// External callee contracts
std::uint32_t __cdecl frame_clock_predicate_0046d960();
std::uint32_t __cdecl frame_clock_sample_time_0046d890();
void __cdecl frame_clock_dispatch_step_00413960(std::uint32_t clock_val);
void __cdecl frame_clock_adjust_rate_004659e0(std::uint32_t zero, std::uint32_t step);

} // namespace porsche

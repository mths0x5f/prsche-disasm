// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Run 429: corrected copy of Run 401's 00413ea0. Two changes, both from the
// original and the upstream review of PR 4:
//  - the entity count 005e8bfc is re-read after every 00413960 call
//    (00413f29 mov eax,[005e8bfc]; 00413f35 cmp edi,eax), not cached;
//  - 005e99f4 and 006573e8 use their canonical owners (application_main.hpp)
//    instead of new names for the same cells.
#include "../401-frame-clock-dispatch/frame_clock_401.hpp"
#include "porsche/application_main.hpp"
#include <cstring>

namespace porsche {

void __cdecl application_main_function_00413ea0() {
    const std::uint32_t mode = global_005e99f4;

    if (mode == 0u || mode == 1u) {
        // Mode 0 or 1: Clear the large 0x19000-byte arena (0x6400 DWORDs via rep stosd in original PE), reset counters, and record tick cell
        const std::uint32_t tick = frame_clock_tick_cell_0065741c;
        for (std::size_t i = 0; i < sizeof(frame_clock_arena_005ed848) / sizeof(std::uint32_t); ++i) {
            frame_clock_arena_005ed848[i] = 0u;
        }
        frame_clock_counter_005e99f8 = 0u;
        frame_clock_flag_005e99fc = 0u;
        frame_clock_ticks_00606858 = tick;

        frame_clock_step_accum_005e9a00 = 0u;
        frame_clock_substep_005e9a04 = 0u;
        return;
    }

    if (static_cast<std::int32_t>(mode) < 2) {
        // Mode < 2 (negative): early exit clearing substep accumulators
        frame_clock_step_accum_005e9a00 = 0u;
        frame_clock_substep_005e9a04 = 0u;
        return;
    }

    // Mode >= 2: Active simulation frame clock step
    frame_clock_flag_005e99fc = 0u;
    frame_clock_flags_00606860 = 0u;
    frame_clock_state_00606864 = 2u;
    frame_clock_var_00606868 = 0u;
    frame_clock_var_0060686c = 0u;
    frame_clock_var_00606870 = 0u;

    if (frame_clock_predicate_0046d960() != 0u) {
        if (global_006573e8 == 9u) {
            frame_clock_adjust_rate_004659e0(0u, 10u);
            frame_clock_rate_00606850 = 20u;
        } else {
            // 00413efd..00413f37: the count is read before the loop and again after
            // each dispatch; the comparison uses the fresh value.
            if (frame_clock_entity_count_005e8bfc > 0) {
                std::int32_t i = 0;
                do {
                    const std::uint32_t sample = frame_clock_sample_time_0046d890();
                    auto* entity = frame_clock_entities_005e8c00[i];
                    entity->clock_value_10e4 = sample;
                    const std::uint32_t step_val = entity->clock_value_10e4;
                    frame_clock_dispatch_step_00413960(step_val);
                    ++i;
                } while (i < frame_clock_entity_count_005e8bfc);
            }
            frame_clock_rate_00606850 = 20u;
        }
    } else {
        frame_clock_rate_00606850 = 10u;
        frame_clock_adjust_rate_004659e0(0u, 10u);
    }

    const std::uint32_t tick = frame_clock_tick_cell_0065741c;
    frame_clock_step_accum_005e9a00 = 0u;
    frame_clock_subticks_00606854 = 0u;
    frame_clock_ticks_00606858 = tick;
    frame_clock_substep_005e9a04 = 0u;
}

} // namespace porsche

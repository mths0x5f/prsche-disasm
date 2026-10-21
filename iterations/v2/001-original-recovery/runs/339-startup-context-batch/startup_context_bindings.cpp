#include "startup_context_bindings.hpp"

namespace porsche {

// Existing Run173 body at 00565030; this is the startup caller's ABI name.
void __cdecl startup_capacity_00565030(std::uint32_t interval) {
    timer_setup_00565030(interval);
}

// Existing Run143 body at 004237d0; preserve the full pointer/size/mode tuple.
void __cdecl game_setup_movie_delta_004237d0(
    void* begin, std::uint32_t bytes, std::uint32_t mode) {
    application_context_clear_004237d0(begin, bytes, mode);
}

} // namespace porsche

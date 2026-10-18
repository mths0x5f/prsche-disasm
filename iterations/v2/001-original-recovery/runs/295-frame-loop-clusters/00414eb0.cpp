#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __cdecl application_main_function_00414eb0() {
    frame_reset_word_00606ab8 = 1u;
    frame_reset_byte_00656858 = 0u;
    frame_reset_word_00606a8c = 0u;
    frame_reset_word_00606a90 = 0u;
    frame_reset_word_00606a98 = 0u;
    frame_reset_word_00606a9c = 0u;
    frame_reset_word_00606aa0 = 0u;
    startup_sequence_word_00606ac0 = 0u;
    startup_sequence_word_00606ac4 = 0u;
    application_state_006573e8.words_[(0x00657e6cu - application_state_base_va) / 4u] = 0u;
    frame_reset_service_004a4780(
        application_state_006573e8.words_[(0x00657a34u - application_state_base_va) / 4u]);
    frame_reset_service_0044fd00(
        application_state_006573e8.words_[(0x00657a34u - application_state_base_va) / 4u]);
    frame_reset_service_004030b0();
    frame_reset_service_004069d0();
    frame_reset_service_004066d0();
    frame_reset_service_004110a0();
    frame_reset_service_00406710();
    frame_reset_service_004069e0();
    frame_reset_service_004690a0();
    frame_reset_service_00412150();
    const std::uint32_t copied = frame_reset_source_005e99b8;
    frame_reset_word_006280f0 = 0u;
    frame_reset_word_00606ac8 = copied;
    frame_reset_word_006280ec = 0u;
    frame_reset_word_006280e8 = 0u;
    frame_reset_word_00628100 = 0u;
    frame_reset_word_006280fc = 0u;
    frame_reset_word_006280f8 = 0u;
}
} // namespace porsche

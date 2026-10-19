cmake_minimum_required(VERSION 3.20)
project(porsche_unified_game_integration_429 LANGUAGES CXX ASM_MASM)

# Run 429: one game graph. Upstream's chain (298 -> 306 -> 309 -> 310 -> 314 ->
# 318 -> 321) is the base. The fork's chain (417 -> 418/419 -> 420 -> 424 ->
# 426 -> 428) is re-applied on top as explicit lists instead of its old 298 base.
# Left out on purpose (each stays an explicit boundary until fixed on its own):
#  - Run 411's TU: wrong 0048cdf0/0048dcb0/0048e1a0 packet layout and zeroed
#    immediates (upstream review of PR 19, items 4-6);
#  - Runs 404/405/407/408/409 TUs: they define second owners of VAs that already
#    have canonical ABIs (for example 005a177b), the items upstream queued in
#    PRs 6/10/11/14/15;
#  - Run 418: its arena view splits 006af3b4..006af3f4 across separate canonical
#    cells, so index 16 does not reach the 006af3f4 guard (PR 19 review, item 2);
#  - the 417/420 bridge files: free-cdecl stand-ins for thiscall methods and
#    zero-filled heap providers; entry_bridges_429.cpp keeps only proven aliases;
#  - sources whose VA upstream already owns (310, 311, 312, 313).
# Corrected copies replace Run 401's 00413ea0 and Run 419's frame root lifecycle.
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../321-simd-fill-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-321")

set(RUNS "${CMAKE_CURRENT_LIST_DIR}/..")
target_include_directories(porsche_game_entry_bridges PRIVATE
    "${RUNS}/400-frame-loop-clusters"
    "${RUNS}/401-frame-clock-dispatch"
    "${RUNS}/419-frame-root-lifecycle"
    "${RUNS}/421-audio-backend-lock-pool"
    "${RUNS}/422-audio-channel-voice-lookup"
    "${RUNS}/425-audio-voice-stop")

# Run 400 bodies not already integrated by upstream Run 310 (00412030, 00425780).
target_sources(porsche_game_entry_bridges PRIVATE
    "${RUNS}/400-frame-loop-clusters/00414eb0.cpp"
    "${RUNS}/400-frame-loop-clusters/00465e20.cpp"
    "${RUNS}/400-frame-loop-clusters/00467740.cpp"
    "${RUNS}/400-frame-loop-clusters/0047f190.cpp"
    "${RUNS}/400-frame-loop-clusters/004acb80.cpp"
    "${RUNS}/400-frame-loop-clusters/004b7140.cpp"
    "${RUNS}/400-frame-loop-clusters/00514990.cpp"
    "${RUNS}/400-frame-loop-clusters/005338d0.cpp"
    "${RUNS}/400-frame-loop-clusters/00538d80.cpp"
    "${RUNS}/400-frame-loop-clusters/00539eb0.cpp"
    "${RUNS}/400-frame-loop-clusters/00540420.cpp"
    "${RUNS}/400-frame-loop-clusters/00563bd0.cpp"
    "${RUNS}/400-frame-loop-clusters/00563c30.cpp"
    "${RUNS}/400-frame-loop-clusters/00563c70.cpp"
    "${RUNS}/400-frame-loop-clusters/00563cc0.cpp"
    "${RUNS}/400-frame-loop-clusters/00563d30.cpp"
    "${RUNS}/400-frame-loop-clusters/00564700.cpp"
    "${RUNS}/400-frame-loop-clusters/00564750.cpp"
    "${RUNS}/400-frame-loop-clusters/00565d60.cpp"
    "${RUNS}/421-audio-backend-lock-pool/audio_backend_lock_pool_421.cpp"
    "${RUNS}/422-audio-channel-voice-lookup/audio_channel_voice_lookup_422.cpp"
    "${RUNS}/425-audio-voice-stop/audio_voice_stop_425.cpp"
    "${RUNS}/427-audio-backend-state-block/audio_backend_state_427.asm"
    "${CMAKE_CURRENT_LIST_DIR}/frame_clock_00413ea0_429.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/frame_root_lifecycle_429.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/frame_root_block_429.asm"
    "${CMAKE_CURRENT_LIST_DIR}/entry_bridges_429.cpp")
set_source_files_properties("${RUNS}/427-audio-backend-state-block/audio_backend_state_427.asm"
    "${CMAKE_CURRENT_LIST_DIR}/frame_root_block_429.asm"
    PROPERTIES COMPILE_OPTIONS "/safeseh")

# Run 427's block owns application_audio_device_state_006b48c0 in the game target.
target_compile_definitions(porsche_original PRIVATE PORSCHE_AUDIO_STATE_BLOCK=1)

# Run 424: input Win32 adapters.
target_sources(porsche_platform_win32 PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../../source/platform/win32_input.cpp")
target_link_libraries(porsche_original_game_link PRIVATE winmm)

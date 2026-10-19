cmake_minimum_required(VERSION 3.20)
project(porsche_audio_state_block_integration_428 LANGUAGES CXX ASM_MASM)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../426-audio-voice-stop-game-integration"
                 "${CMAKE_BINARY_DIR}/integration-426")
# Run 427: the audio module's zero-initialized storage 006b00c0..006b4a44 as one
# block with original offsets. It owns application_audio_device_state_006b48c0,
# so the canonical C++ definition is compiled out for the game target.
target_compile_definitions(porsche_original PRIVATE PORSCHE_AUDIO_STATE_BLOCK=1)
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../427-audio-backend-state-block/audio_backend_state_427.asm")
set_source_files_properties(
    "${CMAKE_CURRENT_LIST_DIR}/../427-audio-backend-state-block/audio_backend_state_427.asm"
    PROPERTIES COMPILE_OPTIONS "/safeseh")

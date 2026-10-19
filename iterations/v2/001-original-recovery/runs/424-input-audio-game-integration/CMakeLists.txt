cmake_minimum_required(VERSION 3.20)
project(porsche_input_audio_integration_424 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../420-game-link-integration"
                 "${CMAKE_BINARY_DIR}/link-420")
# Runs 421 and 422: audio backend lock/pool and channel/voice lookup.
target_include_directories(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../421-audio-backend-lock-pool"
    "${CMAKE_CURRENT_LIST_DIR}/../422-audio-channel-voice-lookup"
)
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../421-audio-backend-lock-pool/audio_backend_lock_pool_421.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../422-audio-channel-voice-lookup/audio_channel_voice_lookup_422.cpp"
)
# Input Win32 adapters (GetModuleHandleA, DirectInputCreateA, GetKeyboardType,
# joyGetNumDevs, joyGetDevCapsA); Run 423's _getstate is already in the graph.
target_sources(porsche_platform_win32 PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../../source/platform/win32_input.cpp")
target_link_libraries(porsche_original_game_link PRIVATE winmm)

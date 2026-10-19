cmake_minimum_required(VERSION 3.20)
project(porsche_audio_voice_stop_integration_426 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../424-input-audio-game-integration"
                 "${CMAKE_BINARY_DIR}/integration-424")
# Run 425: audio voice stop tree.
target_include_directories(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../425-audio-voice-stop")
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../425-audio-voice-stop/audio_voice_stop_425.cpp")

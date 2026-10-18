cmake_minimum_required(VERSION 3.20)
project(porsche_game_startup_followup_293 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../289-game-startup-link"
                 "${CMAKE_BINARY_DIR}/entry-289")
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../291-frame-resolver/004898f0.cpp")
# Batch only the actual game target's large source project and added packet.
# No ALL_BUILD/probe sweep is requested by this entry point.
target_compile_options(porsche_original PRIVATE /MP6)
target_compile_options(porsche_game_entry_bridges PRIVATE /MP6)

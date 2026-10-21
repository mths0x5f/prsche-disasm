cmake_minimum_required(VERSION 3.20)
project(porsche_startup_context_batch LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../335-resource-open-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-335")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/startup_context_bindings.cpp")

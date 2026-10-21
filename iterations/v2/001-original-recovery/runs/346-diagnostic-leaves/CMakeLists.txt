cmake_minimum_required(VERSION 3.20)
project(porsche_diagnostic_leaves LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../345-diagnostic-devices"
                 "${CMAKE_BINARY_DIR}/entry-345")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/diagnostic_leaves.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/platform_debug_output.cpp")

cmake_minimum_required(VERSION 3.20)
project(porsche_heap_context_state LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../339-startup-context-batch"
                 "${CMAKE_BINARY_DIR}/entry-339")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../../source/recovered/Porsche.exe/application_heap_state.cpp")

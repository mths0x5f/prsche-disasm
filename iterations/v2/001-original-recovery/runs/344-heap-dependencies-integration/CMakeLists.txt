cmake_minimum_required(VERSION 3.20)
project(porsche_heap_dependencies LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../340-heap-context-state"
                 "${CMAKE_BINARY_DIR}/entry-340")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../341-heap-shutdown-dependencies/heap_shutdown.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/../342-heap-live-callbacks/heap_callbacks.cpp")

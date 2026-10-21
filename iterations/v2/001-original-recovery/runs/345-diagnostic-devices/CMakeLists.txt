cmake_minimum_required(VERSION 3.20)
project(porsche_diagnostic_devices LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../344-heap-dependencies-integration"
                 "${CMAKE_BINARY_DIR}/entry-344")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/diagnostic_devices.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/fill_binding.cpp")

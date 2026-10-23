cmake_minimum_required(VERSION 3.20)
project(porsche_diagnostic_parsers LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../346-diagnostic-leaves"
                 "${CMAKE_BINARY_DIR}/entry-346")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/diagnostic_parsers.cpp")

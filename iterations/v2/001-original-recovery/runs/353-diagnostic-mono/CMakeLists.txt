cmake_minimum_required(VERSION 3.20)
project(porsche_diagnostic_mono_353 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../351-heap-lock-bindings" entry-351)
target_sources(porsche_game_entry_bridges PRIVATE diagnostic_mono.cpp)

cmake_minimum_required(VERSION 3.20)
project(porsche_startup_bindings_363 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../359-render-settings-bindings" entry-359)
target_sources(porsche_game_entry_bridges PRIVATE startup_binding.cpp)

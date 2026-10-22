cmake_minimum_required(VERSION 3.20)
project(porsche_render_bindings_356 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../354-copy-backends" entry-354)
target_sources(porsche_game_entry_bridges PRIVATE render_binding.cpp)

cmake_minimum_required(VERSION 3.20)
project(porsche_render_descriptor_374 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../373-snapshot-async-integration" entry-373)
target_sources(porsche_game_entry_bridges PRIVATE render_descriptor.cpp)

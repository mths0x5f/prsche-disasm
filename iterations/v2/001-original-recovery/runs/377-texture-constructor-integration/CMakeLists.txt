cmake_minimum_required(VERSION 3.20)
project(porsche_texture_constructor_377 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../374-render-descriptor" entry-374)
target_sources(porsche_game_entry_bridges PRIVATE
    ../375-texture-constructor/texture_constructor.cpp
    ../376-heap-largest/heap_largest.cpp)

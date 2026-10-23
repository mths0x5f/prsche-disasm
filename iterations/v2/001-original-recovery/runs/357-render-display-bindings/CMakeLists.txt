cmake_minimum_required(VERSION 3.20)
project(porsche_render_display_bindings_357 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../356-render-bindings" entry-356)
target_sources(porsche_game_entry_bridges PRIVATE render_binding.cpp)

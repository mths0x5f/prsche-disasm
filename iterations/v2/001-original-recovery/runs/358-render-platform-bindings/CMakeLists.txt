cmake_minimum_required(VERSION 3.20)
project(porsche_render_platform_bindings_358 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../357-render-display-bindings" entry-357)
target_sources(porsche_game_entry_bridges PRIVATE render_binding.cpp)

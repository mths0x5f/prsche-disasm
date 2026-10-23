cmake_minimum_required(VERSION 3.20)
project(porsche_render_settings_bindings_359 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../358-render-platform-bindings" entry-358)
target_sources(porsche_game_entry_bridges PRIVATE render_settings_binding.cpp)

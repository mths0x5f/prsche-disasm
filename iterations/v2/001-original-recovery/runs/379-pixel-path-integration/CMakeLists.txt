cmake_minimum_required(VERSION 3.20)
project(porsche_pixel_path_379 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../377-texture-constructor-integration" entry-377)
target_sources(porsche_game_entry_bridges PRIVATE
    ../378-buffer-select/buffer_select.cpp
    ../380-pixel-helpers/pixel_helpers.cpp
    ../381-pixel-draw-helpers/pixel_draw_helpers.cpp)

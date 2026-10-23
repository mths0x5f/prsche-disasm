cmake_minimum_required(VERSION 3.20)
project(porsche_startup_render_384 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../379-pixel-path-integration" entry-379)
target_sources(porsche_game_entry_bridges PRIVATE
    ../382-rectangle/rectangle.cpp
    ../383-startup-input-imports/startup_input_imports.cpp
    ../221-readonly-scalar-storage/original_scalars.cpp)
target_link_libraries(porsche_game_entry_bridges PUBLIC winmm.lib)

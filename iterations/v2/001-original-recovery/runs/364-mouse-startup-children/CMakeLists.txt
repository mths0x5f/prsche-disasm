cmake_minimum_required(VERSION 3.20)
project(porsche_mouse_startup_children_364 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../361-startup-device-pool" entry-361)
target_sources(porsche_game_entry_bridges PRIVATE startup_mouse_children.cpp)

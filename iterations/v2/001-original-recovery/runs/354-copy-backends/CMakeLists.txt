cmake_minimum_required(VERSION 3.20)
project(porsche_copy_backends_354 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../353-diagnostic-mono" entry-353)
target_sources(porsche_game_entry_bridges PRIVATE copy_backends.cpp)

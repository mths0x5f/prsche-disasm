cmake_minimum_required(VERSION 3.20)
project(porsche_startup_device_pool_361 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../363-startup-bindings" entry-363)
target_sources(porsche_game_entry_bridges PRIVATE startup_device.cpp startup_pool.cpp)

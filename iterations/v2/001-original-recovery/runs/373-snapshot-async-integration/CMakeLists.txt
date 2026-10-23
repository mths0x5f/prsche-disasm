cmake_minimum_required(VERSION 3.20)
project(porsche_snapshot_async_373 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../370-input-startup-integration" entry-370)
target_sources(porsche_game_entry_bridges PRIVATE
    ../371-cursor-snapshot/cursor_snapshot.cpp
    ../372-async-callbacks/async_callbacks.cpp)

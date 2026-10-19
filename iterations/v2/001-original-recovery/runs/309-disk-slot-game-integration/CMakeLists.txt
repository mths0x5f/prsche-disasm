cmake_minimum_required(VERSION 3.20)
project(porsche_disk_slot_game_integration_309 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../306-file-pool-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-306")
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../307-disk-slot-shutdown/005918c0.cpp")

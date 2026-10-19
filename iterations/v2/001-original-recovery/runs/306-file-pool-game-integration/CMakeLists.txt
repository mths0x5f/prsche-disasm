cmake_minimum_required(VERSION 3.20)
project(porsche_file_pool_game_integration_306 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../298-frame-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-298")
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../305-file-pool-shutdown/005678f0.cpp")

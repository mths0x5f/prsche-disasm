cmake_minimum_required(VERSION 3.20)
project(porsche_game_link_integration_420 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../417-game-entry-integration"
                 "${CMAKE_BINARY_DIR}/entry-417")
target_include_directories(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../418-heap-shutdown-closure"
    "${CMAKE_CURRENT_LIST_DIR}/../419-frame-root-lifecycle"
)
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/entry_bridges_420.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../418-heap-shutdown-closure/heap_shutdown_418.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../419-frame-root-lifecycle/frame_root_lifecycle_419.cpp"
)

cmake_minimum_required(VERSION 3.20)
project(porsche_input_modes_game_integration_324 LANGUAGES CXX)
# PR22 updates the canonical input_state.cpp already in the game graph.
# PR23 audio packets and all native test fixtures remain outside production.
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../321-simd-fill-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-321")

cmake_minimum_required(VERSION 3.20)
project(porsche_scalar_fill_game_integration_318 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../314-pr7-pr9-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-314")
# One original scalar body and its existing void dispatcher adapter.
# Native oracle bytes and fixture providers are excluded.
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../317-scalar-fill-backend/005b0980.cpp")

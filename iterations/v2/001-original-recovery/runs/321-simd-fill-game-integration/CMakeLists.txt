cmake_minimum_required(VERSION 3.20)
project(porsche_simd_fill_game_integration_321 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../318-scalar-fill-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-318")
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../319-mmx-fill-backend/005b0a40.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../320-sse-fill-backend/005b0b00.cpp")
# fill_chain_fixture.cpp and generated original_bodies.hpp are native-test only.

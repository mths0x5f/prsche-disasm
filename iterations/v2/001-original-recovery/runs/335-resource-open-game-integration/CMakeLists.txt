cmake_minimum_required(VERSION 3.20)
project(porsche_resource_open_game_integration_335 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../332-resource-chain-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-332")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../334-resource-open/resource_open_334.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/../338-search-abi-bindings/search_bindings_338.cpp")

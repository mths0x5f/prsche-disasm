cmake_minimum_required(VERSION 3.20)
project(porsche_resource_device_game_integration_328 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../324-input-modes-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-324")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../326-resource-exists/resource_exists_326.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/../327-resource-open-callback-evidence/resource_device_327.cpp")

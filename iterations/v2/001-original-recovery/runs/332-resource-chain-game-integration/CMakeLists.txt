cmake_minimum_required(VERSION 3.20)
project(porsche_resource_chain_game_integration_332 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../328-resource-device-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-328")
target_sources(porsche_game_entry_bridges PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../329-resource-constructor/resource_constructor_329.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/../331-drive-letter/drive_letter_331.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/../../source/recovered/Porsche.exe/formatter_search.cpp")

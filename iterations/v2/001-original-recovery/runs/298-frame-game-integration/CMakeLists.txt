cmake_minimum_required(VERSION 3.20)
project(porsche_frame_game_integration_298 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../293-game-startup-followup"
                 "${CMAKE_BINARY_DIR}/entry-293")
# Only reviewed game sources; private fixtures and original-byte test oracles
# are deliberately absent from the actual executable's dependency graph.
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../295-frame-helpers/00423840.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../295-frame-helpers/00482e50.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../297-frame-action/00476170.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../299-frame-action-children/00476710.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../300-frame-float-data/frame_floats_300.cpp")

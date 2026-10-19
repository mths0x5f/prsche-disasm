cmake_minimum_required(VERSION 3.20)
project(porsche_pr_intake_310 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../309-disk-slot-game-integration"
                 "${CMAKE_BINARY_DIR}/entry-309")
# Only the freshly compared PR3 bodies and the selective PR4 helpers are added.
# Original-byte oracles, fixture providers, other Run400 bodies, and the
# duplicate 00471b60 from PR4 are excluded from the real game graph.
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../400-frame-loop-clusters/00412030.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../400-frame-loop-clusters/00425780.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../311-pr4-shutdown-helpers/shutdown_helpers_311.cpp")

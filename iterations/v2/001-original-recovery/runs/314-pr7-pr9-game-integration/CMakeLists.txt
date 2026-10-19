cmake_minimum_required(VERSION 3.20)
project(porsche_pr7_pr9_game_integration_314 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../310-pr-intake-integration"
                 "${CMAKE_BINARY_DIR}/entry-310")
# Selective PR intake: canonical dispatcher and resource opener only.
# Private test oracles/providers and the other duplicate405/407 bodies stay out.
target_sources(porsche_game_entry_bridges PRIVATE
    "${CMAKE_CURRENT_LIST_DIR}/../312-pr7-fill-dispatch/0053c290.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../313-pr9-resource-open/resource_open_313.cpp")

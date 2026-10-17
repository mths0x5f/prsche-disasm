cmake_minimum_required(VERSION 3.20)
project(porsche_game_startup_link_289 LANGUAGES CXX)

if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "The original game entry requires MSVC Win32/x86")
endif()

get_filename_component(ITERATION_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_subdirectory("${ITERATION_ROOT}" "${CMAKE_BINARY_DIR}/common")
add_subdirectory("${ITERATION_ROOT}/runs/102-original-game-link"
                 "${CMAKE_BINARY_DIR}/game-entry")

# Explicit reviewed game sources only. Private fixture providers never enter
# this list. The normal executable target and its entry remain those of Run102.
include("${CMAKE_CURRENT_LIST_DIR}/bridge-sources.cmake")
add_library(porsche_game_entry_bridges STATIC ${PORSCHE_GAME_ENTRY_BRIDGE_SOURCES})
target_include_directories(porsche_game_entry_bridges PRIVATE
    "${ITERATION_ROOT}/source/include")
target_compile_features(porsche_game_entry_bridges PRIVATE cxx_std_17)
target_compile_definitions(porsche_game_entry_bridges PRIVATE
    NOMINMAX WIN32_LEAN_AND_MEAN _CRT_SECURE_NO_WARNINGS)
target_compile_options(porsche_game_entry_bridges PRIVATE /W4 /EHsc /permissive-)
target_link_libraries(porsche_original_game_link PRIVATE porsche_game_entry_bridges)

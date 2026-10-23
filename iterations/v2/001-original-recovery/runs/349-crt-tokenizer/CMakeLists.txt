cmake_minimum_required(VERSION 3.20)
project(porsche_crt_tokenizer_349 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../348-diagnostic-parsers" entry-348)
target_sources(porsche_game_entry_bridges PRIVATE crt_tokenizer.cpp)

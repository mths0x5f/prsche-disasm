cmake_minimum_required(VERSION 3.20)
project(porsche_heap_lock_bindings_351 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../349-crt-tokenizer" entry-349)
target_sources(porsche_game_entry_bridges PRIVATE lock_binding.cpp)

cmake_minimum_required(VERSION 3.24)
project(formatter_search_172 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run172 requires MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(formatter_search_probe
  "${ROOT}/source/recovered/formatter_search_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/formatter_text.cpp"
  "${ROOT}/source/recovered/Porsche.exe/formatter_search.cpp")
target_include_directories(formatter_search_probe PRIVATE "${ROOT}/source/include")
target_compile_features(formatter_search_probe PRIVATE cxx_std_17)
target_compile_options(formatter_search_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(formatter_search_probe PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
option(PORSCHE_SEARCH_READ_TRACE "Observe ordered original input reads" ON)
if(PORSCHE_SEARCH_READ_TRACE)
  target_compile_definitions(formatter_search_probe PRIVATE PORSCHE_FORMATTER_TEXT_TRACE PORSCHE_FORMATTER_SEARCH_TRACE)
endif()
set_target_properties(formatter_search_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

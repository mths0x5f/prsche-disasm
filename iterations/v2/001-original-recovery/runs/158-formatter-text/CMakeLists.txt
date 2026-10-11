cmake_minimum_required(VERSION 3.24)
project(formatter_text_158 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run158 requires MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(formatter_text_probe
  "${ROOT}/source/recovered/formatter_text_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/formatter_text.cpp")
target_include_directories(formatter_text_probe PRIVATE "${ROOT}/source/include")
target_compile_features(formatter_text_probe PRIVATE cxx_std_17)
target_compile_options(formatter_text_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(formatter_text_probe PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN PORSCHE_FORMATTER_TEXT_TRACE)
set_target_properties(formatter_text_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

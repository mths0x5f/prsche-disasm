cmake_minimum_required(VERSION 3.24)
project(formatter_float_helpers_147 LANGUAGES CXX)
if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4 OR NOT MSVC)
  message(FATAL_ERROR "Run147 requires Win32 x86 MSVC")
endif()
add_executable(formatter_float_helpers_probe
  ../../source/recovered/formatter_float_helpers_probe.cpp
  ../../source/recovered/Porsche.exe/formatter_float_helpers.cpp)
target_include_directories(formatter_float_helpers_probe PRIVATE ../../source/include)
target_compile_features(formatter_float_helpers_probe PRIVATE cxx_std_17)
target_compile_options(formatter_float_helpers_probe PRIVATE /W4 /permissive- /EHsc)

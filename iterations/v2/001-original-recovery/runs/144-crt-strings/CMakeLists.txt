cmake_minimum_required(VERSION 3.24)
project(formatter_strings_144 LANGUAGES CXX)
if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4 OR NOT MSVC)
  message(FATAL_ERROR "Run144 requires Win32 x86 MSVC")
endif()
add_executable(formatter_strings_probe
  ../../source/recovered/formatter_strings_probe.cpp
  ../../source/recovered/Porsche.exe/formatter_strings.cpp)
target_include_directories(formatter_strings_probe PRIVATE ../../source/include)
target_compile_features(formatter_strings_probe PRIVATE cxx_std_17)
target_compile_options(formatter_strings_probe PRIVATE /W4 /permissive- /EHsc)
target_compile_definitions(formatter_strings_probe PRIVATE PORSCHE_FORMATTER_MEMORY_TRACE=1)
add_executable(formatter_strings_production_probe
  ../../source/recovered/formatter_strings_probe.cpp
  ../../source/recovered/Porsche.exe/formatter_strings.cpp)
target_include_directories(formatter_strings_production_probe PRIVATE ../../source/include)
target_compile_features(formatter_strings_production_probe PRIVATE cxx_std_17)
target_compile_options(formatter_strings_production_probe PRIVATE /W4 /permissive- /EHsc)

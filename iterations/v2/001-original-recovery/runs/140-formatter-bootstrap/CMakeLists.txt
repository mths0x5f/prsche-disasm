cmake_minimum_required(VERSION 3.24)
project(formatter_bootstrap_140 LANGUAGES CXX)
if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4 OR NOT MSVC)
  message(FATAL_ERROR "Run140 requires Win32 x86 MSVC")
endif()
add_executable(formatter_bootstrap_probe
  ../../source/recovered/formatter_bootstrap_probe.cpp
  ../../source/recovered/Porsche.exe/formatter_bootstrap.cpp
  ../../source/recovered/Porsche.exe/formatter_runtime.cpp
  ../../source/recovered/Porsche.exe/formatter_runtime_storage.cpp)
target_include_directories(formatter_bootstrap_probe PRIVATE ../../source/include)
target_compile_features(formatter_bootstrap_probe PRIVATE cxx_std_17)
target_compile_definitions(formatter_bootstrap_probe PRIVATE _CRT_SECURE_NO_WARNINGS)
target_compile_options(formatter_bootstrap_probe PRIVATE /W4 /permissive- /EHsc)

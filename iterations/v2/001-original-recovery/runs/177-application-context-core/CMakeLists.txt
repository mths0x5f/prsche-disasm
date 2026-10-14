cmake_minimum_required(VERSION 3.24)
project(application_context_core_candidate_177 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run177 candidate requires MSVC Win32/x86")
endif()
# Compile-only candidate. Unresolved effects/address views stay unresolved.
add_library(application_context_core_candidate OBJECT
  ../../source/recovered/Porsche.exe/application_context_core_candidate.cpp)
target_include_directories(application_context_core_candidate PRIVATE ../../source/include)
target_compile_features(application_context_core_candidate PRIVATE cxx_std_17)
target_compile_options(application_context_core_candidate PRIVATE /W4 /EHsc /permissive-)

cmake_minimum_required(VERSION 3.24)
project(context_ranges_149 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run149 requires MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
foreach(name context_ranges_probe context_range_wrapper_probe)
  add_executable(${name}
    "${ROOT}/source/recovered/context_ranges_probe.cpp"
    "${ROOT}/source/recovered/Porsche.exe/context_ranges.cpp")
  target_include_directories(${name} PRIVATE "${ROOT}/source/include")
  target_compile_features(${name} PRIVATE cxx_std_17)
  target_compile_options(${name} PRIVATE /W4 /EHsc /permissive-)
  target_compile_definitions(${name} PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
  set_target_properties(${name} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()
# Private aggregate-forwarding proof supplies an explicit recording boundary
# at 00529c50. The normal target compiles its complete recovered body.
target_compile_definitions(context_range_wrapper_probe PRIVATE CONTEXT_RANGES_EXTERNAL_WALK)

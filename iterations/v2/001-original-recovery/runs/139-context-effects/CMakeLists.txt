cmake_minimum_required(VERSION 3.24)
project(context_effects_139 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run139 requires MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(context_effects_probe
  "${ROOT}/source/recovered/context_effects_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/context_effects.cpp")
target_include_directories(context_effects_probe PRIVATE "${ROOT}/source/include")
target_compile_features(context_effects_probe PRIVATE cxx_std_17)
target_compile_options(context_effects_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(context_effects_probe PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
set_target_properties(context_effects_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

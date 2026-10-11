cmake_minimum_required(VERSION 3.24)
project(context_services_150 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run150 requires MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(context_services_probe
  "${ROOT}/source/recovered/context_services_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/context_services.cpp")
target_include_directories(context_services_probe PRIVATE "${ROOT}/source/include")
target_compile_features(context_services_probe PRIVATE cxx_std_17)
target_compile_options(context_services_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(context_services_probe PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
set_target_properties(context_services_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

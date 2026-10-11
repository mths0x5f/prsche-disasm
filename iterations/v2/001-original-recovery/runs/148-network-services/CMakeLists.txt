cmake_minimum_required(VERSION 3.20)
project(network_services_148 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run148 requires native MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(network_services_probe
  "${ROOT}/source/recovered/network_services_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/network_services.cpp")
target_include_directories(network_services_probe PRIVATE "${ROOT}/source/include")
target_compile_features(network_services_probe PRIVATE cxx_std_17)
target_compile_definitions(network_services_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(network_services_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(network_services_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

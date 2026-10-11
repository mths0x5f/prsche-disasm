cmake_minimum_required(VERSION 3.20)
project(application_services_next_141 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run141 requires native MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(application_services_next_probe
  "${ROOT}/source/recovered/application_services_next_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/application_services_next.cpp"
  "${ROOT}/source/recovered/Porsche.exe/application_services.cpp"
  "${ROOT}/source/recovered/Porsche.exe/application_state.cpp"
  "${ROOT}/source/recovered/Porsche.exe/install_paths_storage.cpp")
target_include_directories(application_services_next_probe PRIVATE "${ROOT}/source/include")
target_compile_features(application_services_next_probe PRIVATE cxx_std_17)
target_compile_definitions(application_services_next_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(application_services_next_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(application_services_next_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

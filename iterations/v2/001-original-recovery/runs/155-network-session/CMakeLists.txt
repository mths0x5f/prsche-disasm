cmake_minimum_required(VERSION 3.20)
project(network_session_155 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "Run155 requires native MSVC Win32/x86")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(network_session_probe
  "${ROOT}/source/recovered/network_session_probe.cpp"
  "${ROOT}/source/recovered/Porsche.exe/network_session.cpp"
  "${ROOT}/source/recovered/Porsche.exe/network_services.cpp"
  "${ROOT}/source/recovered/Porsche.exe/network_cleanup.cpp"
  "${ROOT}/source/recovered/Porsche.exe/network_lifecycle.cpp"
  "${ROOT}/source/recovered/Porsche.exe/context_effects.cpp")
target_include_directories(network_session_probe PRIVATE "${ROOT}/source/include")
target_compile_features(network_session_probe PRIVATE cxx_std_17)
target_compile_definitions(network_session_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(network_session_probe PRIVATE /W4 /EHsc /permissive- /Gy)
target_link_options(network_session_probe PRIVATE /OPT:REF)
set_target_properties(network_session_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

cmake_minimum_required(VERSION 3.24)
project(formatter_error_integration_143 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
 message(FATAL_ERROR "MSVC Win32 required")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(formatter_error_integration_probe
 "${ROOT}/source/recovered/formatter_bootstrap_probe.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_bootstrap.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_strings.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_runtime.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_runtime_storage.cpp")
target_include_directories(formatter_error_integration_probe PRIVATE "${ROOT}/source/include")
target_compile_features(formatter_error_integration_probe PRIVATE cxx_std_17)
target_compile_options(formatter_error_integration_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(formatter_error_integration_probe PRIVATE PORSCHE_FORMATTER_CONNECTED_STRINGS=1 _CRT_SECURE_NO_WARNINGS)
set_target_properties(formatter_error_integration_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

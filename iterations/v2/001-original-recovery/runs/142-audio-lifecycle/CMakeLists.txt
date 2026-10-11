cmake_minimum_required(VERSION 3.24)
project(audio_lifecycle_142 LANGUAGES CXX)
if(NOT MSVC OR NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
 message(FATAL_ERROR "MSVC Win32 required")
endif()
set(ROOT "${CMAKE_CURRENT_LIST_DIR}/../..")
add_executable(application_audio_lifecycle_probe
 "${ROOT}/source/recovered/application_audio_lifecycle_probe.cpp"
 "${ROOT}/source/recovered/Porsche.exe/application_audio_lifecycle.cpp"
 "${ROOT}/source/recovered/Porsche.exe/application_services.cpp"
 "${ROOT}/source/recovered/Porsche.exe/application_state.cpp")
target_include_directories(application_audio_lifecycle_probe PRIVATE "${ROOT}/source/include")
target_compile_features(application_audio_lifecycle_probe PRIVATE cxx_std_17)
target_compile_options(application_audio_lifecycle_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(application_audio_lifecycle_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

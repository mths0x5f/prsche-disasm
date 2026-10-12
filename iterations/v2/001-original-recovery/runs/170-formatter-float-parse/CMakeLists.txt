cmake_minimum_required(VERSION 3.24)
project(formatter_float_parse_170 LANGUAGES CXX)
if(NOT WIN32 OR NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
 message(FATAL_ERROR "Run170 requires MSVC Win32")
endif()
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
add_executable(formatter_float_parse_probe
 "${ROOT}/source/recovered/formatter_float_parse_probe.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_float_parse.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_float_output.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_float_helpers.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_runtime.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_strings.cpp"
 "${ROOT}/source/recovered/Porsche.exe/formatter_crt_runtime.cpp"
 "${ROOT}/source/recovered/Porsche.exe/context_move.cpp")
target_include_directories(formatter_float_parse_probe PRIVATE "${ROOT}/source/include")
target_compile_features(formatter_float_parse_probe PRIVATE cxx_std_17)
target_compile_options(formatter_float_parse_probe PRIVATE /W4 /permissive- /EHsc /Gy)
target_compile_definitions(formatter_float_parse_probe PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
option(PORSCHE_FLOAT_PARSE_STAGE_TRACE "Observe private integer conversion stages" ON)
if(PORSCHE_FLOAT_PARSE_STAGE_TRACE)
 target_compile_definitions(formatter_float_parse_probe PRIVATE PORSCHE_FLOAT_PARSE_TRACE)
endif()
target_link_options(formatter_float_parse_probe PRIVATE /OPT:REF /BASE:0x10000000 /DYNAMICBASE:NO)
set_target_properties(formatter_float_parse_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

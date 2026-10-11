add_executable(formatter_crt_native_probe formatter-crt-native.cpp
    "${PORSCHE_SOURCE_ROOT}/platform/formatter_crt_links.cpp")
target_include_directories(formatter_crt_native_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(formatter_crt_native_probe PRIVATE cxx_std_17)
target_compile_options(formatter_crt_native_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(formatter_crt_native_probe PRIVATE NOMINMAX)
set_target_properties(formatter_crt_native_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

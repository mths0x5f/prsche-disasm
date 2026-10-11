add_executable(formatter_error_native_probe formatter-error-native.cpp
    "${PORSCHE_SOURCE_ROOT}/platform/formatter_error_links.cpp")
target_include_directories(formatter_error_native_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(formatter_error_native_probe PRIVATE cxx_std_17)
target_compile_options(formatter_error_native_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(formatter_error_native_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

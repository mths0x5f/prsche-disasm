add_executable(formatter_locale_heap_native_probe formatter-locale-heap-native.cpp
    "${PORSCHE_SOURCE_ROOT}/platform/formatter_locale_heap_links.cpp"
    "${PORSCHE_SOURCE_ROOT}/platform/formatter_crt_links.cpp")
target_include_directories(formatter_locale_heap_native_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(formatter_locale_heap_native_probe PRIVATE cxx_std_17)
target_compile_options(formatter_locale_heap_native_probe PRIVATE /W4 /EHsc /permissive-)
target_compile_definitions(formatter_locale_heap_native_probe PRIVATE NOMINMAX)
set_target_properties(formatter_locale_heap_native_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

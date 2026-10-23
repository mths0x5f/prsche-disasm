cmake_minimum_required(VERSION 3.20)
project(porsche_input_startup_370 LANGUAGES CXX)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../366-frame-init" entry-366)
target_sources(porsche_game_entry_bridges PRIVATE
    ../367-input-platform-bindings/startup_input_platform.cpp
    ../368-mouse-callbacks/mouse_callbacks.cpp
    ../369-original-sort/original_sort.cpp)

# Recreate the original named import missing from current Windows SDK libraries.
# CMake tracks the .def input; this adds no separate recovery build project.
set(dinput_def "${CMAKE_CURRENT_SOURCE_DIR}/../367-input-platform-bindings/dinput.def")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${dinput_def}")
set(dinput_lib "${CMAKE_CURRENT_BINARY_DIR}/original-dinput.lib")
execute_process(COMMAND "${CMAKE_AR}" /nologo /machine:x86
    "/def:${dinput_def}" "/out:${dinput_lib}"
    RESULT_VARIABLE dinput_result)
if(NOT dinput_result EQUAL 0)
    message(FATAL_ERROR "Could not generate original DINPUT named-import library")
endif()
target_link_libraries(porsche_game_entry_bridges PUBLIC "${dinput_lib}")

cmake_minimum_required(VERSION 3.20)

project(porsche_v2_recovery_probe LANGUAGES CXX)
if(NOT MSVC)
    message(FATAL_ERROR "The measured v2 recovery toolchain is MSVC")
endif()

if(NOT WIN32)
    message(FATAL_ERROR "v2 native probe build requires Windows/MSVC; no cross-platform game target is defined")
endif()

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "v2 recovery probe must be configured as 32-bit Win32/x86 (pointer size is ${CMAKE_SIZEOF_VOID_P})")
endif()

set(PORSCHE_SOURCE_ROOT "${CMAKE_CURRENT_LIST_DIR}/source")
set(PORSCHE_RECOVERY_PROBE "${PORSCHE_SOURCE_ROOT}/recovered/recovery_probe.cpp")
set(PORSCHE_RECOVERY_INCLUDE "${PORSCHE_SOURCE_ROOT}/include")
set(PORSCHE_RECOVERY_SOURCES_FILE "${PORSCHE_SOURCE_ROOT}/recovered/sources.cmake")

if(NOT EXISTS "${PORSCHE_RECOVERY_PROBE}")
    message(FATAL_ERROR "No recovered source exists: expected ${PORSCHE_RECOVERY_PROBE}")
endif()

set(PORSCHE_RECOVERED_SOURCES "")

# This optional file is the only supported way to add explicitly recovered
# source objects. It may append to PORSCHE_RECOVERED_SOURCES; it must not copy
# original game binaries or introduce guessed game logic.
if(EXISTS "${PORSCHE_RECOVERY_SOURCES_FILE}")
    include("${PORSCHE_RECOVERY_SOURCES_FILE}")
endif()

add_library(porsche_original STATIC ${PORSCHE_RECOVERED_SOURCES})
target_link_libraries(porsche_original PUBLIC winmm)
add_executable(recovery_probe "${PORSCHE_RECOVERY_PROBE}")
add_executable(fe_stream_probe "${PORSCHE_SOURCE_ROOT}/recovered/fe_stream_probe.cpp")
add_executable(heap_probe "${PORSCHE_SOURCE_ROOT}/recovered/heap_probe.cpp")
add_executable(files_probe "${PORSCHE_SOURCE_ROOT}/recovered/files_probe.cpp")
add_executable(device_probe "${PORSCHE_SOURCE_ROOT}/recovered/device_probe.cpp")
add_executable(worker_probe "${PORSCHE_SOURCE_ROOT}/recovered/worker_probe.cpp")
add_executable(wait_probe "${PORSCHE_SOURCE_ROOT}/recovered/wait_probe.cpp")
add_executable(event_probe "${PORSCHE_SOURCE_ROOT}/recovered/event_probe.cpp")
add_executable(thread_probe "${PORSCHE_SOURCE_ROOT}/recovered/thread_probe.cpp")
add_executable(joint_disk_probe "${PORSCHE_SOURCE_ROOT}/recovered/joint_disk_probe.cpp")
target_link_libraries(joint_disk_probe PRIVATE porsche_original)
add_executable(disk_probe "${PORSCHE_SOURCE_ROOT}/recovered/disk_probe.cpp")
target_link_libraries(disk_probe PRIVATE porsche_original)
add_executable(fe_callbacks_probe "${PORSCHE_SOURCE_ROOT}/recovered/fe_callbacks_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/fe_callbacks.cpp")
target_include_directories(fe_callbacks_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(fe_callbacks_probe PRIVATE cxx_std_17)
add_executable(input_probe "${PORSCHE_SOURCE_ROOT}/recovered/input_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/input_state.cpp")
add_executable(lock_probe "${PORSCHE_SOURCE_ROOT}/recovered/lock_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/heap_locks.cpp")
add_executable(disk_open_probe "${PORSCHE_SOURCE_ROOT}/recovered/disk_open_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/disk_open.cpp")
add_executable(input_buffer_probe "${PORSCHE_SOURCE_ROOT}/recovered/input_buffer_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/input_buffer.cpp")
add_executable(bootstrap_probe "${PORSCHE_SOURCE_ROOT}/recovered/bootstrap_probe.cpp")
target_link_libraries(bootstrap_probe PRIVATE porsche_original)
add_executable(startup_services_probe "${PORSCHE_SOURCE_ROOT}/recovered/startup_services_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/startup_services.cpp")
add_executable(resource_paths_probe "${PORSCHE_SOURCE_ROOT}/recovered/resource_paths_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/resource_paths.cpp")
add_executable(render_startup_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_startup_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_startup.cpp")
add_executable(application_heap_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_heap_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_heap.cpp")
add_executable(render_objects_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_objects_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_objects.cpp")
add_executable(window_runtime_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_runtime_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_runtime.cpp")
add_executable(render_loader_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_loader_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_loader.cpp"
)
add_executable(window_create_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_create_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_callback_bindings.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_create.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_init.cpp"
)
add_executable(application_alloc_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_alloc_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_alloc.cpp"
)
add_executable(application_heap_init_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_heap_init_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_heap_init.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_heap.cpp"
)
add_executable(window_procedure_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_procedure_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_procedure.cpp"
)
foreach(probe input_probe lock_probe disk_open_probe input_buffer_probe startup_services_probe resource_paths_probe render_startup_probe render_objects_probe window_runtime_probe application_heap_probe render_loader_probe window_create_probe application_alloc_probe application_heap_init_probe window_procedure_probe)
    target_include_directories(${probe} PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
    target_compile_features(${probe} PRIVATE cxx_std_17)
endforeach()
foreach(probe disk_probe fe_callbacks_probe input_probe lock_probe joint_disk_probe disk_open_probe input_buffer_probe bootstrap_probe startup_services_probe resource_paths_probe render_startup_probe render_objects_probe window_runtime_probe application_heap_probe render_loader_probe window_create_probe application_alloc_probe application_heap_init_probe window_procedure_probe)
    target_compile_definitions(${probe} PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
    target_compile_options(${probe} PRIVATE /W4 /EHsc /permissive-)
    target_link_options(${probe} PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/${probe}.map")
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()

target_link_libraries(thread_probe PRIVATE porsche_original)
target_compile_definitions(thread_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(thread_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(thread_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/thread_probe.map")
set_target_properties(thread_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(event_probe PRIVATE porsche_original)
target_compile_definitions(event_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(event_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(event_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/event_probe.map")
set_target_properties(event_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(wait_probe PRIVATE porsche_original)
target_compile_definitions(wait_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(wait_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(wait_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/wait_probe.map")
set_target_properties(wait_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(worker_probe PRIVATE porsche_original)
target_compile_definitions(worker_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(worker_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(worker_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/worker_probe.map")
set_target_properties(worker_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(device_probe PRIVATE porsche_original)
target_compile_definitions(device_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(device_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(device_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/device_probe.map")
set_target_properties(device_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(files_probe PRIVATE porsche_original)
target_compile_definitions(files_probe PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
target_compile_options(files_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(files_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/files_probe.map")
set_target_properties(files_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(heap_probe PRIVATE porsche_original)
target_compile_definitions(heap_probe PRIVATE _CRT_SECURE_NO_WARNINGS)
target_compile_options(heap_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(heap_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/heap_probe.map")
set_target_properties(heap_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
target_link_libraries(fe_stream_probe PRIVATE porsche_original)
target_compile_options(fe_stream_probe PRIVATE /W4 /EHsc /permissive-)
target_link_options(fe_stream_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/fe_stream_probe.map")
set_target_properties(fe_stream_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(PORSCHE_RECOVERY_TARGET recovery_probe)

target_include_directories(porsche_original PUBLIC "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(porsche_original PUBLIC cxx_std_17)
target_link_libraries(recovery_probe PRIVATE porsche_original)
target_include_directories(recovery_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(recovery_probe PRIVATE cxx_std_17)
target_compile_definitions(recovery_probe PRIVATE PORSCHE_V2_RECOVERY_PROBE=1)

if(MSVC)
    target_compile_definitions(porsche_original PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_options(porsche_original PRIVATE /W4 /EHsc /permissive-)
    target_compile_options(recovery_probe PRIVATE /W4 /EHsc /permissive-)
    target_link_options(recovery_probe PRIVATE /machine:X86 "/MAP:${CMAKE_BINARY_DIR}/recovery_probe.map")
endif()

set(PORSCHE_TOOLCHAIN_COMPILER "${CMAKE_CXX_COMPILER}")
string(REPLACE "\\" "/" PORSCHE_TOOLCHAIN_COMPILER "${PORSCHE_TOOLCHAIN_COMPILER}")
set(PORSCHE_TOOLCHAIN_PLATFORM "${CMAKE_GENERATOR_PLATFORM}")
file(WRITE "${CMAKE_BINARY_DIR}/build-toolchain.json"
    "{\n"
    "  \"compiler\": \"${PORSCHE_TOOLCHAIN_COMPILER}\",\n"
    "  \"compiler_id\": \"${CMAKE_CXX_COMPILER_ID}\",\n"
    "  \"compiler_version\": \"${CMAKE_CXX_COMPILER_VERSION}\",\n"
    "  \"pointer_size\": ${CMAKE_SIZEOF_VOID_P},\n"
    "  \"generator_platform\": \"${PORSCHE_TOOLCHAIN_PLATFORM}\"\n"
    "}\n")

set_target_properties(recovery_probe PROPERTIES
    CXX_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# Explicit native Win32 fixture; not an original game executable.
add_subdirectory(runs/036-native-window native-window)

# Integrated startup packages; platform/game callees stay explicit boundaries.
add_executable(render_display_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_display_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_display.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_objects.cpp"
)
add_executable(window_worker_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_worker_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_runtime.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_worker.cpp"
)
add_executable(application_pool_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_pool_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_pool.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/file_pages.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/file_device.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/io_worker_lists.cpp"
)
add_executable(window_handlers_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_handlers_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_handlers.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_procedure.cpp"
)
add_executable(window_state_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_state_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_create.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_worker.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_state.cpp"
)
add_executable(application_bootstrap_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_bootstrap_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_heap.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_heap_init.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_alloc.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/heap.cpp"
)
add_executable(startup_subsystems_probe "${PORSCHE_SOURCE_ROOT}/recovered/startup_subsystems_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/startup_subsystems.cpp"
)
add_executable(window_thread_start_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_threads_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_threads.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/file_threads.cpp"
)
foreach(probe render_display_probe window_worker_probe application_pool_probe window_handlers_probe window_state_probe application_bootstrap_probe startup_subsystems_probe window_thread_start_probe)
    target_include_directories(${probe} PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
    target_compile_features(${probe} PRIVATE cxx_std_17)
    target_compile_definitions(${probe} PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${probe} PRIVATE /W4 /EHsc /permissive-)
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()

add_executable(render_registry_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_registry_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_registry.cpp")
target_include_directories(render_registry_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(render_registry_probe PRIVATE cxx_std_17)
target_compile_definitions(render_registry_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(render_registry_probe PRIVATE /W4 /EHsc /permissive-)
target_link_libraries(render_registry_probe PRIVATE advapi32)
set_target_properties(render_registry_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# Next startup integration: original consumers, isolated recording boundaries.
add_executable(window_messages_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_messages_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_messages.cpp"
)
add_executable(startup_input_probe "${PORSCHE_SOURCE_ROOT}/recovered/startup_input_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/startup_input.cpp"
)
add_executable(application_fe_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_fe_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_fe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/fe_stream.cpp"
)
add_executable(window_position_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_position_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_position.cpp"
)
add_executable(render_activate_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_activate_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_activate.cpp"
)
add_executable(application_instance_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_instance_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_instance.cpp"
)
add_executable(render_window_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_window_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_window.cpp"
)
add_executable(exit_registry_probe "${PORSCHE_SOURCE_ROOT}/recovered/exit_registry_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/exit_registry.cpp"
)
add_executable(crt_shutdown_probe "${PORSCHE_SOURCE_ROOT}/recovered/exit_shutdown_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/exit_shutdown.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/exit_registry.cpp"
)
add_executable(thread_shutdown_probe "${PORSCHE_SOURCE_ROOT}/recovered/thread_shutdown_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/thread_shutdown.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/file_threads.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/file_pages.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/heap_locks.cpp"
)
add_executable(render_driver_calls_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_driver_calls_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_driver_calls.cpp"
)
add_executable(render_event_route_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_event_route_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_driver_calls.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_event_route.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/mouse_input.cpp"
)
add_executable(window_keys_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_keys_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_keys.cpp")
foreach(probe window_keys_probe window_messages_probe startup_input_probe application_fe_probe window_position_probe render_activate_probe application_instance_probe render_window_probe exit_registry_probe crt_shutdown_probe thread_shutdown_probe render_driver_calls_probe render_event_route_probe)
    target_include_directories(${probe} PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
    target_compile_features(${probe} PRIVATE cxx_std_17)
    target_compile_definitions(${probe} PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${probe} PRIVATE /W4 /EHsc /permissive-)
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()
add_subdirectory(runs/057-native-thread-chain native-thread)

add_executable(render_mode_probe "${PORSCHE_SOURCE_ROOT}/recovered/render_mode_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/render_mode.cpp")
add_executable(window_callback_bindings_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_callback_bindings_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_callback_bindings.cpp")
foreach(probe render_mode_probe window_callback_bindings_probe)
    target_include_directories(${probe} PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
    target_compile_features(${probe} PRIVATE cxx_std_17)
    target_compile_definitions(${probe} PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${probe} PRIVATE /W4 /EHsc /permissive-)
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()

add_executable(application_main_probe "${PORSCHE_SOURCE_ROOT}/recovered/application_main_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_main.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_context.cpp")
target_include_directories(application_main_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(application_main_probe PRIVATE cxx_std_17)
target_compile_definitions(application_main_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(application_main_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(application_main_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_executable(window_callback_integration_probe "${PORSCHE_SOURCE_ROOT}/recovered/window_callbacks_integration_probe.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_callback_bindings.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_handlers.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_procedure.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_messages.cpp"
    "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/window_keys.cpp"
)
target_include_directories(window_callback_integration_probe PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(window_callback_integration_probe PRIVATE cxx_std_17)
target_compile_definitions(window_callback_integration_probe PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
target_compile_options(window_callback_integration_probe PRIVATE /W4 /EHsc /permissive-)
set_target_properties(window_callback_integration_probe PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# Shared original application storage, used by standalone comparison targets.
foreach(probe render_startup_probe render_display_probe application_fe_probe render_mode_probe application_main_probe)
    target_sources(${probe} PRIVATE
        "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_state.cpp"
        "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/application_globals.cpp")
endforeach()
add_subdirectory(runs/066-render-settings render-settings)
add_subdirectory(runs/068-application-state application-state)
add_subdirectory(runs/069-window-event-queue window-event-queue)
add_subdirectory(runs/070-native-window-bindings native-window-bindings)
add_subdirectory(runs/071-render-state-init render-state-init)
add_subdirectory(runs/072-window-links window-links)
add_subdirectory(runs/073-render-state-integration render-state-integration)
add_subdirectory(runs/074-application-arena application-arena)
add_subdirectory(runs/075-recovered-links recovered-links)
add_subdirectory(runs/077-native-window-chain native-window-chain)

add_library(porsche_window_links STATIC "${PORSCHE_SOURCE_ROOT}/platform/window_links.cpp")
target_include_directories(porsche_window_links PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
target_compile_features(porsche_window_links PRIVATE cxx_std_17)
target_compile_options(porsche_window_links PRIVATE /W4 /EHsc /permissive-)
add_subdirectory(runs/079-window-channels window-channels)
add_subdirectory(runs/080-shared-diagnostic-storage shared-diagnostic-storage)
add_subdirectory(runs/082-window-scheduler window-scheduler)
target_sources(native_window_smoke PRIVATE "${PORSCHE_SOURCE_ROOT}/recovered/Porsche.exe/shared_runtime_globals.cpp")

add_subdirectory(runs/083-window-shutdown window-shutdown)
add_subdirectory(runs/084-window-support window-support)
add_subdirectory(runs/085-window-exit-cleanup window-exit-cleanup)
add_subdirectory(runs/086-native-window-lifecycle native-window-lifecycle)
add_subdirectory(runs/087-window-notifications window-notifications)
add_subdirectory(runs/088-object-cleanup object-cleanup)
add_subdirectory(runs/089-mouse-input mouse-input)
add_subdirectory(runs/091-window-event-translation window-event-translation)
add_subdirectory(runs/092-object-update object-update)
add_subdirectory(runs/093-game-setup game-setup)
add_subdirectory(runs/094-movie-header movie-header)
add_subdirectory(runs/096-input-snapshot input-snapshot)
add_subdirectory(runs/097-startup-sequence startup-sequence)
add_subdirectory(runs/095-splash-progress splash-progress)
add_subdirectory(runs/099-startup-service startup-service-099)
add_subdirectory(runs/100-startup-service startup-service-100)
add_subdirectory(runs/101-frame-pump frame-pump-101)
add_subdirectory(runs/103-engine-service engine-service-103)
add_subdirectory(runs/105-frame-services frame-services-105)
add_subdirectory(runs/106-resource-predicate resource-predicate-106)
add_subdirectory(runs/108-formatter-entry formatter-entry-108)
add_subdirectory(runs/109-resource-leaf resource-leaf-109)
add_subdirectory(runs/112-clock-worker clock-worker-112)
add_subdirectory(runs/113-resource-dispatch resource-dispatch-113)
add_subdirectory(runs/115-process-exit process-exit-115)
add_subdirectory(runs/116-install-paths install-paths-116)
add_subdirectory(runs/117-install-integration install-integration-117)
add_subdirectory(runs/118-timer-setup timer-setup-118)
add_subdirectory(runs/119-formatter-original formatter-original-119)
add_subdirectory(runs/122-auxiliary-wait auxiliary-wait-122)
add_subdirectory(runs/121-formatter-timer-integration formatter-timer-integration-121)
add_subdirectory(runs/123-event-lifecycle event-lifecycle-123)
add_subdirectory(runs/127-thread-wait thread-wait-127)
add_subdirectory(runs/128-application-services application-services-128)
add_subdirectory(runs/130-event-thread-integration event-thread-integration-130)
add_subdirectory(runs/129-application-context application-context-129)
add_subdirectory(runs/124-formatter-parser formatter-parser-124)
add_subdirectory(runs/132-formatter-cleanup formatter-cleanup-132)
add_subdirectory(runs/133-application-audio-device application-audio-device-133)
add_subdirectory(runs/134-formatter-integration formatter-integration-134)
add_subdirectory(runs/137-formatter-runtime formatter-runtime-137)
add_subdirectory(runs/135-application-context-base application-context-base-135)
add_subdirectory(runs/138-formatter-runtime-storage formatter-runtime-storage-138)
add_subdirectory(runs/140-formatter-bootstrap formatter-bootstrap-140)
add_subdirectory(runs/141-application-services-next application-services-next-141)
add_subdirectory(runs/142-audio-lifecycle audio-lifecycle-142)
add_subdirectory(runs/139-context-effects context-effects-139)
add_subdirectory(runs/144-crt-strings crt-strings-144)
add_subdirectory(runs/145-network-lifecycle network-lifecycle-145)
add_subdirectory(runs/143-runtime-network-integration runtime-network-integration-143)
add_subdirectory(runs/147-float-helpers float-helpers-147)
add_subdirectory(runs/148-network-services network-services-148)
add_subdirectory(runs/149-context-ranges context-ranges-149)
add_subdirectory(runs/150-context-services context-services-150)
add_subdirectory(runs/151-network-cleanup network-cleanup-151)
add_subdirectory(runs/153-services-integration services-integration-153)
add_subdirectory(runs/152-crt-lowio crt-lowio-152)
add_subdirectory(runs/154-context-move context-move-154)
add_subdirectory(runs/155-network-session network-session-155)
add_subdirectory(runs/156-lowio-memory-integration lowio-memory-integration-156)
add_subdirectory(runs/157-crt-runtime crt-runtime-157)
add_subdirectory(runs/158-formatter-text formatter-text-158)
add_subdirectory(runs/159-network-workers-members network-workers-members-159)
add_subdirectory(runs/160-crt-text-workers-integration crt-text-workers-integration-160)
add_subdirectory(runs/161-small-heap small-heap-161)
add_subdirectory(runs/162-formatter-locale formatter-locale-162)
add_subdirectory(runs/163-network-groups network-groups-163)
add_subdirectory(runs/165-heap-locale-groups-integration heap-locale-groups-integration-165)

# The native platform target is defined by Run055's add_subdirectory above.
if(TARGET porsche_platform_win32)
    target_sources(porsche_platform_win32 PRIVATE
        "${PORSCHE_SOURCE_ROOT}/platform/win32_shutdown.cpp"
        "${PORSCHE_SOURCE_ROOT}/platform/application_service_links.cpp"
        "${PORSCHE_SOURCE_ROOT}/platform/formatter_error_links.cpp"
        "${PORSCHE_SOURCE_ROOT}/platform/formatter_lowio_links.cpp"
        "${PORSCHE_SOURCE_ROOT}/platform/formatter_crt_links.cpp"
        "${PORSCHE_SOURCE_ROOT}/platform/formatter_locale_heap_links.cpp")
endif()

foreach(probe engine_service_427a60_probe frame_services_probe resource_predicate_probe formatter_entry_probe resource_leaf_probe clock_worker_probe resource_dispatch_probe process_exit_probe install_paths_probe install_paths_integration_probe timer_setup_probe formatter_original_probe auxiliary_wait_probe startup_timing_integration_probe)
    target_include_directories(${probe} PRIVATE "${PORSCHE_RECOVERY_INCLUDE}")
    target_compile_features(${probe} PRIVATE cxx_std_17)
    target_compile_definitions(${probe} PRIVATE NOMINMAX _CRT_SECURE_NO_WARNINGS)
    target_compile_options(${probe} PRIVATE /W4 /EHsc /permissive-)
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()

foreach(probe formatter_parser_probe formatter_cleanup_probe application_audio_device_probe formatter_integration_probe formatter_runtime_probe application_context_base_probe formatter_runtime_storage_probe formatter_bootstrap_probe application_services_next_probe application_audio_lifecycle_probe context_effects_probe formatter_strings_probe formatter_strings_production_probe network_lifecycle_probe formatter_float_helpers_probe network_services_probe context_ranges_probe context_range_wrapper_probe context_services_probe network_cleanup_probe formatter_lowio_probe context_move_probe network_session_probe formatter_crt_runtime_probe formatter_crt_runtime_trace_probe formatter_small_heap_probe)
    set_target_properties(${probe} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endforeach()

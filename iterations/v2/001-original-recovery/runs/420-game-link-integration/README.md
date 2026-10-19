# Run 420: Integration of Heap Shutdown (418) and Frame Root Lifecycle (419) into Game Target

> **Correction:** the bridge no longer defines the `00628960` cell. It comes from Run 419's object, which defines `frame_service_root_00628960` — the same symbol Run 290's frozen header declares. The bridge previously defined a cell of its own: the link contract closed, but the consumer `00471b60` read storage nothing ever wrote. The rebuild (`build-002.json`) keeps 188 sources, 415 unresolved names / 446 references and zero errors, with the symbol resolved from Run 419.
>
> **Исправление:** бридж больше не определяет ячейку `00628960`. Она берётся из объекта Run 419, который определяет `frame_service_root_00628960` — тот же символ, что объявляет замороженный заголовок Run 290. Ранее бридж определял собственную ячейку: контракт линковки закрывался, но потребитель `00471b60` читал память, в которую никто не писал. Пересборка (`build-002.json`) сохраняет 188 исходников, 415 имён / 446 ссылок и ноль ошибок.

## Summary
- Integrated 188 C++ translation units in the real game graph (`porsche_original_game_link`), compiling 100% cleanly under MSVC Win32 (`/MP6`, 0 compiler errors, 0 other linker errors).
- Connected `heap_shutdown_418.cpp` (5 PE functions, 623 bytes) and `frame_root_lifecycle_419.cpp` (2 PE functions + contiguous storage layout).
- Closed 8 unresolved linker contracts from the Run 417 frontier:
  1. `?platform_flush_0059eb20@porsche@@YAXXZ`
  2. `?application_pool_shutdown_005678f0@porsche@@YAXXZ`
  3. `?startup_sequence_call_00471b70@porsche@@YAXXZ`
  4. `?frame_service_root_00628960@porsche@@3IA`
  5. `?app_loop_post_tick_pipeline_004b68f0@porsche@@YAXXZ`
  6. `?application_context_heap_selector_005e4fec@porsche@@YAIXZ`
  7. `?application_context_heap_state_005e4fe8@porsche@@YAPAXXZ`
  8. `?context_selector_pointer_005e4fec@porsche@@YAPAXXZ`
- Provided clean bridge `entry_bridges_420.cpp` resolving heap selector/state accessors and linking the C/C++ boundaries cleanly.
- Verified 433 source pins via `v2_shared_manifests.py`.
- Independent batch audit (`audit-v2-game-link-420.py`) PASSED 100%.

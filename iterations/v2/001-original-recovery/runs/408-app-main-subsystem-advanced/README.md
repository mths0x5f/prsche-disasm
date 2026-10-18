# Run 408 — app_main advanced subsystem recovery

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: 5 advanced functions (1,536 bytes) called across the `app_main_004b6a50` subsystem:
1. `00531f90` (278 bytes): `heap_pool_block_free_00531f90` — Heap Pool Block deallocator. Handles coalescing with forward and backward physical heap blocks, midpoint calculation for bidirectional free-list sentinel search, and thread lock release (`005322c0`).
2. `004a6840` (279 bytes): `display_device_transition_004a6840` — Display Device Mode Transition manager. Allocates scratch buffer via `heap_pool_alloc_00531ca0`, initializes 8 `DisplayDeviceEntry` slots, probes display mode via `004a66b0`, initializes mode via `004ae100`, calls subsystems `004a8b80`, `004ae2b0`, `004ab4b0`, `00565890`, and frees scratch buffer via `00531f90`.
3. `004b67b0` (311 bytes): `app_loop_pre_tick_pipeline_004b67b0` — Pre-simulation-tick engine pipeline. Executes `step_00536080` on `SimSubsystem`, followed by ordered pipeline stages (`0044dfb0`, `0056a490`, `00516950`, `00413cf0`, `00427a60`, etc.), phase notifications `004a4a70(1/2)`, clears `g_val_00606ac0/4`, polls input via `0048cdf0`, and tail-dispatches to `004691c0`.
4. `004b4b80` (331 bytes): `window_event_filter_dispatch_004b4b80` — Window and engine event message filter and dispatcher. Handles routing message IDs `>= 0x21e` (stride-based destination buffers), `>= 0x14e` (callback table dispatch via `005cc5d0`), and standard event routing entries (`0x142..0x147` array payload copies).
5. `004b68f0` (337 bytes): `app_loop_post_tick_pipeline_004b68f0` — Post-simulation-tick engine pipeline. Executes pre-log pipes `004690f0`, `00516950`, copies target object strings and sub-objects, transfers 150-dword payloads into `g_data_005e75a0`, and executes teardown pipes `00413fd0`, `004a8a80`, `004afe50`, heap trace logs `005a177b`, etc.

The implementation is verified with native differential execution on an isolated physical x86 execution slab against original PE bytes (11 cases, all passing).

## Russian / На русском

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: 5 функций (1 536 байт) сложной подсистемы `app_main_004b6a50`:
1. `00531f90` (278 байт): `heap_pool_block_free_00531f90` — освобождение блока пула кучи с объединением соседних физических блоков и двунаправленным поиском позиции в списке свободных блоков.
2. `004a6840` (279 байт): `display_device_transition_004a6840` — переключение режимов дисплея и инициализация массива устройств с управлением буфером и вызовами подсистем.
3. `004b67b0` (311 байт): `app_loop_pre_tick_pipeline_004b67b0` — пайплайн до тика симуляции (вызов шага подсистемы, цепочка фильтров и фазовых уведомлений, опрос ввода и хвостовой переход).
4. `004b4b80` (331 байт): `window_event_filter_dispatch_004b4b80` — фильтрация и маршрутизация оконных и игровых событий с таблицами маршрутов и обратных вызовов.
5. `004b68f0` (337 байт): `app_loop_post_tick_pipeline_004b68f0` — пайплайн после тика симуляции с копированием строк, полей объектов и снимков 150 двойных слов данных.

Реализация подтверждена нативным дифференциальным тестом на физическом слэбе x86 против оригинальных байтов PE (11 тестов, 100% совпадение).

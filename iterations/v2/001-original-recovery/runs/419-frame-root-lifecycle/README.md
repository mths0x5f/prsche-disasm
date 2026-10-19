# Run 419 — Frame Root Lifecycle Recovery (00471b70 & 00471c40)

[English](#english) | [Русский](#русский)

---

## English

### Overview
Run 419 resolves the long-standing `HOLD` on the frame root storage cell `00628960` and recovers its two sole owners in retail binary `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
- `00471b70..00471c36` (198 PE bytes): `frame_root_init_00471b70` (`BWorld_Init`) — copies track name string (`00657444` to `00628940`), allocates `0x3c` bytes through `0059ef90`, constructs the root frame service object through `004874a0` storing into `00628960`, formats path string into `00628964`, attempts track load via `004876e0` (with error logging via `0059fd90`), calculates context parameters from `00628bc0` calling `005323a0`, and logs completion to trace.
- `00471c40..00471c81` (65 PE bytes): `frame_root_teardown_00471c40` (`BWorld_DeInit`) — logs `"BWorld_DeInit..."`, destructs root through `00487590`, frees root memory through `0059f050`, clears `00628960` to `0`, and logs `"done.\n"`.

Total recovered PE body bytes: **263 bytes across 2 functions**.

### Resolution of Storage Cell `00628960`
- Contiguous memory layout across `00628940` (track name, 32 bytes), `00628960` (root pointer, 4 bytes), and `00628964` (formatted path, 256 bytes) is maintained in `FrameRootStorageLayout`.
- Closes the pending contract for `?startup_sequence_call_00471b70@porsche@@YAXXZ` in `porsche_original_game_link`.
- Closes the pipeline target `pipe_00471c40` called in `app_loop_post_tick_pipeline_004b68f0`.

### Verification
- Clean compilation under MSVC Win32 (`/W4 /Od /Zl`), **0 warnings, 0 errors**.
- Differential verification on physical x86 CPU memory slab (`native-fixture.exe`) with 5/5 passed cases.
- Independent acceptance audit (`scripts/research/audit-v2-frame-root-419.py`) **100% PASS**.

---

## Русский

### Обзор
Запуск 419 закрывает статус `HOLD` для ячейки памяти корня кадра `00628960` и восстанавливает двух её единственных владельцев в оригинальном `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
- `00471b70..00471c36` (198 байт PE): `frame_root_init_00471b70` (`BWorld_Init`) — копирует имя трека из `00657444` в `00628940`, выделяет `0x3c` байт через `0059ef90`, конструирует объект через `004874a0` и сохраняет в `00628960`, форматирует путь в `00628964`, загружает трек через `004876e0` (с выводом ошибки через `0059fd90`), вычисляет смещения из `00628bc0` для вызова `005323a0` и логирует завершение.
- `00471c40..00471c81` (65 байт PE): `frame_root_teardown_00471c40` (`BWorld_DeInit`) — логирует `"BWorld_DeInit..."`, деструктирует корень через `00487590`, освобождает память через `0059f050`, обнуляет `00628960` и логирует `"done.\n"`.

Суммарный объём: **263 байта тела PE в 2 функциях**.
Все 5 дифференциальных проверок на CPU x86 пройдены успешно (100% PASS).

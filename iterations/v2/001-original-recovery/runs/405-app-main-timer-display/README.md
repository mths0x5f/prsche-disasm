# Run 405 — app_main timer, display resolution, SIMD/MMX vector, and stream packet cluster

## English

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
This run recovers four authentic functions (420 PE body bytes) directly invoked by `app_main_004b6a50` or its immediate startup/display/timer sequence:

1. `0053c290` (77 bytes): CPU SIMD/MMX feature branch vector operation dispatcher. Tests 3DNow flag (`005deb1c`), then MMX flag (`005deb18`), calling the specialized transform routines `005b0b00` or `005b0a40`, or falling back to generic `005b0980`.
2. `004b6660` (99 bytes): Packet stream serialization and buffer flush dispatcher. Allocates a temporary stream buffer (`00531ca0`), initializes a stack-based context cursor (`004b5ee0`), serializes the packet payload (`004b60d0`), appends a 4-byte 0 delimiter, flushes the stream (`00569640`), and returns the buffer.
3. `00467fc0` (112 bytes): Display resolution and video mode switcher (`DisplayManager_00467fc0`). Checks active dimensions (`00619784`, `00619788`, `0061978c`), short-circuits on identical resolution, or sets mode via `00468030` (mode 0 for fullscreen or `find_display_mode_005376c0` result for windowed).
4. `005366e0` (132 bytes): Periodic game timer subsystem dispatcher. Compares `g_timer_last_tick_0069de24` with `g_current_time_006b7c40`, loops through the 16-entry timer table `g_timer_table_0069dd20` (16 bytes per entry: callback, period, next_fire_time, is_running), dispatches pending callbacks with elapsed time, advances `next_fire_time`, and returns bitwise OR of callback return values.

### Physical x86 Verification
- Captured machine code bytes are tested in `local/experiments/v2-app-main-405/native-fixture.exe` against the original byte sequence in an executable memory slab.
- All 10 differential test cases pass bit-exact matching.
- Validated with `scripts/research/audit-v2-app-main-405.py`.

---

## Русский

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Этот запуск восстанавливает четыре аутентичные функции (420 байт тела PE), вызываемые напрямую из `app_main_004b6a50` или его непосредственной подсистемы таймеров, экрана и сериализации потока:

1. `0053c290` (77 байт): Диспетчер векторных операций SIMD/MMX с проверкой флагов процессора. Проверяет флаг 3DNow (`005deb1c`), затем флаг MMX (`005deb18`), вызывая оптимизированные процедуры `005b0b00` / `005b0a40`, либо базовую `005b0980`.
2. `004b6660` (99 байт): Диспетчер сериализации пакета и сброса потока. Выделяет буфер (`00531ca0`), инициализирует стек-курсор контекста (`004b5ee0`), записывает пакет (`004b60d0`), записывает терминатор 0 (4 байта), вызывает сброс буфера (`00569640`) и возвращает указатель.
3. `00467fc0` (112 байт): Переключатель разрешения экрана и видеорежима (`DisplayManager_00467fc0`). Сверяет текущие параметры (`00619784`, `00619788`, `0061978c`), завершается при совпадении, либо переключает режим через `00468030` (режим 0 для полноэкранного или через поиск `find_display_mode_005376c0` для оконного).
4. `005366e0` (132 байт): Диспетчер подсистемы периодических игровых таймеров. Сверяет `g_timer_last_tick_0069de24` с `g_current_time_006b7c40`, обходит таблицу из 16 таймеров `g_timer_table_0069dd20` (по 16 байт на элемент: callback, period, next_fire_time, is_running), вызывает сработавшие коллбэки с передачей прошедшего времени, сдвигает `next_fire_time` на период и возвращает побитовое ИЛИ результатов коллбэков.

### Проверка на реальном процессоре x86
- Байт-в-байт сверка оригинальных инструкций в исполняемом слэбе памяти `local/experiments/v2-app-main-405/native-fixture.exe`.
- Все 10 дифференциальных тестов пройдены успешно без расхождений.
- Проверено независимым скриптом аудита `scripts/research/audit-v2-app-main-405.py`.

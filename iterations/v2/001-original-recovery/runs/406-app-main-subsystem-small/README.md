# Run 406 — app_main input device update, audio heap logging, subsystem startup, and sound context cluster

## English

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
This run recovers four authentic functions (635 PE body bytes) invoked directly by `app_main_004b6a50` or its immediate subsystem sequence:

1. `0048e6f0` (153 bytes): Input device update and event router mode switcher (`InputDevice_0048e6f0::update_mode_0048e6f0`). Checks mode `mode_28`: if 0, updates device (`sub_0048e9c0`) and posts event 0 (`post_input_event_0048e1a0`); if 2, updates device and posts event 2; otherwise if `flag_c6` is set, frees sub-object `sub_object_14` (`004935c0`, `0059f050`) and dispatches input command `0xba` with bounds `0x80000000` via `handle_0c->dispatch_input_cmd_0048c870`; else calls `sub_0048e9c0`.
2. `004a6960` (153 bytes): Presentation sync and audio heap usage logger (`application_main_function_004a6960`). Calls `time_delay_005659f0(-1)`, flushes/destroys stream buffer `00656518`, synchronizes render context (`004ae310`), and if render flags `005d1734`/`005d1738` are active, cycles rendering (`004ab4b0`), retrieves audio heap usage delta (`00565890`), destroys stream `00655d44`, and logs formatted byte count via reciprocal division and `log_printf("audio heap used %d bytes\n", edx)`.
3. `004a5410` (157 bytes): Subsystem startup memory, timer, and input manager initialization dispatcher (`application_main_function_004a5410`). Configures heap hook table `005debf0`, initializes main heap with 24MB and 4MB limits (`0059e9d0`), reserves smallblock heap (`0059edb0`), allocates system buffer (`00565030`), conditionally instantiates `InputManager` if `g_subsystem_mgr_00628c70` is null, runs startup service sequence `0055fcf0`, `00564e70`, `00564ab0`, `00564850(2)`, initializes timers `00536e50`/`005367b0(0, 1000, 1)`, and sets up window channel `00563ad0(30, 8192, 0)`.
4. `004d1a90` (172 bytes): SoundContext object constructor and default sound driver setup (`SoundContext_004d1a90::init_004d1a90`). Invokes base initializer `00525e20`, zeroes 12 internal fields (`0xd4`, `0xe0`, `0xe4`, `0xe8`, `0xf8`, `0xfc`, `0x100`, `0x104`, `0x108`, `0x170`, `0x174`, `0x17c`), assigns vtable `005b683c`, allocates and constructs sub-device `005294c0` (44 bytes), copies default driver string `"Primary DirectSound Driver"` (`005e8e50`) to `device_name_10c`, and returns `this`.

### Physical x86 Verification
- Captured machine code bytes are tested in `local/experiments/v2-app-main-406/native-fixture.exe` against the original byte sequence in an executable memory slab.
- All 10 differential test cases pass bit-exact matching.
- Validated with `scripts/research/audit-v2-app-main-406.py`.

---

## Русский

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Этот запуск восстанавливает четыре аутентичные функции (635 байт тела PE), вызываемые напрямую из `app_main_004b6a50` или его подсистем ввода, логирования памяти, запуска и звука:

1. `0048e6f0` (153 байт): Обновление устройства ввода и переключение режима маршрутизатора событий (`InputDevice_0048e6f0::update_mode_0048e6f0`). Проверяет режим `mode_28`: если 0 — обновляет устройство (`sub_0048e9c0`) и отправляет событие 0 (`post_input_event_0048e1a0`); если 2 — обновляет устройство и отправляет событие 2; иначе при установленном `flag_c6` освобождает подузел `sub_object_14` (`004935c0`, `0059f050`) и отправляет команду ввода `0xba` с границами `0x80000000` через `handle_0c->dispatch_input_cmd_0048c870`; иначе вызывает `sub_0048e9c0`.
2. `004a6960` (153 байт): Синхронизация отображения и протоколирование использования звуковой кучи (`application_main_function_004a6960`). Вызывает задержку `time_delay_005659f0(-1)`, уничтожает поток `00656518`, синхронизирует рендер-контекст (`004ae310`), а при активных флагах рендера запускает цикл рендера (`004ab4b0`), получает дельту использования звуковой кучи (`00565890`), уничтожает поток `00655d44` и выводит отформатированный размер кучи через обратное умножение и `log_printf("audio heap used %d bytes\n", edx)`.
3. `004a5410` (157 байт): Диспетчер инициализации памяти, таймеров и менеджера ввода (`application_main_function_004a5410`). Настраивает хук кучи `005debf0`, инициализирует кучу с лимитами 24МБ и 4МБ (`0059e9d0`), резервирует мелкоблочную кучу (`0059edb0`), выделяет системный буфер (`00565030`), при отсутствии `g_subsystem_mgr_00628c70` инстанциирует `InputManager`, запускает цепочку служб `0055fcf0`, `00564e70`, `00564ab0`, `00564850(2)`, настраивает периодические таймеры `00536e50`/`005367b0(0, 1000, 1)` и оконный канал `00563ad0(30, 8192, 0)`.
4. `004d1a90` (172 байт): Конструктор объекта звукового контекста SoundContext и настройка драйвера (`SoundContext_004d1a90::init_004d1a90`). Вызывает базовый инициализатор `00525e20`, обнуляет 12 полей (`0xd4`, `0xe0`, `0xe4`, `0xe8`, `0xf8`, `0xfc`, `0x100`, `0x104`, `0x108`, `0x170`, `0x174`, `0x17c`), устанавливает vtable `005b683c`, выделяет и конструирует подустройство `005294c0` (44 байта), копирует имя устройства по умолчанию `"Primary DirectSound Driver"` (`005e8e50`) в `device_name_10c` и возвращает `this`.

### Проверка на реальном процессоре x86
- Байт-в-байт сверка оригинальных инструкций в исполняемом слэбе памяти `local/experiments/v2-app-main-406/native-fixture.exe`.
- Все 10 дифференциальных тестов пройдены успешно без расхождений.
- Проверено независимым скриптом аудита `scripts/research/audit-v2-app-main-406.py`.

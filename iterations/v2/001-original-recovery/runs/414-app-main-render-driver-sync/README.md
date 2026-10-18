# Run 414 — App Main Render Driver Sync Recovery (`render_driver_sync_004d3420`)

[English](#english) | [Русский](#русский)

---

## English

### Overview
Run 414 recovers `render_driver_sync_004d3420` (8,592 bytes: `0x004d3420..0x004d55b0`) in retail binary `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`).
This function represents the **70th and final direct CALL target** originating from top-level entry point `app_main_004b6a50`.
With this run completed, **100% of all direct call targets of `app_main_004b6a50` (70 functions, 26,209 PE body bytes) are recovered and verified bit-exact**.

### Function Details
- **Function Name:** `render_driver_sync_004d3420`
- **Virtual Address:** `0x004d3420..0x004d55b0`
- **Body Size:** 8,592 bytes
- **Calling Convention:** `__thiscall`
- **Parameters:**
  - `this`: pointer to render driver synchronization state structure (512 bytes)
  - `setup_name`: pointer to configuration string (`const char*`, e.g. `"gamesetup"`)
  - `save_buf`: optional pointer to replay/config storage buffer (`0x4000` bytes)
  - `param_4`: flag / mode parameter (`std::int32_t`)
- **Key Responsibilities:**
  1. Resolves and initializes DirectDraw / 3D render display submodes and resolutions (`0x280 x 0x1e0`, 16-bit).
  2. Parses and dispatches UI / layout setup scripts (`gamesetup`, `bottombar.lay`, `serverlist`, `victoryroom`, etc.).
  3. Manages network / multiplayer server communication synchronization modes (P2P IP, modem, IPX, LAN).
  4. Coordinates Front-End accessor hierarchy RTTI queries (`FEAccessor`, `FEPositionableAccessor`, `FECharVectAccessor`).
  5. Synchronizes 3D engine scene parameters, sound drivers, video replay streams, and driver framebuffers.

### Differential Verification
Native differential execution is performed by `local/experiments/v2-app-main-414/native-fixture.exe` against the original physical x86 CPU memory slab:
1. **10/10 Test Cases Passed (100% bit-exact):**
   - TC 1: `01_quick_setup_p4_1` (`orig_ret = 0, cpp_ret = 0`)
   - TC 2: `02_cold_startup_p4_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 3: `03_warm_path_sync_flag_1` (`orig_ret = 1, cpp_ret = 1`)
   - TC 4: `04_warm_path_sync_flag_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 5: `05_resolution_320x240_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 6: `06_resolution_640x480_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 7: `07_resolution_800x600_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 8: `08_resolution_1024x768_32bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 9: `09_save_config_buf` (`orig_ret = 1, cpp_ret = 1`)
   - TC 10: `10_full_driver_negotiation` (`orig_ret = 1, cpp_ret = 1`)
2. **Trace & State Equivalence:**
   - Call trace: 100% identical sequence of external and hooked calls.
   - Return values: 100% identical across all 10 test cases.
   - Global synchronization flag (`g_dat_00619800`): bit-exact match.
   - Instance state memory (`s_this`, 512 bytes): bit-exact match.
   - Replay / config storage buffer (`0x4000` bytes): bit-exact match.

---

## Русский

### Обзор
Запуск 414 восстанавливает функцию `render_driver_sync_004d3420` (8 592 байта: `0x004d3420..0x004d55b0`) в оригинальном релизном исполняемом файле `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`).
Эта функция является **70-й и последней прямой вызываемой функцией (CALL target)** точки входа `app_main_004b6a50`.
С завершением этого запуска **100% всех прямых вызываемых функций `app_main_004b6a50` (70 функций, 26 209 байт машинного кода PE) полностью восстановлены и верифицированы бит-в-бит**.

### Детали функции
- **Имя функции:** `render_driver_sync_004d3420`
- **Диапазон адресов:** `0x004d3420..0x004d55b0`
- **Размер тела:** 8 592 байта
- **Конвенция вызова:** `__thiscall`
- **Параметры:**
  - `this`: указатель на структуру состояния синхронизации драйвера рендера (512 байт)
  - `setup_name`: указатель на строку конфигурации (`const char*`, например `"gamesetup"`)
  - `save_buf`: опциональный указатель на буфер сохранения конфигурации/повторов (`0x4000` байт)
  - `param_4`: флаг / параметр режима (`std::int32_t`)
- **Основные задачи:**
  1. Определение и инициализация видеорежимов DirectDraw / 3D рендера (`0x280 x 0x1e0`, 16 бит).
  2. Разбор и диспетчеризация сценариев интерфейса и верстки (`gamesetup`, `bottombar.lay`, `serverlist`, `victoryroom` и др.).
  3. Управление режимами сетевой синхронизации (P2P IP, модем, IPX, локальная сеть).
  4. Координация RTTI-запросов иерархии акцессоров интерфейса (`FEAccessor`, `FEPositionableAccessor`, `FECharVectAccessor`).
  5. Синхронизация параметров сцены 3D-движка, звуковых драйверов, видеопотоков повторов и кадровых буферов драйвера.

### Дифференциальная верификация
Нативное дифференциальное тестирование выполнено исполняемым файлом `local/experiments/v2-app-main-414/native-fixture.exe` на физическом x86 CPU memory slab:
1. **10/10 тестов пройдены успешно (100% совпадение):**
   - TC 1: `01_quick_setup_p4_1` (`orig_ret = 0, cpp_ret = 0`)
   - TC 2: `02_cold_startup_p4_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 3: `03_warm_path_sync_flag_1` (`orig_ret = 1, cpp_ret = 1`)
   - TC 4: `04_warm_path_sync_flag_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 5: `05_resolution_320x240_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 6: `06_resolution_640x480_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 7: `07_resolution_800x600_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 8: `08_resolution_1024x768_32bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 9: `09_save_config_buf` (`orig_ret = 1, cpp_ret = 1`)
   - TC 10: `10_full_driver_negotiation` (`orig_ret = 1, cpp_ret = 1`)
2. **Эквивалентность трассы и состояния:**
   - Трасса вызовов: 100% по порядку, тегам функций и аргументам.
   - Возвращаемые значения: 100% во всех 10 тестовых сценариях.
   - Глобальный флаг синхронизации (`g_dat_00619800`): бит-в-бит совпадение.
   - Память состояния объекта (`s_this`, 512 байт): бит-в-бит совпадение.
   - Буфер сохранения конфигурации (`0x4000` байт): бит-в-бит совпадение.

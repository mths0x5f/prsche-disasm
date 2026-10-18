# Run 415 — WinMain and Pre-WinMain Initializers Recovery

## English Summary
Recovery and differential validation of the original standard Win32 entry point and its companion CRT static initializers from `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
1. `004b66d0..004b66e4` (20 bytes): `winmain_set_heap_size_004b66d0` — sets global heap buffer limit `0x0065b290 = 0x800000` (8 MB).
2. `004b66f0..004b6703` (19 bytes): `winmain_compute_scale_004b66f0` — computes float reciprocal scale factor `0x0065b28c = 0x005b24a8 (1.0f) / *(float*)0x0065b290`.
3. `004b6710..004b67a5` (149 bytes): `winmain_004b6710` — standard Win32 `WinMain(hInstance, hPrevInstance, lpCmdLine, nShowCmd)` entry point. It sets `argv[0] = "AppName"`, tokenizes `lpCmdLine` by splitting on spaces (`0x20`), populates `g_argv_0065b20c` (clamped to 32 arguments), sets `g_argc_0065b294`, and calls `app_main_004b6a50(argc, argv)`.

Total PE code recovered: 188 bytes.
Differential native fixture: 12/12 cases passed on physical x86 CPU slab against the original PE machine code, testing empty strings, multi-space delimiters, argument count clamping, argument string parsing, and return code propagation.

## Описание на русском
Восстановление и дифференциальная верификация оригинальной точки входа Win32 и сопутствующих статических инициализаторов из `Porsche.exe`:
1. `004b66d0..004b66e4` (20 байт): `winmain_set_heap_size_004b66d0` — установка размера буфера кучи `0x0065b290 = 0x800000` (8 МБ).
2. `004b66f0..004b6703` (19 байт): `winmain_compute_scale_004b66f0` — вычисление коэффициента масштабирования `0x0065b28c = 1.0f / *(float*)0x0065b290`.
3. `004b6710..004b67a5` (149 байт): `winmain_004b6710` — стандартная точка входа `WinMain`. Инициализирует `argv[0] = "AppName"`, парсит `lpCmdLine` с разбиением по пробелам, заполняет массив указателей `g_argv_0065b20c` (до 32 аргументов), устанавливает `g_argc_0065b294` и вызывает `app_main_004b6a50(argc, argv)`.

Всего восстановлено: 188 байт PE-тела.
Дифференциальный нативный тест: 12/12 проверок успешно пройдены на физическом слэбе x86.

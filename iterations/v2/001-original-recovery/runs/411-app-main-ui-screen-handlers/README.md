# Run 411 — app_main UI screen render & present handlers

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
This run recovers the 3 heavy UI screen render and refresh handlers invoked directly by `app_main_004b6a50`:
1. `0048cdf0..0048d343` (1,364 bytes): `ui_draw_screen_tree_0048cdf0` — multiphase screen tree draw coordinator with 4 synchronization phases, abort handling, and event pump invocation.
2. `0048dcb0..0048e191` (1,250 bytes): `ui_screen_refresh_0048dcb0` — screen layout coordinator and packet dispatcher across modes 0, 1, and 2.
3. `0048e1a0..0048e6ec` (1,357 bytes): `ui_screen_render_present_0048e1a0` — screen render, child list traversal, and frame presentation.

Total recovered PE body bytes: 3,971 bytes across 3 functions.

Game sources are `app_main_ui_screen_handlers_411.cpp` and `app_main_ui_screen_handlers_411.hpp` in this directory. Actual object paths, SHA-256 values, defined/undefined i386 COFF symbols, ordered MSVC include roots, and `/sourceDependencies` files are captured in `summary.json` and validated in `validation.json`. The controlled test fixture and native differential test runner are under `local/experiments/v2-app-main-411`.

`python scripts/research/experiment-v2-app-main-411.py --finalize --attempt 1` compiles with MSVC `/Od /GS- /GR- /EHsc /TP /W4`, links against the native controlled fixture, and verifies identical bit-exact behavior against the original PE bytes on a physical x86 memory slab across 10 controlled differential test cases.
`python scripts/research/audit-v2-app-main-411.py` independently verifies all 3,971 body bytes, receipt logs, and COFF symbols.

---

# Запуск 411 — обработчики отрисовки и отображения экранов интерфейса app_main

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Восстановлены 3 функции подсистемы отрисовки и обновления интерфейса, вызываемые напрямую из `app_main_004b6a50`:
1. `0048cdf0..0048d343` (1,364 байт): `ui_draw_screen_tree_0048cdf0` — многофазный координатор отрисовки дерева экранов с четырьмя фазами синхронизации, обработкой прерываний и вызовом цикла событий.
2. `0048dcb0..0048e191` (1,250 байт): `ui_screen_refresh_0048dcb0` — координатор обновления макета и отправки сетевых пакетов для режимов 0, 1 и 2.
3. `0048e1a0..0048e6ec` (1,357 байт): `ui_screen_render_present_0048e1a0` — отрисовка экранов, обход дочерних узлов и презентация кадра.

Суммарный объём восстановленного PE-кода: 3,971 байт в 3 функциях.
Поведение подтверждено 10 дифференциальными тестами на физическом x86-слебе памяти оригинального бинарника.

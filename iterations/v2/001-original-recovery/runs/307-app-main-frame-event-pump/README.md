# Run 307 — app_main frame event pump & UI mode 3 event dispatcher

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
This run recovers the core frame event pump function invoked directly by `app_main_004b6a50` at callsite `004b6cc4`:
- `004b4da0..004b51d5` (1,078 bytes): `frame_event_pump_004b4da0` — frame event queue pump, screen mode 3 tree traversal & element mapping, event translation, Fisher-Yates element shuffle, string buffer validation, delay regulation, and input subsystem state flush (`sub_00411760`).

Total recovered PE body bytes: 1,078 bytes across 1 function.

Game sources are `app_main_frame_event_pump_307.cpp` and `app_main_frame_event_pump_307.hpp` in this directory. Actual object paths, SHA-256 values, defined/undefined i386 COFF symbols, ordered MSVC include roots, and `/sourceDependencies` files are captured in `summary.json` and validated in `validation.json`. The controlled test fixture and native differential test runner are under `local/experiments/v2-app-main-307`.

`python scripts/research/experiment-v2-app-main-307.py --finalize --attempt 1` compiles with MSVC `/Od /GS- /GR- /EHsc /TP /W4`, links against the native controlled fixture, and verifies identical bit-exact behavior against the original PE bytes on a physical x86 memory slab across 10 controlled differential test cases.
`python scripts/research/audit-v2-app-main-307.py` independently verifies all 1,078 body bytes, receipt logs, and COFF symbols.

---

# Запуск 307 — насос событий кадра app_main и диспетчер событий режима 3 UI

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Восстановлена функция насоса событий кадра, вызываемая напрямую из `app_main_004b6a50` по адресу `004b6cc4`:
- `004b4da0..004b51d5` (1,078 байт): `frame_event_pump_004b4da0` — обработка очереди событий кадра, обход дерева и сопоставление элементов в режиме 3 UI, трансляция событий, тасование элементов алгоритмом Фишера-Йейтса, валидация строкового буфера, регуляция задержки и сброс состояния подсистемы ввода (`sub_00411760`).

Суммарный объём восстановленного PE-кода: 1,078 байт в 1 функции.
Поведение подтверждено 10 дифференциальными тестами на физическом x86-слебе памяти оригинального бинарника.

# Run 413 — app_main render screen driver (004a4a70)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: `004a4a70..004a53e8` (2,424 PE bytes). This routine is directly called by `app_main_004b6a50` at `004b6cca` with calling convention `void CALL_CDECL render_screen_driver_004a4a70(std::int32_t step)`. It serves as the primary loading screen presenter and multi-pass UI renderer, handling background strip rendering (5 horizontal slices across 640x480), car art overlay composition, MLoading graphic sequencing, loading status bar updates, slot table element rendering, Direct3D/DirectDraw presentation flipping, and centered surface blitting.

The recovered C++ implementation is in `app_main_render_screen_driver_413.hpp` and `app_main_render_screen_driver_413.cpp`. All 52 HIGHLOW base relocations and 78 call sites were audited against the original binary disassembly and verified through differential native execution on a physical x86 CPU memory slab (`app_main_fixture.cpp` in `local/experiments/v2-app-main-413/`). 10/10 test cases passed with bit-exact parity against the original retail bytes, covering initialization (`step = 0`), shutdown (`step = 10`), early exit when disabled, render skipping, era-specific car art overlays (`step = 5`), alternate FSH modes, loadtext overlay rendering, UI screen node slot walks (both hidden and active elements), and high-resolution surface centering.

Independent audit script `scripts/research/audit-v2-app-main-413.py` validates the 2,424 body bytes against `Porsche.exe`, checks COFF symbol tables, and ensures reproducibility.

---

## Русская версия (Russian)

Оригинальный `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: `004a4a70..004a53e8` (2 424 байта PE). Процедура вызывается напрямую из `app_main_004b6a50` по адресу `004b6cca` с конвенцией вызова `void CALL_CDECL render_screen_driver_004a4a70(std::int32_t step)`. Она отвечает за отрисовку экрана загрузки и многопроходный рендеринг пользовательского интерфейса: 5 горизонтальных полос фона (640x480), наложение моделей автомобилей, отображение графики MLoading, индикатор прогресса загрузки, обход слотов элементов UI, переключение буферов через указатели драйвера и центрированный вывод поверхности.

Восстановленная реализация на C++ находится в файлах `app_main_render_screen_driver_413.hpp` и `app_main_render_screen_driver_413.cpp`. Все 52 базовых перемещения HIGHLOW и 78 точек вызова выверены по ассемблерному листингу оригинального бинарника и подтверждены дифференциальным нативным тестированием на физическом срезе памяти x86 (`app_main_fixture.cpp` в `local/experiments/v2-app-main-413/`). Все 10 из 10 тестовых сценариев успешно пройдены со 100% побитовым совпадением с оригиналом.

Независимый скрипт аудита `scripts/research/audit-v2-app-main-413.py` сверяет 2 424 байта с оригинальным `Porsche.exe`, проверяет таблицу символов COFF и подтверждает воспроизводимость.

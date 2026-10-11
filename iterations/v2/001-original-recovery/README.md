# v2 / 001 — восстановление исходного кода оригинала

Текущий результат — [Run160](runs/160-crt-text-workers-integration/README.md): **386 проверенных C++ функций** и6 зарегистрированных частичных consumers.
Общая MSVC Win32 сборка:144 projects /270 unique TUs;126 comparison/alias targets,7 native OS и3 link fixtures.
12 свежих original-x86 отчётов /14491 сравнений плюс4 component-proven composed cases; все10 native/link проверок прошли.
Приняты43 новые функции: CRT heap/TLS/locks, текст/locale consumers и сетевые workers/members.
SHA-аудит выполняется батчем с кешем уникальных файлов; inventory ускорился9,3→2,4с на текущем корпусе.
Game-link:0 compile errors /279 unresolved symbols /312 references /0 other diagnostics; игрового EXE нет.
Это текущая граница зависимостей, а не весь остаток: новые тела открывают следующие callees.
131 audio-init и partial00525ec0 остаются изолированными и не зарегистрированы в production.
Отложенные проверки —docs/recovery-validation-backlog.md; полный004d3420, CRT engines и live startup открыты.
Маршрут: проверенный полный C/C++ baseline → схема устройства игры → Rust native/web.
Полный игровой запуск, live timer/WM_CLOSE и визуальная приёмка остаются открытыми.

Начато 2026-10-08 по решению пользователя. Предыдущая разработка сохранена
в коммите `dc6b9d8`; 012 незавершена, продолжение её интеграции остановлено.
001–011 не меняются. Игровые данные общие: `local/game`, только чтение.

[Run 001](runs/001-full-corpus/README.md): все 25 модулей экспортированы,
36 587 функций попытаны декомпилятором; 36 583 псевдо-C результата и
4 failed/timeout сохранены. Основной Porsche.exe — 5772/5772 без failed/timeout.
Это полный автоматический корпус обнаруженного кода. Ручные собираемые
исходники появились в Run 002–003; игрового v2 EXE пока нет.

Цель v2 — восстановить игру целиком из бинарников, получить собираемый
исходный код и исходное поведение, затем переносить платформенные зависимости.
Первый исполняемый результат должен быть Windows/x86-оригиналом из
восстановленного кода. Rust/wgpu прежней версии не задают новую архитектуру.

Образец процесса — [SpaceRangersHD_decomp](https://github.com/pakompom/SpaceRangersHD_decomp):
восстановленный исходный код, закреплённый инструментарий сборки,
проверка функций и финального EXE. Его автор сообщает полное совпадение
SHA Rangers.exe; для Porsche такое совпадение ещё не достигнуто.
Метод и тонкости инструментария описаны в
[development.md](https://github.com/pakompom/SpaceRangersHD_decomp/blob/main/docs/development.md).

Расположение:

- `iterations/v2/001-original-recovery`: план, входной манифест, ручной исходный
  код `source/`, проверки и собственные `runs/`, начиная с 001.
- `research/v2/binaries`: полный листинг каждого модуля, автоматический
  псевдо-C, результаты всех функций и явно нераспознанные области.
- `local/builds/v2/001-original-recovery`: отдельная x86 C++ библиотека и
  консольные verification probes; игровой EXE пока отсутствует.
- `local/experiments/v2-*`: изменяемые эксперименты и дополнительные базы Ghidra.

Существующий индекс покрывает 24 уникальных PE. В v2 учитываются также
16-битный NE `clcd16.dll`, алиасы, драйверы, установщики и патчи; их связь
с игровой сборкой устанавливается отдельно. Неизвестный модуль не исчезает
из отчёта. Покрытие/хеши: [reference/binaries.json](reference/binaries.json).

Ступени восстановления различаются: полный экспорт найденного кода,
автоматическая декомпиляция, ручной собираемый исходник, совпавшая функция,
совпавший модуль. Автоматический `decompiled.c` содержит гипотезы Ghidra о
типах/сигнатурах и не является готовым проектом C/C++. Нераспознанные байты,
косвенные вызовы, ошибки/тайм-ауты остаются в измеримом списке работ.

У Porsche.exe PE linker version 6.0; строка `Microsoft Visual C++ Runtime
Library` находится по VA 0x5c1e5c. Это свидетельства для проверки MSVC-era
toolchain, а не доказательство точного компилятора/ключей/библиотек.
Проверять реальные пробные сборки и машинный код до выбора инструментария.

Сначала собираем и проверяем Windows/x86 baseline. Цель полного совпадения
не достигается постобработкой EXE, копированием оригинальных функций в
результат или заглушками неизвестной игровой логики. Когда компоненты игры
восстановлены, отдельный этап адаптирует графику, звук, ввод и ОС под native/web.
Проверенные прежние источники и replay-стенды используются как свидетельства;
аркадные реализации не переносятся автоматически.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode listing
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode listing -ImportNE
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode decompile
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode decompile -NE
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification
```

NE находится в отдельном проекте; повторный listing использует `-NE` вместо
`-ImportNE`. Первый критерий приёмки 001: все входные SHA учтены,
весь обнаруженный код экспортирован, каждая найденная функция попытана
декомпилятором, ошибки/неопределённые области перечислены. Это ещё не полная
реконструкция игры.

Run 002: пользователь выбрал сразу C/C++, без ассемблерной промежуточной
сборки. Создано [исходное дерево](source/README.md) с адресным каталогом
всех функций и ручными C++ модулями. Переход 0x4b6710 собирается и совпал
с x86 на 175 случаях; callee 0x4b6a50 только записывается в стенде, не восстановлен.
Современный MSVC 19.44.35229 собирает Win32/x86; точная исходная версия
не подтверждена. [Отчёт](runs/002-cpp-startup/README.md),
[граф запуска](reference/startup.json). 1 проверенная ручная функция,
0 байтовых совпадений/целых модулей. Игрового запуска ещё нет.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-startup.py
py -3 scripts/research/structure-v2.py
py -3 scripts/research/trace-v2-startup.py
```

[Run 003](runs/003-fe-stream/README.md): восстановлен цельный участок
fe.txt/command-line → FE stream → исполнение записей: девять новых C++ функций,
таблицы команд/значений/действий и исходные глобальные слова. 236 native/x86
сравнений прошли, настоящий fe.txt даёт 23 записи / 188 байтов. Всего десять
проверенных ручных функций; число байтовых совпадений и целых модулей — ноль.
IO/heap/callback callees ещё не восстановлены: их заменяет запись только в
стенде. Общий реестр — source/recovered/functions.json.

```powershell
py -3 scripts/research/export-v2-fe-tables.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-fe-stream.py
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
py -3 scripts/research/structure-v2.py
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification --verification-output iterations/v2/001-original-recovery/runs/003-fe-stream/corpus-verification.json
```

[Run 004](runs/004-original-heap/README.md): восстановлены 11 функций собственного
heap: создание, выделение с двух концов, выбор максимального подходящего блока,
free со слиянием, resize без перемещения указателя и helpers. Все 551 случай
совпали с оригинальным x86 по всей арене после каждой операции. ABI free
уточнён (возврат 1), 236 FE регрессий повторены в новом run; старые отчёты сохранены.
Всего 21 проверенная ручная функция, 0 байтовых совпадений/целых модулей.
OS/CRT/оптимизированные копировщики пока внешние зависимости.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-heap.py
py -3 scripts/research/verify-v2-fe-stream.py --report-dir iterations/v2/001-original-recovery/runs/004-original-heap/fe-regression
```

[Run 005](runs/005-original-files/README.md): восстановлены 29 функций
файловых очередей, completion/status, чтения блоками и списков. Все 89
совместных FE/heap/IO проверок с x86 прошли, включая настоящий fe.txt;
551 heap и 236 FE регрессий сохранены в новом run. Всего 50 проверенных
ручных функций. Дополнительный SHA index содержит 3 пропущенных callbacks:
каталог 36 587 automatic + 3 supplementary = 36 590 записей.
Disk/thread/VirtualAlloc/OS/CRT остаются внешними границами; игрового EXE нет.

[Run 006](runs/006-file-device/README.md): ещё 6 функций page wrappers,
list constructors/default key/device init сверены на 474 случаях с x86.
89 совместных проверок повторены с настоящими page wrappers; всего 56 функций.
Каталог 36 587 automatic + 5 supplementary = 36 592 записей.
Worker 0x568530 проиндексирован, но пока не восстановлен.

Следующий пакет — worker/control/completion, thread/wait/events и disk/archive
dispatch, затем привязка к startup 0x4b6a50.
Точные адреса и первый шаг — [в плане](PLAN.md).

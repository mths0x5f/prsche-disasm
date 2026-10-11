# Состояние проекта

Текущий результат — [Run153](iterations/v2/001-original-recovery/runs/153-services-integration/README.md): **330 проверенных C++ функций** и6 зарегистрированных частичных consumers.
Общая MSVC Win32 сборка:135 projects /254 unique TUs;119 comparison/alias targets,5 native OS и3 link fixtures.
18 свежих original-x86 отчётов /5816 сравнений плюс4 component-proven composed cases; все8 native/link проверок прошли.
Приняты35 новых функций: float helpers, context ranges/string/vector, network serialization/lists/cleanup.
256 x87 случаев сверены с исходными машинными байтами на CPU;128 расхождений Unicorn сохранены явно.
Game-link:0 compile errors /282 unresolved symbols /313 references /0 other diagnostics; игрового EXE нет.
Это текущая граница зависимостей, а не весь остаток: новые тела открывают следующие callees.
131 audio-init и partial00525ec0 остаются изолированными и не зарегистрированы в production.
Отложенные проверки —docs/recovery-validation-backlog.md; полный004d3420, context move, lowio и live CRT открыты.
Маршрут: проверенный полный C/C++ baseline → схема устройства игры → Rust native/web.
Полный игровой запуск, live timer/WM_CLOSE и визуальная приёмка остаются открытыми.

2026-10-08: активна [v2/001-original-recovery](iterations/v2/001-original-recovery/README.md).
v1 сохранена и запушена: dc6b9d8; 012 незавершена и её интеграция остановлена.
Полные листинги 24 PE + 1 NE экспортированы: 36 587 функций, 2 827 310 инструкций.
Границы нераспознанного кода/данных/паддинга учтены (3 199 385 байтов);
это не готовые исходники. Все функции попытаны декомпилятором: 36 583 псевдо-C,
4 failed/timeout, 5639 функций с предупреждениями. Основной Porsche.exe:
5772/5772 псевдо-C, без failed/timeout. Проверка полного инвентаря прошла.
Сразу C/C++ по выбору пользователя: адресный каталог всего корпуса,
porsche_original.lib и отдельные консольные стенды (Windows x86).
Run 002: startup 0x4b6710 сверён на 175 случаях. Run 003: 9 функций чтения
fe.txt/аргументов, создания и применения FE stream сверены на 236 случаях.
Сравнивались записи, глобальные поля, callbacks и порядок file/heap вызовов;
внешние службы — записывающие границы стенда, ещё не восстановленные callees.
Настоящий fe.txt даёт 23 записи / 188 байтов. Run 004: 11 новых C++ функций
heap init/alloc/free/resize и helpers; 551 случай совпал с x86 по всей арене
после каждой операции. Повторные 236 FE регрессий прошли; free возвращает 1.
Run 005: 29 функций файловой очереди/completion/chunk read и списков;
89 совместных FE/heap/IO сравнений с x86 прошли. 551 heap и 236 FE регрессий
повторены в новом run. Всего 50 проверенных ручных функций; библиотека
содержит реальный FE/heap/IO frontend. Disk/thread/VirtualAlloc/OS/CRT/SIMD
ещё внешние; в стенде completion немедленный, это не исходный scheduler.
Три пропущенных callbacks добавлены в SHA-guarded index: каталог 36 590 записей,
из них 36 587 automatic. 0 байтовых совпадений/модулей; игрового v2 EXE нет.
MSVC 19.44.35229 доступен; точный исходный compiler/CRT/flags не подтверждён.
Worker/thread/wait/events и disk/archive backend открыты; после них совместная
сверка с исходным scheduler и startup 0x4b6a50.
Run 006: 6 новых C++ page/list/device startup функций, 474 сравнения с x86
и 89 совместных регрессий прошли. Настоящие page wrappers включены в FE/heap/IO;
Win32 APIs остаются записывающими границами. Всего 56 проверенных функций,
каталог 36 592 записей (5 supplementary). Worker 0x568530 проиндексирован,
его loop/thread/wait/events/disk ещё открыты. Следом worker jump table/dispatch.
Отчёт: runs/006-file-device внутри v2/001. Визуальная приёмка открыта.
Пути: iterations/v2/001-original-recovery, research/v2/binaries,
local/builds/v2/001-original-recovery. Исполнитель — координатор.

2026-10-08: пользователь попросил закоммитить текущее состояние и перейти
к отдельной v2 с полным восстановлением бинарников. 012 сохраняется незавершённой.
Run 020: 47 исходных four-wheel loops / 188 состояний совпали с Rust.
221 tests (3 ignored), fmt/clippy/wasm32/native/web и 3 Quick Race прошли.
Общий browser прогон Run 020 не завершён; force adapter/binding открыты.
Run 019 запушен: 13b70f1. Дальнейшие игровые правки 012 остановлены.

Run 019, 2026-10-06: общие polygon+EDG tree и wheel support работают в игре.
3 дерева / 27 EDG queries, 8 body selections, 45 scene-dependent responses,
5 height / 29 material-state cases совпали с x86. 220 tests (3 ignored),
fmt/clippy/wasm32, native/web, 3 Quick Race и 21 browser check прошли.
Body/wheel APIs ещё не заменяют force adapter. Остаток: исходные поля,
full 0x499a70/cadence, special/car-car, UI/миссия/визуальная приёмка.
012 открыта, активных исполнителей нет; координатор завершил частичный код
после лимита worker. Запуск: local/builds/012-campaign-fidelity/Launch-desktop.cmd.

Run 018 внутри 012, 2026-10-06: восстановленные type-1 опоры подключены
к реальной загрузке трасс и четырём колёсам. Ordinary Base filter, retained
flag-1 loader, mt/vt/df/pr, дерево, два кэша и plane query работают в заезде;
RD* и Skidpad mt53/54 подбор исключён. На 15 трассах 237 395 полигонов.
9 loader / 10 owner случаев совпали с x86; 215 Rust-тестов прошли (3 ignored),
fmt/clippy workspace -D warnings, wasm32 и native+web release прошли.
Quick Race Skidpad/Alps/Canyon: реальные кэши четырёх колёс, нагрузка, движение,
высота проверены; 21 общий browser check прошёл. Отчёт/команды/кадры:
runs/018-original-support-runtime. Запуск: local/builds/012-campaign-fidelity/Launch-desktop.cmd.
Силы подвески и body response пока прежний adapter; prepared-contact kernel
не подключён. Type-2/box/cylinder в общем дереве, mutable Base ordinal и
полный original wheel state/forces остаются незавершёнными; 012 открыта.
Назначения исполнителей завершены. Следующий конкретный шаг координатора:
смешанная сцена → original 0x499a70 state/alternate height/force consumers →
геометрия 0x495020 и response 0x494000. Сверка реальной езды с оригиналом обязательна.

Run 017 внутри 012, 2026-10-05: исходные type-1 insertion/split и cached
support query соединены в отдельном Rust-модуле. 38 callback / 304 predicate
cases, 36 полных деревьев и 72 полных запроса совпали с исходным x86. Original
allocator/vector code исполнен на заданной арене; Win32 locks — один поток.
20 Rust-тестов, fmt/clippy -D warnings и wasm32 прошли. Источник/команды —
runs/017-original-support-insertion. Runtime fa56d05, 012 открыта.
Найден special producer: animdefs.txt → 0x47eba0 → 0x628ba0; 0x47ed90 на
неизвестном ненулевом Base tag возвращает первый ENDW/kBox, а не null.
Следом координатор: полный polygon loader 0x475543..0x47591e, original
special lookup/parser и Base ordinal producer, затем state/cadence автомобиля.
Цель подключения в 012 — первая трасса с исходными опорами и контактом.

Run 016 внутри 012, 2026-10-05: Base/pr readers и child constructor дерева
перенесены из оригинальных consumers в отдельные Rust-модули. 317 primitive
payload cases / 2536 helper outputs, 60 Base и 256 child cases сверены с x86.
Rust проверил 15 трасс: 74 300 pr / 16 591 Base. 16 тестов, fmt/clippy -D warnings
и wasm32 check прошли; источник/команды — runs/016-original-support-assembly.
Исполнитель по insertion остановлен лимитом; source export сохранён, child
constructor завершён координатором. Активных назначений нет. Сборка fa56d05,
012 открыта; новые модули пока вне игрового цикла. Следом координатор:
0x484320 + type-1 vtable+4/+8 callbacks → insertion replay; затем полный loader
(ordinal producer/special/alternate/degeneracy) и связь с state/cadence авто.

Run 015 внутри 012, 2026-10-05: material flags = mt payload+0 доказаны;
208 x86 material cases и 10 plane/gap cases проверены, перенесены в pure Rust.
Rust независимо проверил 15 трасс / 3651 mt entries; 11 тестов, fmt/clippy
и wasm32 check прошли. Источник/команды — runs/015-original-support-loader.
Исполнители завершили работу. Runtime пока прежний (fa56d05), 012 открыта.
Следом координатор: Base/pr/vt selection в0x4750b0, insertion0x484ae0/483bd0,
затем сцена → state автомобиля и исходный cadence; приближений не подключать.

Run 014 внутри 012, 2026-10-05: исходный spatial bounds/traversal/cache
перенесён в pure Rust. 572 результата совпали с исполнением оригинального x86;
семь Rust-тестов, fmt/clippy и wasm32 check прошли. Source/fixtures — Run 014.
Путь owner → material flags установлен; raw mt offset ещё неизвестен.
Runtime не подключён, сборка fa56d05.
Ближайший шаг: raw flags linkage, plane/split loader, построение дерева
и связь с состоянием авто. Исполнители завершили работу.

2026-10-05, Run 013 внутри 012: исходные support polygon predicates и выбор в
готовом листе перенесены в Rust. 36+10 результатов сверены с оригинальным x86;
10 quad-split случаев также исполнены. Три Rust-теста (включая 468 контактов),
fmt/clippy и wasm32 check прошли. Выбор/загрузка листа сцены ещё не подключены.
Прослежен источник timer128/derived counters64Гц; cadence интеграции остаётся открытой.
[Run 013](iterations/012-campaign-fidelity/runs/013-original-support-query/README.md).

2026-10-05, Run 012: исходная реакция подготовленного контакта перенесена
в отдельный Rust-модуль; 468 состояний совпали с исполнением исходного x86.
Восстановлены ветка поворота, её Y-поле и геометрия точек/нормали. 103 теста
nfs-assets, fmt/clippy и wasm32 check прошли. К игровому циклу ещё не подключено:
нужны полный запрос сцены и cadence исходного интегратора. Сборка остаётся fa56d05.
[Отчёт и команды](iterations/012-campaign-fidelity/runs/012-original-contact-kernel/README.md).

2026-10-04, Run 011: пользователь выбрал восстановление оригинала вместо
подбора похожих реализаций во всех подсистемах, включая существующий код.
Sweep сохранён отдельно и снят с runtime; в release не попадал.
Последняя игровая сборка/коммит — fa56d05. 012 открыта: физика/UI/миссии
ещё требуют оригинальных consumers и приёмки. 013 (повреждения + рынок б/у)
пока только план. Правила закреплены в AGENTS.md и .cursor/rules.

2026-10-05: доказана цепочка EDG → пространственный запрос → 0x494000.
64 дифференциальных случая участка реакции прошли на исходных x86-инструкциях
в Unicorn; геометрия задана фикстурой, угловой callback отключён. Результаты:
[разбор реакции](iterations/012-campaign-fidelity/research/original-collision/response.md).
Игровой код не менялся; далее угловая реакция и полный контракт контакта.

2026-10-04: пользователь подтвердил прохождение первой Factory-миссии, но
«Продолжить» повторно открывает результат. Run 010 исправляет JS lifecycle;
UI regression и пять Factory Rust-тестов прошли. Windows/WASM собраны.
Chromium: Continue → список → 1m01 → реальный старт, сохранение после reload,
fail/retry без цикла, 0 JS errors. Финиш задан тестовой фикстурой; проходимость
1m01 не заявляется. Исправлен её SIM: boxster.sim (отсутствует) → boxster25.sim.


Обновлено 2026-10-03. Активна **012-campaign-fidelity** из завершённой 011.
Текущий план: [iterations/012-campaign-fidelity/PLAN.md](iterations/012-campaign-fidelity/PLAN.md).

## Активная 012: исправление соответствия оригиналу
Run 008: реальные wheel pivots/радиусы/mesh groups из CRP подключены к физике
и рендереру. Работают вращение/руление колёс, ход подвески игрока, контакт кузова
с трассой и столкновения player/AI/AI. CPU: 184 passed; Windows/WASM собраны.
Chromium: 21/21 общих проверок, wheel pivots/анимация и столкновение Quick Race
прошли; оба заезда 0M01 — 5/6 точек без переворота, затем тайм-аут. Коммит 9efb71c.
Run 009: версионируемый индекс оригинала готов в `research/binary-index/`:
25 PE-путей / 24 уникальных бинарника, 36 510 функций и 1 274 749 ссылок.
NE-библиотека clcd16.dll явно не покрыта; полнота семантики и косвенных вызовов не заявляется.
Правило поиска по индексу перед реализацией закреплено в AGENTS.md и .cursor/rules.
Предыдущий опубликованный промежуточный checkpoint: cb07500.
Предыдущий опубликованный checkpoint по запросу пользователя:
[Run 007](iterations/012-campaign-fidelity/runs/007-publish-checkpoint/README.md).
Quick Race, source SIM, SCN-триггеры/стрелки и исправления поверхности собраны;
полное прохождение 0M01 и оригинальная физика НЕ приняты. Следующий результат —
одна миссия от старта до корректного итогового экрана с короткими коммитами.

Текущий checkpoint 2026-09-29: исправлены обратный знак стабилизатора и геометрия
луча подвески; 172 Rust-теста passed, 3 GPU ignored, Clippy/fmt чисты,
Windows/WASM собраны. Полный заезд attempt-5 по-прежнему переворачивается после
2-й точки; коллизии кузова с землёй нет. Найдена неподтверждённая трактовка
SIM 0x10c/0x110 как колеи: Boxster runtime получает принудительный 1 м.
Следующий приоритет — EXE consumers и источник геометрии колёс, затем повтор
миссии и result/penalty flow. Подробности и все попытки — в Run 006 ниже.

Предыдущие checkpoints Run 006:
Run 006: исправлен провал после первой точки — подключены все исходные сектора
Skidpad mt53/mt54 вместо одного MESH04; исключено одноимённое здание.
169 Rust-тестов passed, 3 GPU ignored; Clippy/fmt чисты, Windows/WASM собраны.
Реальный повтор прошёл 4/6 точек без падения и JS-ошибок, затем тайм-аут на
развороте; профиль не изменился. Полное прохождение ещё не подтверждено.
Далее — телеметрия разворота (управление/физика), затем result/penalty flow.
Attempt-3: кузов переворачивается (up.y до -1). Обнаружен и исправлен обратный
знак сил стабилизатора; тест до правки воспроизводит усиливающий крен момент.
Проверка исправления в полном заезде ещё выполняется.
2026-09-29: attempt-4 всё ещё переворачивается. Исправлена следующая причина:
неверное расстояние до земли и ложный контакт перевёрнутых колёс. Новый raycast
подвески проверяется на конечных треугольниках, наклоне и границах grid cells.
[Run 006](iterations/012-campaign-fidelity/runs/006-mission-playthrough/README.md).

Run 005 проверен 2026-09-28: runtime использует восстановленный shape1 predicate —
диагонали корпуса, height band, source direction/speed constraints, type-based End.
169 Rust-тестов passed, 3 GPU ignored; Clippy/fmt/UI чисты; Windows/WASM собраны;
Chromium 21 checks, 0 errors/known failures. Срабатывание первой точки корпусом,
gate count и reset проверены реальным W/R вводом; кадр после точки осмотрен.
Размеры берутся из видимой модели, pose/velocity из sim; exact original selected
bounds/body origin/contact correction ещё не доказаны. Полное прохождение 0M01,
штрафы/результаты и UI 1:1 открыты. Активных назначений нет, агенты остановились по лимиту.
[Run 005](iterations/012-campaign-fidelity/runs/005-trigger-contract/README.md).

Run 004: animdefs.txt triggerable и упорядоченные ссылки SCN подключены к runtime.
По восстановленной reset-цепочке Start выбирает Arrow 1, проезд первого триггера
переключает Arrow 2, повтор возвращает Arrow 1. L A остаётся скрытой; стартовый
кадр осмотрен, перекрытие камеры устранено. 166 Rust-тестов passed, 3 GPU ignored;
Clippy/fmt/UI чисты, Windows/WASM собраны; Chromium 21 checks, 0 errors/known failures.
Оригинальные условия прохождения, spawn/камера и UI 1:1 ещё не доказаны.
[Run 004](iterations/012-campaign-fidelity/runs/004-scenario-arrows/README.md).
Назначений агентам нет. Следующие записи — история проверок предыдущих runs.

Run 003: исправлена численная смена знака omega от тормоза в physics/tire.rs.
До исправления 2/4 сценарных повторов не возвращались из R, после — 8/8 passed.
Подключён масштаб SCN v4: 162 Rust-теста passed, 3 GPU ignored; Clippy/fmt/UI чисты,
Windows/WASM собраны. Chromium: 20 checks passed, 0 errors, 0 known failures.
Кадр 0M01 просмотрен: L A / ARW1 по-прежнему закрывает камеру. Восстановлена цепочка
animdefs.txt triggerable → initial hide → trigger-linked selection; в runtime она
пока не подключена, первая активация требует дальнейшего реверса. Назначений агентам нет.
[Run 003](iterations/012-campaign-fidelity/runs/003-factory-diagnostics/README.md).
Run 001/002 ниже сохраняют исторические checkpoint, включая уже исправленный сбой.

- Замечания пользователя: чужой интерфейс, смешанное оформление карьер, неправильный
  Factory Driver/старт миссий, подлёты, отсутствие заднего хода после торможения на S.
- Checkpoint 2026-09-26: T01–T04 частично выполнены, итерация остаётся открытой.
  Исправлены первый контакт, фиктивный пол, плечи осей и S тормоз→стоп→задний ход (W симметрично).
  Калибровка на реальных SIM: 356 — 54.7 м, Boxster — 43.3 м со 100 км/ч, без опрокидывания.
  Для 0M01 добавлены SCN Start, опора MESH04 и waypoint 1–5→End; общий круг LSP больше не даёт
  победу Factory, неподдержанные сценарии не получают награду. Правила пока реконструированы.
- 151 Rust-тест passed, 3 GPU ignored; Clippy/fmt/UI-тесты чисты. Release Windows/WASM собраны.
  Chromium: 14 автоматических проверок, 0 ошибок, включая руль и удержание S/W; см.
  [Run 001](iterations/012-campaign-fidelity/runs/001-fidelity-repair/README.md).
- Визуальная приёмка НЕ пройдена: на кадре 0M01 камера перекрыта геометрией. Точный spawn offset,
  правила оригинала, UI 1:1 (комнаты/шрифты/слои) и реальное прохождение ещё не подтверждены.
  В продолжении Run 002 добавлена загрузка SIM в web runtime, проверка повреждённых файлов
  и исправлена ссылка Boxster на `boxster25` по nfs5.car. Native CLI пока использует таблицы.
- Run 002: добавлен Quick Race с выбором трассы/автомобиля, 1/3/5 кругов и 0/3 AI,
  без карьерных наград. Windows/WASM собраны, 157 Rust-тестов passed, 3 GPU ignored;
  Clippy/UI чисты. Финальный Chromium: 19 checks passed, 0 JS errors и 1 known failure
  (нестабильный R→вперёд Boxster в 0M01). Quick Race S/W проходит; общий verifier не green.
- Исправлены знак поворота кинематического AI и lookahead спринта. Аудит 15 трасс теперь
  измеряет прогресс вдоль пути: раньше проверялось удаление от пути >50 м, так что прежний
  pass не доказывал следование маршруту. Исправленный аудит прошёл. AIS/AI-таблицы,
  финиш спринта и исходный состав участников кампании остаются открытыми.
- UI разделяет карьеры и частично следует LAY 640x480. Извлечение 119 PNG воспроизводимо через
  `scripts/extract-fe-ui.ps1` в `local/derived/fe-ui`. Повторный
  [Computer Use](docs/computer-use-recovery.md): `sky.list_apps()` → `spawn EPERM`.
  Назначений агентам нет; результаты и команды — [Run 002](iterations/012-campaign-fidelity/runs/002-runtime-sim/README.md).
- Снимки 001–011 неизменны. Прежние отчёты ниже — история проверок, а не доказательство
  полного сходства с оригиналом; соответствие 011 оспорено замечаниями пользователя.
- Звук/кокпит отложены до исправлений карьер и управления.

Полный перенос с обеими карьерами: [дорожная карта](docs/roadmap.md).

## Завершённая итерация: 011-factory-driver
- [Run 001](iterations/011-factory-driver/runs/001-factory-driver/README.md):
  - T01: бинарный реверс всех 34 миссий `nfs5.fac` и языковой базы `festrings.csv`.
  - T02: движок испытаний `factory_driver.rs` в `crates/nfs-game`: детекторы трюков `StuntDetector` (180° slide, 360° spin, reverse J-turn, слаломные штрафы, контроль повреждений кузова).
  - T03: система карьерного роста пилота (Applicant -> Junior Test Driver -> Test Driver -> Senior Test Driver -> Chief Test Driver -> Master Ace) и наградные автомобили ('78 911 Turbo 3.3, '73 Carrera RS 2.7, '99 911 GT3 Factory Edition).
  - T04: модальное окно `#factoryMissionsModal` с фильтрами уровней сложности Tier 1–3, репликами шеф-инструктора Рольфа, статусами и лучшими временами.
  - T05: устранение дефектов кампаний и аутентичность интерфейса:
    - Аутентичная игровая оболочка Need for Speed: Porsche Unleashed (2000) по макетам `bottombar.lay`, `singleplayer.lay`, `factorydriver.lay`: полноэкранный шелл, верхний брендовый хедер PORSCHE, статус-бар с балансом CR и рангом, левая колонка рубиновых пилюль `.nfs-pill-btn`, нижняя панель с кнопкой ESC и светящейся овальной кнопкой RACE (`racebutton.fsh`).
    - Аутентичный экран брифинга миссий (`missionbrief.lay`): реальное фото Рольфа (`people_rolp.png`), технические чертежи заданий (`map_*.png`, 34 схемы) с расстановкой конусов и стрелками.
    - Аутентичный круглый щиток приборов Porsche в заезде (`hud.fsh`): аналоговый тахометр с redline (6.5–8k) и стрелкой, янтарный цифровой спидометр (км/ч) и индикатор передачи.
    - Устранение ошибки покупки авто (`missing or invalid 'version'`).
    - Загрузка настоящих 3D-моделей Porsche (`.crp`/`.fsh`) и параметров симуляции в сюжетных заданиях вместо коробчатой заглушки.
    - Исправление масштаба 1:1 (x5.0) и разворот модели на 180° вперед по ходу трека.
    - Исправление трассы Canyon и заземления машины со старта Evolution.
  - T06: 142 теста Rust passed across workspace, Clippy `-D warnings` чист, Rustfmt чист, Playwright Chromium E2E (12/12 checks, 0 errors), сборка release native и WASM.
- Задачи T01–T06 завершены, тег `iteration-011`.

## Завершённая итерация: 010-evolution-career
- [Run 001](iterations/010-evolution-career/runs/001-evolution-career/README.md):
  - T01: бинарный реверс турниров (`nfs5.trn`), запчастей (`nfs5.prt`), цен и износа.
  - T02: турнирный движок Evolution с эпохами (Classic, Golden, Modern), зачётной системой очков (10-6-4-3-2-1), прогрессией этапов и призовыми.
  - T03: автосалон новых автомобилей и рынок подержанных (Б/У) с динамическим пробегом и остаточной стоимостью.
  - T04: каталог запчастей и тюнинга, влияние на физику, износ узлов и процедура ремонта.
  - T05: полный стресс-тест физики на всех 15 трассах: 0 туннелирований на скоростях до 252 км/ч, проверка полотна и удержания.
  - T06: интеграция UI, 138 тестов Rust passed, clippy `-D warnings` чист, fmt чист, Playwright Chromium E2E (0 errors), сборка native и WASM.
- Задачи T01–T06 завершены. Документированы скрипты в `docs/scripts.md`.

## Проверенный результат

### 009-game-shell
- [Run 001](iterations/009-game-shell/runs/001-controls-regression/README.md):
  - T00: исправление инверсии руля в 6 DOF физике (`vehicle.rs`), отрицательный угол для правого поворота колёс при направлении -Z.
  - Регрессионный стенд: воспроизведение бага до исправления, 21 тест `porsche-viewer` зелёный, web input checks, Playwright тест знака курса.
- [Run 002](iterations/009-game-shell/runs/002-game-shell/README.md):
  - T01: независимый крейт `crates/nfs-game`, архитектурная машина экранов `Screen`, идемпотентная обработка результатов и защита от гонок загрузки.
  - T02: профиль игрока `PlayerProfile` (11 000 CR, гараж, ранги), атомарное сохранение `.tmp` -> rename на диске, `localStorage` и JSON импорт/экспорт в Web.
  - T03: бинарное исследование `nfs5.trn` и `nfs5.fac`, парсеры турниров и миссий в `nfs-formats/src/career.rs`, отчёт [`research/first-events-evidence.md`](iterations/009-game-shell/research/first-events-evidence.md).
  - T04: сквозной запуск первых карьерных событий: Evolution 356 Challenge (Canyon, Monaco 1; взнос 2 000 CR, приз 4 500 CR) и Factory Driver 0M01 (Skidpad, Boxster, лимит 32.0 с).
  - T05: базовый звук: WebAudio синтезатор (RPM, визг шин, сигналы отсчёта/финиша) и WinMM beeper для native; модальные окна брифинга, профиля и результатов.
  - 129 Rust-тестов passed, clippy `-D warnings` и fmt чистые, release native/WASM собраны, 10 проверок Chromium WebGPU пройдены.
- Задачи T00–T05 завершены, код закоммичен, тег `iteration-009`.

### 008-race-loop
- [Run 001](iterations/008-race-loop/runs/001-race-loop/README.md):
  - T01: конечный автомат гонки (`RaceSession`): состояния `Loading`, `Countdown(3..2..1..GO)`, `Racing`, `Paused`, `Finished`, `Results`, секундомеры, время круга, лучший круг (`best_lap`), дельты сплитов.
  - T02: маршрутизация и чекпоинты (`TrackCourse`): реверс-инжиниринг бинарного формата EA Canada `.lsp` (Line Spline Path), 30 файлов трасс валидированы со 100% успехом, автоматическая классификация кольцо/спринт (порог gap < 60м), ворота чекпоинтов с защитой от срезок, детекция движения против хода («Wrong Way»).
  - T03: столкновения с барьерами (`BarrierCollider`): отскок от кромок полотна `.edg` с коэффициентом восстановления 0.35 и касательным трением 0.75, предотвращение вылета за пределы трека.
  - T04: соперники ИИ и стартовая решётка (`AiOpponent`): следование траектории с чистым преследованием (pure pursuit) и адаптацией скорости под кривизну $v = \sqrt{a_{lat}/\kappa}$, профили на основе `.ais`, шахматная стартовая решётка до 8 машин, живая таблица позиций по пройденной дистанции.
  - T05: гоночный HUD и экран результатов: бейдж позиции (P1/4), счетчик кругов (Lap 1/3), секундомер, таймер лучшего круга, пульсирующий баннер обратного отсчёта, предупреждение Wrong Way, модальное окно финиша в Web и телеметрия в заголовке Native окна.
  - T06: сквозной integration тест (`tests/race_integration.rs`): 115/115 тестов passed; чистые `fmt` и `clippy -- -D warnings`; полная сборка release native и WASM.
- Задачи T01–T06 завершены, код закоммичен, тег `iteration-008`.

### 007-physics-simulation
- [Run 001](iterations/007-physics-simulation/runs/001-physics-simulation/README.md):
  - T01: 6 DOF Rigid Body динамика (`rigid_body.rs`): масса, моменты инерции, кватернион ориентации, локальные/мировые преобразования, численный интегратор с подшагами $\le 1/240$ с.
  - T02: силовая установка и КПП (`powertrain.rs`): 21-точечная сетка крутящего момента с шагом 500 RPM из `.sim`, динамика оборотов маховика (холостой ход, отсечка, сопротивление вращению), передаточные числа и главная передача.
  - T03: 4-колёсная независимая подвеска (`suspension.rs`): лучевые запросы к spatial grid `surface.rs`, силы пружин, амортизаторы сжатия и отбоя (bump/rebound), стабилизаторы поперечной устойчивости, динамический перенос веса кузова.
  - T04: шинная модель и тормоза (`tire.rs`): продольный (slip ratio) и поперечный (slip angle) увод шин, эллипс трения Кулона, коэффициенты `front_grip`/`rear_grip` из `.sim`, статический замок тормозов при остановке.
  - T05: калибровочный стенд (`calibration_bench.rs`): 102/102 unit/integration тестов passed; битовый детерминизм подтверждён; воспроизведение потока управления из `replay.rpl`; разгон и торможение 356A (0-100 за 14.37 с, 100-0 за 43.9 м) и Boxster 2.5L (0-100 за 7.83 с, 100-0 за 41.5 м).
  - T06: интеграция в просмотрщик (desktop/web): переключение на лету клавишей `M` / кнопкой UI между 6 DOF симуляцией и аркадным прототипом; телеметрический HUD со спидометром, тахометром, передачей, перегрузкой $g$ и реакцией колёс; чистые `fmt` и `clippy -- -D warnings`; полная сборка native и WASM.
- Задачи T01–T06 завершены, код закоммичен, тег `iteration-007`.

### 006-game-systems
- [Run 001](iterations/006-game-systems/runs/001-game-systems/README.md):
  - T01: PE-карта `nfs5.exe`, функции загрузки `.sim` (`0x0049c750`), `.ais` (`0x0049ca30`), масштабирующие коэффициенты. См. [`simulation-evidence.md`](iterations/006-game-systems/research/simulation-evidence.md).
  - T02: парсеры `SimCar` (328 байт) и `AisCar` (304 байта) в `nfs-formats/src/sim.rs`. Валидация 88/88 `.sim` и 22/22 `.ais` файлов.
  - T03: архитектура сохранений `.sav` (связный список секций `0x0065b634`), парсеры каталогов `nfs5.car` (109 авто), `nfs5.trk` (15 трасс), `nfs5.fac` (34 миссии Factory Driver) в `nfs-formats/src/career.rs`. См. [`career-evidence.md`](iterations/006-game-systems/research/career-evidence.md).
  - T04: реверс детерминированных реплеев `replay.rpl` (8 суб-сэмплов на тик, RLE-поток ввода, заголовок 15 908 байт на 8 авто), парсер `ReplayFile` в `nfs-formats/src/replay.rs`, открытие 500-RPM сетки крутящего момента, baseline стенд в `local/experiments/bench/sim_baseline.json`. См. [`telemetry-evidence.md`](iterations/006-game-systems/research/telemetry-evidence.md).
  - T05: интеграция, 83 unit-теста passed, `fmt` и `clippy` (`-D warnings`) чистые, полная сборка `build.ps1 -Target all` (native + WASM) выполнена без ошибок.
- Итерация завершена, закоммичена, тег `iteration-006`.

### 005-unified-driving
- [Run 001](iterations/005-unified-driving/runs/001-unified-driving/README.md):
  - Общий desktop/web запуск (`scripts/launch-viewer.ps1`), три `Launch-*.cmd`; desktop — web/WASM в отдельном окне Edge/Chrome. Native CLI сохранён, добавлен каталог без аргументов и непрерывный ввод по кадрам. Пользователь подтвердил интерактивную работу.
  - Web UI: Esc скрывает/возвращает меню, H выключает приборы, диагностика отдельно.
  - Прототип: плавный руль, ограничение угла по скорости, максимум 240 км/ч, подшаги ≤1/120 с и фильтр кромок по высоте. Это не оригинальная физика.
  - CPU spatial grid по статическим RD* треугольникам до batching: высота/нормаль, выбор ближайшего допустимого уровня и исходный article/primitive/triangle ID. Все 15 трасс прошли centroid audit (109 707 треугольников), худшая ошибка 0.000164 м.
  - 72 unit tests passed, 3 специальных GPU tests ignored; fmt/clippy чистые; release native/WASM собраны; 44/44 модели загружаются.
  - Playwright 1.57 + обычное окно Chromium: меню/заезд/HUD/каталог/focus проверены, ошибок страницы нет. Native offscreen Vulkan — skidpad и 356a осмотрены.
  - Реверс: воспроизводимый аудит PE/EDG/JNC, оговорки о семантике флагов, инвентарь FEData/Simulation/savedata для карьер.
- Предыдущие снимки: `001-car-viewer`, `002-track-viewer`, `003-track-environment`, `004-track-topology`.
- [План 005](iterations/005-unified-driving/PLAN.md). [Следующий этап](docs/next-iteration.md).
- Задачи T01–T06 завершены, код закоммичен, тег `iteration-005`.

### 004-track-topology
- [Run 001](iterations/004-track-topology/runs/001-topology-verification/README.md): offscreen Vulkan-снимки треков и автомобиля:
  - `skidpad_topology.png`: отображение 167 кромок дорожного полотна skidpad (121 непрерывная линия) поверх геометрии без z-fighting.
  - `autobahn_topology.png`: корректная отрисовка многополосных линий и развязок автобана поверх ландшафта.
  - `car_356a_regression.png`: отсутствие визуальных и логических регрессий при отрисовке автомобилей (356A).
- Форматы `.jnc`, `.edg`, `.map` полностью исследованы и специфицированы в `local/research/004-track-topology/README.md`.
- Парсеры `nfs-formats/src/topology.rs`: валидированы все 15 трасс игры без сбоев.
- Сборка полилиний в `nfs-assets/src/track_loader.rs`: связывание последовательных сегментов границ дорожного полотна.
- Рендеринг `TopologyRenderer` в `porsche-viewer`: WGSL шейдер линий, глубинное смещение `clip_pos.z - 0.0004 * clip_pos.w`, переключатель видимости (hotkey `T`, API `set_show_topology`).
- Веб-интерфейс: автозагрузка ресурсов по дефолту из `local/game` (без необходимости выбирать файлы вручную), сохранение кнопок ручной загрузки («Папка игры», «Файлы») для переопределения с кнопкой сброса обратно к `local/game`, нативный выпадающий список `<select id="targetSelect">` для мгновенного выбора трасс/авто без стирания текста, чекбокс «3D Границы».
- **Аркадная навигация по трассе (Arcade Car Navigation)**:
  - Стилизованный спорткар Porsche (`car_mesh.rs`) со сменой цветов палитры (горячая клавиша `P`).
  - Аркадная физика автомобиля (`arcade.rs`): разгон, торможение, руление с учётом скорости, ручной тормоз с заносом (Space), расчёт передачи (1..5, R, N) и оборотов двигателя (RPM).
  - Привязка к дорожному полотну: адаптация высоты ($Y$) и наклона кузова по уклону и виражам дороги (`sample_road_elevation_fromEdges`), отскок от границ `.edg`.
  - Динамическая камера от 3-го лица с плавной интерполяцией и переключением видов (Chase / Bumper / Free, клавиша `C`).
  - Гоночный HUD в веб-версии: полупрозрачный стеклянный спидометр (км/ч), индикатор передачи, шкала тахометра (RPM) и подсказка клавиш. В нативном окне статус отображается в заголовке окна.
- Исследовательские скрипты реверса сохранены в версионируемой папке `scripts/research/`.
- Тесты: 53 unit-теста проходят (26 в assets, 21 в formats, 6 в viewer), `cargo clippy --all-targets -- -D warnings` и `cargo fmt` чистые, release native и WASM сборки собраны. Интерактивная проверка в браузере выполнена (Playwright + ручной тест).

### 003-track-environment
- [Run 001](iterations/003-track-environment/runs/001-environment-baseline/README.md): offscreen Vulkan-снимки трека `skidpad`:
  - `skidpad-overview.png`: общий вид кругового трека Skidpad с высоты с расставленными пропами (конусы слалома, стартовая стрелка) и панорамой горизонта.
  - `skidpad-cone-macro.png`: макро-вид дорожного конуса `CONE`, стоящего на поверхности асфальта, без парения и смещений.
  - `skidpad-arrow-macro.png`: крупный план стартового указателя направления `ARW1`.
  - `skidpad-driver-view.png`: вид с водительской позиции на трассу (конус створа, дорожное покрытие, строения, ограда и естественный горизонт).
- Парсинг сценариев расстановки `.scn` (`nfs-formats/src/scn.rs`): декодирование координат, ориентации 3x3 и FourCC. Сопоставление 11/11 элементов на `skidpad_st1.scn`.
- Инстанцирование динамических библиотечных пропов (`Base & 0x8000 != 0`): шаблоны пропов сохраняются в `scene.prop_articles` и отрисовываются исключительно через проход инстанцирования (`PropDraw`), предотвращая артефакт парения в начале координат (0, 0, 0).
- Загрузка и рендеринг неба: текстура горизонта `horz` из `Sky/<track>.fsh` (два вертикальных тайла 256x128) разворачивается в цилиндрическую панораму 360° с гладким затуханием в фоновый цвет земли/неба (`sky.wgsl`).
- Нулевая регрессия: все 44 автомобиля (`44/44 passed`) и все 15 трасс (`15/15 passed`) успешно загружаются и валидируются.
- Тесты: 40 unit tests pass, `cargo clippy -- -D warnings` чист, `cargo fmt` проверен, native и WASM сборки собраны.

### 002-track-viewer
- [Run 001](iterations/002-track-viewer/runs/001-track-baseline/README.md): offscreen Vulkan-снимки трека `skidpad`:
  - `skidpad-overview.png`: общий вид кругового трека, внутренней площадки и ландшафта.
  - `skidpad-road-joint.png`: макро-вид бесшовного стыка смежных блоков дорожного полотна `RD0040C` и `RD0048C` (расстояние между вершинами 0.00000).
  - `skidpad-tirewall.png`: макро-вид шинных отбойников `tir1`, каменных стен, деревьев и строений.
- [Run 002](iterations/002-track-viewer/runs/002-texture-format-and-batching/README.md): исправление 16-битных текстур FSH `0x7e` (ARGB 1555) и батчинг мешей:
  - Устранена фиолетовая пикселизация на `farmland`, `castle`, `foothills`, `industrial`, `monaco1`, `monaco2`, `monaco4`.
  - Батчинг геометрии по материалам сократил число буферов/мешей на 97% (`castle` с 11 296 до 263, `industrial` с 8 101 до 240, `farmland` с 3 836 до 184), предотвратив исчерпание ресурсов WebGPU.
  - Добавлены снимки с высоким приближением (zoom-in) и общим планом, подтверждающие отсутствие артефактов.
- Парсинг `karT` контейнеров CRP (`nfs-formats/src/track.rs`), поддержка типов примитивов 3 (треугольники), 4 (квады) и 1 (triangle strips с пропуском дегенеративных связок).
- Декодер FSH поддерживает форматы: `0x7d` (BGRA 32bpp), `0x7f` (BGR 24bpp), `0x7b` (палитровые 8bpp), `0x78` и `0x7e` (ARGB 1555 16bpp с 1-битной альфой). Все 15 трасс игры успешно валидируются и загружаются.
- Сборка мешей `nfs-assets/src/track_loader.rs`: 100% сопоставление материалов по `mt+0x28` с именами FSH-текстур. Координаты в метрах, трансформация `[x, y, -z]` с обходом CCW даёт правильные нормали дорожного полотна.
- Фильтрация библиотечных пропов по флагу `Base & 0x8000 != 0` устранила артефакт парящих объектов в центре трека.
- Нулевая регрессия: все 44 автомобиля из итерации 001 успешно загружаются (`verify_all_cars.py`: 44/44 passed).
- Тесты: 37 unit tests pass, `cargo clippy -- -D warnings` чист, release native и WASM сборки собраны.

### 001-car-viewer
- [Run010](iterations/001-car-viewer/runs/010-material-depth/README.md): все 44
  модели загрузились, 88 front/rear GPU-снимков осмотрены, без новых явных дефектов.
- Исправлены Base/style/LOD, последовательные pr-каналы, масштаб/tr/Z/winding,
  FSH-атласы, колёса и оформление специальных моделей.
- Перекрытие фар 356b исправлено signed полем материала mt+0x114 -> depth bias.
- Краска использует alpha-маску: лампы/хром сохраняют цвет.

## Приёмка и ограничения

Итерация `009-game-shell` полностью принята (тег `iteration-009`).
Следующий этап — `010-evolution-career`: полный цикл эпохи Classic, турнирное древо `nfs5.trn`, покупка/продажа подержанных авто и рынок запчастей.
См. `docs/next-iteration.md` и полную дорожную карту `docs/roadmap.md`.

## Основание проекта

Rust/wgpu/winit, shared native/WASM Scene, четыре crate в workspace (`nfs-formats`, `nfs-assets`, `nfs-game`, `porsche-viewer`).
local/game: 1742 файла / 599126359 байт, SHA-256 манифест в docs/game-manifest.json.
Среда и версии: docs/environment.md и docs/building.md; формат: docs/crp-format.md.
Git main, локальные снимки iteration-001..iteration-009; remote не настроен.

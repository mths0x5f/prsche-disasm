# План восстановления Porsche Unleashed

Текущий результат — [Run160](iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration/README.md): **386 проверенных C++ функций** и6 зарегистрированных частичных consumers.
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


Активно параллельно:161 smallblock allocator,164 network vtable targets,166 formatter output;162/163 готовы. Root: checkpoint160; далее общая приёмка161/162/163 и native vtable relocations.

## Ближайшая цель: полный игровой EXE из C/C++

Уточнение пользователя2026-10-11: результат этапа — компиляция и полный запуск игры.
Checkpoint156 запушен6fd070a; принят следующий пакет160. Общая библиотека и проверочные программы собираются;
реальный игровой target ещё не линкуется:279 видимых unresolved symbols /312 references. Это текущая
граница восстановленного графа, а не число всех оставшихся функций: новые тела могут
открыть новые зависимости, включая косвенные вызовы и частично восстановленные consumers.

1. После принятой160 интеграции продолжить CRT smallblock heap, locale engines и network dispatch
   и полный004d3420; 004a6a00 восстановлен, но virtual mode всё ещё не ограничен:131 остаётся isolated.
   Formatter fatal/bootstrap и strings приняты143; float helpers147 приняты; lowio005a953e принят156; далее decimal/locale engines.
   Partial00525ec0 требует исходного EAX contract; не подключать guessed return.
2. По actual game-link report восстанавливать целые связанные блоки startup/application,
   render/driver и resource services. После каждого пакета повторять линковку настоящего
   игрового target и учитывать новые зависимости; не закрывать их заглушками.
3. Получить настоящий игровой EXE, выполнить startup с исходными ресурсами, окно/ввод,
   первый кадр, меню и штатный выход. Это промежуточный рубеж, не полный запуск игры.
4. Довести Quick Race, обе карьеры, физику/ИИ/повреждения, прогрессию/экономику,
   сохранения и звук до проверенного исходного поведения. Вернуться ко всем пунктам
   docs/recovery-validation-backlog.md. Только затем — архитектурная схема и Rust.

## Схема устройства игры после восстановления кода

- [ ] После полного разбора и восстановления кода построить и версионировать
  общую архитектурную схему игры в `docs/architecture/`: запуск/завершение,
  главный игровой цикл, модули и граф их связей, потоки/callbacks,
  владельцы данных и жизненный цикл ресурсов.
- [ ] Отдельно раскрыть связи UI/режимов/карьер/сохранений с физикой, ИИ,
  повреждениями, экономикой/гаражом, рендером, вводом и звуком.
- [ ] Подкрепить схемы ссылками на восстановленные C/C++ файлы и исходные
  модуль/SHA/VA. Разделять подтверждённое устройство оригинала, платформенную
  адаптацию и ещё неизвестные связи. Готовность: по схемам можно проследить
  запуск→меню→гонку→результат/сохранение→выход и найти код каждого перехода.

Назначение схемы — последующее переписывание игры на Rust (уточнение пользователя
2026-10-10). Порядок: восстановленный C/C++ baseline → проверка оригинального
поведения → схема архитектуры → Rust native/web. Для Rust дополнительно показать
границы модулей, владение/жизненный цикл данных и обмен между подсистемами,
чтобы перенос сохранял исходную семантику и опирался на понятную структуру.

Активный путь с 2026-10-08 — [v2/001-original-recovery](iterations/v2/001-original-recovery/PLAN.md).
Полный корпус всех бинарников → собираемый original Windows/x86 → современный
порт. Отдельные итерации `iterations/v2/*`, сборки `local/builds/v2/*`.
Текущий результат: 24 PE + 1 NE / 36 587 функций / 2 827 310 инструкций
экспортированы целиком; 3 199 385 исполняемых байтов пока не классифицированы
как инструкции. Все 36 587 функций попытаны декомпилятором: 36 583 псевдо-C,
4 failed/timeout, 5639 функций с предупреждениями. Инвентаризация прошла.
Сразу C/C++ по выбору пользователя; первый игровой запуск допускается позже.
Адресное дерево: 25 модулей / 36 587 функций; native x86 библиотека и отдельные
стенды. Run 002: startup 0x4b6710 сверён на 175 входах. Run 003: ещё 9 C++
функций fe.txt/command-line → FE stream → dispatch сверены на 236 случаях,
включая настоящий fe.txt. Run 004: ещё 11 функций собственного heap на C++;
551 случай совпал по всей арене после каждой операции, 236 FE регрессий прошли.
Run 005: ещё 29 функций файловых запросов/очередей/completion/chunk read;
89 совместных FE/heap/IO сравнений прошли, 551 heap и 236 FE регрессий прошли.
Всего 50 проверенных ручных функций. Три пропущенных callbacks добавлены
в supplementary SHA index: 36 587 automatic + 3 = 36 590 записей каталога.
Внешние CRT/OS/SIMD/disk/thread/callback callees ещё открыты; 0 байтовых
совпадений/целых модулей. Игрового v2 EXE нет. История runs сохранена.
Startup и открытые зависимости — reference/startup.json. Владелец — координатор,
Run011 disk_backend и Run012 fe_callbacks. Allocation wrappers/device init уже сделаны в Run006;
worker/thread/wait/events/disk/archive и startup 0x4b6a50 ещё открыты.
Run 006: ещё 6 page/list/device init функций; 474 x86 сравнения и 89 joint
регрессий прошли. Page wrappers перенесены в общий стенд, OS APIs остаются
границами. Всего 56 проверенных функций; каталог 36 592 (5 supplementary).
Worker 0x568530 проиндексирован (925 bytes), пока не восстановлен.
Следующий конкретный шаг — 0x5688d0 jump table → worker/control/completion,
thread trampoline/start 0x55f4f0/0x55f5f0, wait/events → disk/archive backend.
Отчёт: iterations/v2/001-original-recovery/runs/006-file-device/README.md.

2026-10-08: по запросу пользователя сохраняем 012 как есть и меняем подход.
Run 020: 47 original four-wheel loops / 188 состояний совпали с Rust;
221 tests (3 ignored), fmt/clippy/wasm32/native/web и 3 Quick Race прошли.
Общий browser прогон Run 020 не завершён. Игровой force adapter сохраняется,
012 не закрыта. Дальнейший перенос в 012 остановлен для разработки v2.
Run 019 запушен: 13b70f1.

Run 019, 2026-10-06: исходные EDG подключены к общему дереву игровых опор.
3 mixed trees / 27 EDG queries, 8 body selections, 45 complete responses,
5 height branches / 29 material states совпали с x86. 220 Rust tests, 3 ignored;
fmt/clippy/wasm32, native/web release, 3 Quick Race и 21 browser check прошли.
Original-state body/wheel API отдельно от force adapter; поля/силы/cadence,
special/car-car, UI/миссия/визуальная сверка остаются в 012. Активных исполнителей
нет, владелец остатка — координатор. Следом 0x499bc4..0x499eec: fallback/front
offset и wheel +0x64/+0x6c → forces. Источник/границы/команды:
iterations/012-campaign-fidelity/runs/019-original-contact-runtime.

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

Run 013 внутри 012, 2026-10-05: исходные type-1 опоры/выбор уровня прослежены;
36 полигонов/10 выборов листа/10 quad splits прошли на исходном x86. Предикаты
и выбор листа перенесены в Rust, сверены с оригиналом; проверки прошли.
Источник Base/pr/vt/df найден, таймер128/счётчики64Гц прослежены. Исполнители закончили.
Далее координатор: raw flags/material и spatial leaf query до runtime. Сборка fa56d05.

2026-10-05, Run 012: угловой callback включён в проверку оригинального x86;
468 состояний совпали. Перенесён отдельный Rust-участок подготовленного контакта,
пока вне игрового цикла. Геометрия точек/направление нормали проверены отдельно.
Далее полный контракт выбора контакта и связь исходных полей с состоянием авто.

Run 011, 2026-10-04: по решению пользователя восстанавливаем оригинал во всех
подсистемах, включая старый код. Самостоятельный sweep границ снят с runtime
и сохранён в local/experiments/012-swept-boundaries-20261004. Сборка — fa56d05.
Сначала завершаем 012: исходные consumers физики/контактов, миссии и UI,
сравнение с оригиналом. 2026-10-05: EDG → запрос → реакция 0x494000 прослежены;
64 проверки участка реакции на исходных x86-инструкциях прошли. Следом угловая
реакция и условия принятия контакта; перенос в runtime ещё не выполнен.
013 запланирована под повреждения и рынок б/у, не начата. Правила: AGENTS.md.

2026-10-04, Run 010: пользователь прошёл 0M01 и сообщил цикл «Продолжить».
Подтверждён повторный показ результата при неизменной phase 4/5.
JS исправлен, регрессия воспроизвела ошибку до правки и прошла после.
Исправлена также ссылка 1m01 на отсутствующий boxster.sim → boxster25.
Windows/WASM собраны. Chromium подтвердил Continue, сохранение, реальный старт
1m01 и повтор после fail (финиш — тестовый). Пять Factory Rust-тестов прошли.
Run 010 завершён. Далее: игровая приёмка следующей миссии и дефект границ Quick Race.


Обновлено 2026-10-03. Активна **012-campaign-fidelity** из завершённой 011.
Run 008: подключены геометрия/анимация колёс из CRP, контакт кузова с дорогой
при перевороте и столкновения player/AI/AI. Колея Boxster берётся из модели.
184 Rust-теста прошли; Windows/WASM собраны. Браузер подтвердил wheel pivots,
вращение/руление и контакт в Quick Race; общая регрессия 21/21. Оба повтора 0M01 —
5/6 точек без переворота, но тайм-аут. Изменения сохранены в коммите 9efb71c.
Run 009 по запросу пользователя: общий индекс всех EXE/DLL/ASI/OCX, Ghidra-функции
и ссылки, поиск по строке/адресу, данные в `research/binary-index/` под Git.
До следующих изменений поведения обязательно обращаться к индексу (AGENTS.md).
Покрытие проверено: 25 PE-путей / 24 уникальных бинарника, 36 510 функций;
clcd16.dll (NE) явно вне PE-анализа. Поиск строки/адреса и дизассемблирование работают.
Ближайший шаг после публикации: по индексу восстановить оригинальный путь
миссии/физики и довести 0M01 до результата в исходном лимите.

Приоритет пользователя 2026-09-29: публикуем промежуточный checkpoint сейчас.
[Run 007](iterations/012-campaign-fidelity/runs/007-publish-checkpoint/README.md)
содержит рабочие функции, ограничения и запуск. Далее — один законченный игровой
шаг: 0M01 от старта до корректного результата. Короткий реверс конкретного consumer,
правка, заезд, небольшой коммит; не откладывать публикацию до полного реверса.

Исторический блокер Run 006: восстановить EXE consumers SIM 0x10c/0x110 и источник
геометрии колёс. Их трактовка как колеи заставляет runtime применять 1 м;
оригинальная семантика не установлена. Две ошибки сил/лучей подвески исправлены,
172 Rust-теста passed, Windows/WASM собраны, но attempt-5 всё ещё переворачивается
после 2-й точки. Нет коллизии кузова с землёй. Полное прохождение/UI остаются открыты.

История текущей проверки:

Run 006: исправлена отсутствующая опора площадки Skidpad после MESH04.
169 Rust-тестов passed, Windows/WASM собраны. Повтор проходит 4/6 точек,
без провала; теряет траекторию на развороте и получает тайм-аут. Следующий
шаг — отделить ошибку управления пробой от физики, затем полный result flow.
Оба заезда сохранены в runs/006-mission-playthrough; итерация открыта.
Продолжение: attempt-3 доказал переворот на развороте. Исправлен обратный знак
сил стабилизатора, воспроизведённый отдельным тестом; повторная проверка в работе.
Attempt-4 показал оставшийся переворот. Следующая подтверждённая ошибка —
проекция вместо пересечения луча подвески с покрытием при крене. Реализован
raycast по исходным конечным треугольникам; регрессия и повтор в работе.
Снимки 001–011 заморожены; замечания пользователя исправляются только в 012.

## Цель

Полный перенос на Windows, Linux, macOS и web: Evolution, Factory Driver,
остальные режимы, правила событий, экономика, профили/сохранения, интерфейс и звук.
Крупные этапы: [docs/roadmap.md](docs/roadmap.md).
Просмотрщик и аркадная машина — вспомогательные инструменты.

## Завершено: 011-factory-driver

Рабочий план: [iterations/011-factory-driver/PLAN.md](iterations/011-factory-driver/PLAN.md).
Результаты: [STATUS.md](STATUS.md). Отчёты: [Run 001](iterations/011-factory-driver/runs/001-factory-driver/README.md).

1. **T01 — реверс Factory Driver:** спецификация 34 миссий `nfs5.fac` и языковой базы `festrings.csv`.
2. **T02 — движок испытаний и трюков:** детекторы `StuntDetector` (180° slide, 360° spin, reverse J-turn, слаломные штрафы, контроль повреждений кузова).
3. **T03 — карьерные ранги и наградные авто:** от Applicant до Master Ace Driver, бонусные авто ('78 911 Turbo 3.3, '73 Carrera RS 2.7, '99 911 GT3 Factory Edition).
4. **T04 — веб-интерфейс лестницы миссий:** модальное окно `#factoryMissionsModal`, фильтры Tier 1–3, реплики Рольфа, статусы и лучшие времена.
5. **T05 — устранение дефектов кампаний и аутентичность интерфейса:** аутентичный брифинг, устранение ошибки покупки авто, загрузка настоящих 3D-моделей Porsche в миссиях, исправление трассы Canyon.
6. **T06 — интеграция и приёмка:** 142 теста Rust passed, Clippy/Rustfmt чисты, Playwright E2E 12/12 checks 0 errors, сборка release native и WASM.

## Завершённые снимки

- [001-car-viewer](iterations/001-car-viewer/README.md): модели автомобилей.
- [002-track-viewer](iterations/002-track-viewer/README.md): геометрия трасс.
- [003-track-environment](iterations/003-track-environment/README.md): окружение.
- [004-track-topology](iterations/004-track-topology/README.md): топология, прототип заезда.
- [005-unified-driving](iterations/005-unified-driving/README.md): общий запуск, поверхность.
- [006-game-systems](iterations/006-game-systems/README.md): форматы игровых систем.
- [007-physics-simulation](iterations/007-physics-simulation/README.md): симуляция автомобиля.
- [008-race-loop](iterations/008-race-loop/README.md): цикл гонки и соперники.
- [009-game-shell](iterations/009-game-shell/README.md): оболочка, профили, первые события карьер, звук.
- [010-evolution-career](iterations/010-evolution-career/README.md): режим Evolution, экономика, тюнинг, 15-track аудит.
- [011-factory-driver](iterations/011-factory-driver/README.md): режим Factory Driver (34 миссии, трюки, ранги).

История проверок — в STATUS.md и runs снимков. Позднее найденные дефекты
исправляются в новом снимке, не переписывая историю.

## Сейчас: 012-campaign-fidelity

Приоритет пользователя от 2026-09-25: исправить несоответствие интерфейса и заданий,
неверный старт Factory Driver, подлёты автомобилей и тормоз/задний ход на S.
Рабочий план: [PLAN 012](iterations/012-campaign-fidelity/PLAN.md).
T01 — экраны карьер; T02 — сценарий/старт миссий; T03 — контакты и ввод; T04 — приёмка.
Без Computer Use выполнены SCN-цели 0M01 вместо ложного завершения по кругу,
регрессия контактов/торможения, извлечение UI и сборки Windows/WASM. 151 Rust-тест и
14 браузерных проверок прошли. Визуальная приёмка открыта: камера 0M01 перекрыта геометрией,
UI 1:1 и правила оригинала требуют сверки. Native CLI ещё использует табличную физику.
Checkpoint 2026-09-26: все задачи остаются открытыми и частично выполненными; подробности,
ограничения и точные команды продолжения — в [PLAN 012](iterations/012-campaign-fidelity/PLAN.md)
и [Run 001](iterations/012-campaign-fidelity/runs/001-fidelity-repair/README.md).
Звук/кокпит отложены до этих исправлений: [план](docs/planned-audio-cockpit.md).

Продолжение 2026-09-26: Computer Use проверен, `sky.list_apps()` → `spawn EPERM`.
Run 002: подключены исходные SIM к web runtime, добавлен Quick Race,
исправлены знак поворота AI, lookahead спринта и ложная метрика старого аудита трасс.
157 Rust-тестов passed; Chromium 19 checks passed, 0 JS errors, 1 открытый сбой
смены направления в 0M01. Сценарии, AIS/AI-таблицы и число участников кампании ещё
не восстановлены. Следующий приоритет — доказанное поведение 0M01 и состав заездов
по исходным данным/EXE, а не расширение приближённых сценариев.
Run 003, 2026-09-27: исправлен тормозной импульс колёс (R→вперёд 8/8 повторов),
подключён доказанный масштаб SCN v4. 162 Rust-теста и 20 Chromium checks passed,
0 JS errors/known failures; Windows/WASM собраны. Камеру закрывает L A / ARW1;
EXE доказал отсутствующее переключение стрелок через animdefs.txt/trigger links.
Следующий шаг — первая активация стрелки и подключение этого механизма.
Визуальная приёмка остаётся открытой. См. [Run 003](iterations/012-campaign-fidelity/runs/003-factory-diagnostics/README.md).

## Постоянные правила

Run 004 проверен: animdefs/SCN-linked стрелки подключены, стартовое перекрытие камеры
устранено; 166 Rust-тестов и 21 Chromium check passed. Windows/WASM собраны.
Далее — start-pose consumer и оригинальные условия trigger dispatch, затем полное
прохождение 0M01. Общая цель карьер/UI остаётся открытой; активных назначений нет.
Run 005 (2026-09-28): shape1 predicate внедрён — диагонали корпуса, ограничения
SCN heading/velocity/speed и type-based End. 169 Rust-тестов/21 browser check passed,
Windows/WASM собраны. Далее — exact original bounds/model origin, полный заезд 0M01
и penalty/result flow. Агенты остановлены лимитом, назначения завершены.

- `local/game` только читается; изменяющие оригинал эксперименты — в `local/experiments`.
  Ресурсы не копировать в снимки или Git.
- Новый снимок — через `scripts/new-iteration.py`, без прежних runs и кэшей.
- Перед работой сверять STATUS, активный PLAN и runs с Git и диском.

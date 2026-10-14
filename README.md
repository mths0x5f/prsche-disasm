# Need for Speed: Porsche Unleashed — восстановление оригинала

2026-10-14: compilation-first192/190:1054 разных Porsche.exe VA дали реальные
x86 COFF:924 общего корпуса +130 thiscall leaves, пересечений0. У27 leaf bodies
машинные байты совпадают с оригиналом. Это candidates, не игровой EXE/fidelity acceptance;
production baseline476full+6partial и game-link173267symbols/303refs неизменны.
184:3312TUs reused;2460 changed covered37batchedcl +12pilot/153priorfailures,
syntax733→923, missing-global errors25306→16818,0lost/0ambiguousfallback.
188:733objects reused/190new,3 /MP6 batches43.416с,0codegenerrors;
384undefinednames/747refs автоматического поднабора.187:127COFF/32fail, only__fltused8refs.
186:1258/1301 inferred RET extents match;42mismatch/1noRET, missingcallargs remainopen.
189 завершён:99exact rewrites/39TUs,1920nativechecks;923→924syntaxpass.
192:923COFFreused/1new00553a70,2.732с/0codegenerrors;190130leafCOFF/29failures.
byte-identical reuse и originalABI/data evidence сохраняются. EXE пока нет.

Текущий результат — [Run173](iterations/v2/001-original-recovery/runs/173-float-transport-integration/README.md): **476 проверенных C++ функций** и6 зарегистрированных частичных consumers.
Общая MSVC Win32 сборка:157 projects /292 unique TUs;137 comparison/alias targets,9 native OS и3 link fixtures.
15 свежих original-x86 отчётов /24560 сравнений, включая8791 повтор в production без observers, плюс4 composed cases; все12 native/link проверок прошли.
Приняты46 новых функций: original float output/parse, lower network transport и network constructors.
00580ad0 повторно проверена через canonical io_find; второй алгоритм и двойной учёт устранены.
Game-link:0 compile errors /267 unresolved symbols /303 references /0 other diagnostics; игрового EXE нет.
Это текущая граница зависимостей, а не полный остаток. RTTI owners и полный004d3420 ещё открыты.
Приоритет2026-10-12: полный собираемый C/C++ граф → первый экспериментальный запуск; глубокие проверки пакетами через backlog.
Проверенные функции и механически восстановленные compile candidates учитываются отдельно; заглушек и guessedalgorithms в игре нет.
SHA-аудит батчем/кешем; измеренный inventory9,3→2,4с относится к156, не ко всему восстановлению.
Маршрут: полный проверенный C/C++ baseline → схема устройства игры → Rust native/web.
Полный игровой запуск, live timer/WM_CLOSE и визуальная приёмка остаются открытыми.

**Активная разработка с 2026-10-08: [v2 — восстановление полного оригинала](iterations/v2/001-original-recovery/README.md).**
Сначала полный корпус бинарников и собираемый Windows/x86 original baseline,
после — современный native/web порт. v1 сохранена в `dc6b9d8`; 012 не завершена,
её дальнейшая интеграция остановлена. Каталоги v2 отделены в итерациях и сборках.
v2 восстанавливается сразу на C/C++; первый запуск игры допускается позже.
[Run 002](iterations/v2/001-original-recovery/runs/002-cpp-startup/README.md):
адресный каталог 25 модулей / 36 587 функций и самостоятельная x86 C++ сборка.
Первый startup-переход совпал с x86 на 175 входах.
[Run 003](iterations/v2/001-original-recovery/runs/003-fe-stream/README.md):
ещё 9 C++ функций fe.txt/аргументы → поток команд → применение записей;
236 сравнений с оригинальным x86 прошли, включая настоящий fe.txt.
[Run 004](iterations/v2/001-original-recovery/runs/004-original-heap/README.md):
11 функций собственного heap: создание, выделение, слияние, resize и helpers.
551 сравнение всей арены после каждой операции и 236 FE регрессий прошли.
[Run 005](iterations/v2/001-original-recovery/runs/005-original-files/README.md):
29 новых функций файловой очереди, completion, чтения блоками и списков.
89 совместных FE/heap/IO сравнений с x86 и 551 + 236 регрессий прошли.
Всего 50 проверенных ручных функций. Три пропущенных callbacks добавлены
в SHA-проверяемый индекс. Далее — исходные disk/thread/VirtualAlloc службы;
пока они остаются записывающими границами стенда. Игрового v2 EXE ещё нет.
[Run 006](iterations/v2/001-original-recovery/runs/006-file-device/README.md):
ещё 6 C++ функций page allocation/list construction/device startup;
474 сравнения и 89 совместных регрессий прошли. Всего 56 проверенных функций.
Page wrappers исполняются и в общем FE/heap/IO стенде; граница теперь на
Win32 imports. Worker проиндексирован, его loop/thread/disk ещё открыты.
Ниже — история v1.

[Run 019 внутри 012](iterations/012-campaign-fidelity/runs/019-original-contact-runtime/README.md):
исходные EDG подключены к общему дереву с опорами дороги. 3 дерева / 27 queries,
8 body contacts, 45 responses, 5+29 wheel-state cases сверены с x86. 220 тестов,
native/web, 3 Quick Race и 21 browser check прошли. Запуск:
`local/builds/012-campaign-fidelity/Launch-desktop.cmd`.
Силы подвески/body response пока adapter; исходные API требуют доказанного
состояния автомобиля. Остаток 012 указан в плане; итерация открыта.

[Run 018 внутри 012](iterations/012-campaign-fidelity/runs/018-original-support-runtime/README.md):
восстановленные type-1 опоры уже в заезде: исходный resource loader → дерево →
кэш/плоскость → четыре колеса. Подбор RD* и mt53/54 убран. 15 трасс, 237 395
полигонов; 215 тестов и native/web release прошли. Quick Race на Skidpad/Alps/
Canyon и 21 общий browser check прошли. Запуск новой сборки:
`local/builds/012-campaign-fidelity/Launch-desktop.cmd`.
Это подключение геометрии; оригинальные силы/impact kernel и mixed-object tree
ещё незавершены. 012 открыта.

Современная независимая реализация игрового движка **Need for Speed: Porsche Unleashed** (NFS 5, 2000) на **Rust + wgpu + winit** для Windows, Linux, macOS и браузера (WebAssembly / WebGPU).

Активная итерация: **[v2/001-original-recovery](iterations/v2/001-original-recovery/README.md)**. Предыдущая [012-campaign-fidelity](iterations/012-campaign-fidelity/README.md) сохранена незавершённой. Последний завершённый v1 снимок: [011-factory-driver](iterations/011-factory-driver/README.md), тег `iteration-011`. Снимки 001–011 заморожены; прежние отчёты не подтверждают полного совпадения с оригиналом 1:1.
Полный перенос, включая Evolution, Factory Driver и остальные режимы: [дорожная карта](docs/roadmap.md).
Документация проекта: [План работ](PLAN.md) &bull; [Текущее состояние](STATUS.md) &bull; [Сборка](docs/building.md) &bull; [Форматы топологии](docs/track-topology-formats.md) &bull; [Роли агентов](docs/agents.md).

[Run 017 внутри 012](iterations/012-campaign-fidelity/runs/017-original-support-insertion/README.md):
исходное построение/деление дерева соединено с cached support query. 36 полных
деревьев и 72 запроса совпали с x86; 20 тестов, fmt/clippy/wasm32 прошли.
Следом полный ресурсный loader и state/cadence для подключения первой трассы
в 012. Игровая сборка пока fa56d05; восстановленная связка ещё вне заезда.

[Run 016 внутри 012](iterations/012-campaign-fidelity/runs/016-original-support-assembly/README.md):
Base/pr readers и child constructor дерева перенесены по оригинальным consumers.
317 primitive / 60 Base / 256 child случаев сверены с x86; Rust проверил все
74 300 pr на 15 трассах. 16 тестов, fmt/clippy/wasm32 прошли. Полная сборка опор,
вставка дерева и подключение к заезду ещё открыты; игровая сборка fa56d05.

[Run 015 внутри 012](iterations/012-campaign-fidelity/runs/015-original-support-loader/README.md):
доказан источник флагов опоры mt+0; перенесены material lookup и plane/split
helpers. 208+10 случаев сверены с оригинальным x86, Rust проверил материалы
всех 15 трасс. 11 тестов и native/WASM проверки прошли. Далее полный загрузчик
полигонов и построение дерева; игровой цикл ещё прежний, сборка fa56d05.

[Run 014 внутри 012](iterations/012-campaign-fidelity/runs/014-original-spatial-query/README.md):
исходные spatial bounds, обход дерева и кэш опоры перенесены в Rust;
572 результата совпали с исполнением оригинального x86. Native/WASM проверки
прошли. Загрузка/построение сцены и подключение к заезду ещё открыты;
последняя игровая сборка — fa56d05.

[Run 013 внутри 012](iterations/012-campaign-fidelity/runs/013-original-support-query/README.md):
исходные проверки опорных полигонов и выбор уровня перенесены в Rust и сверены
с исполнением оригинального x86. Прослежены CRP consumer и исходный таймер.
Подключение геометрии сцены к игровому циклу остаётся открытым.

2026-10-05, [Run 012](iterations/012-campaign-fidelity/runs/012-original-contact-kernel/README.md):
в Rust перенесён исходный участок реакции на подготовленный контакт, включая
поворот; 468 состояний совпали с исполнением оригинального x86. Проверки native
и WASM прошли. Подключение к заезду ещё открыто; последняя игровая сборка — fa56d05.

Решение 2026-10-04: **восстанавливаем оригинальные алгоритмы и поведение во всех
подсистемах**, включая пересмотр старого кода. Подбор похожей физики/ИИ/правил
не является переносом. Источники, вычисления и сравнение с оригиналом обязательны;
правило закреплено в AGENTS.md. [Аудит и Run 011](iterations/012-campaign-fidelity/runs/011-original-physics-audit/README.md).
Сначала завершаем 012; [013: повреждения и рынок б/у](docs/planned-damage-used-cars.md)
пока в плане. Последняя игровая сборка — fa56d05; новый sweep в неё не включён.

2026-10-05: прослежена исходная цепочка контакта с EDG и проверен участок реакции
на исходных x86-инструкциях: 64 численных случая прошли.
[Доказательства и ограничения](iterations/012-campaign-fidelity/research/original-collision/response.md).
Перенос полной реакции в игровую сборку ещё впереди.

Обновление 2026-10-04: [Run 010](iterations/012-campaign-fidelity/runs/010-result-continue/README.md)
исправляет цикл кнопки «Продолжить»: результат показывается один раз за попытку,
Factory Driver возвращается к списку миссий. Исправлена ссылка на SIM второй
миссии; браузер подтвердил её старт и сохранение прогресса. Windows/WASM собраны.
Пользователь сообщил о прохождении
0M01; автоматическая проверка полного заезда и сверка с оригиналом остаются открыты.
Чтобы загрузить обновление с текущим профилем, обновите уже открытое окно (Ctrl+F5).

Обновление 2026-10-03: [Run 008](iterations/012-campaign-fidelity/runs/008-wheel-animation/README.md)
добавляет анимацию колёс по геометрии CRP, контакт кузова с трассой при перевороте
и столкновения машин. Windows/WASM собраны; 21 браузерная проверка прошла.
0M01 теперь достигает 5/6 точек без переворота, но полный заезд в лимит ещё не принят.

**Перед реализацией поведения обращаемся к оригиналу:**
[индексы бинарников и команды поиска](research/binary-index/README.md).
Генераторы, сводки и подробные текстовые индексы хранятся в репозитории:
`research/binary-index/`. Найденные адреса и границы доказательств фиксируются
в отчёте правки; правило закреплено в [AGENTS.md](AGENTS.md).

В 012 добавлен **Quick Race**: кнопка в главном меню, выбор трассы и автомобиля,
1/3/5 кругов и 0/3 соперника. Используются доступные оригинальные SIM; карьерный
профиль не меняется. Проверки и ограничения — [Run 002](iterations/012-campaign-fidelity/runs/002-runtime-sim/README.md).
В [Run 005](iterations/012-campaign-fidelity/runs/005-trigger-contract/README.md)
подключена восстановленная проверка триггеров диагоналями корпуса и условиями SCN.
169 Rust-тестов и 21 browser check прошли. Переключение стрелок и свободная стартовая
камера сохранены; полное соответствие сценариев и UI ещё открыто.
В [Run 006](iterations/012-campaign-fidelity/runs/006-mission-playthrough/README.md)
исправлен провал через площадку после первой точки. Повтор достигает 4/6 точек;
полное прохождение пока не подтверждено из-за потери траектории на развороте.
Продолжение Run 006: телеметрия выявила переворот; исправлены две ошибки
подвески, но исходная геометрия колёс в SIM runtime требует реверса.
Исторические 172 Rust-теста Run 006 не подтверждают полное прохождение или физику оригинала.

---

## 🚀 Быстрый запуск

Для активной 012-campaign-fidelity:

```powershell
. .\scripts\tool-env.ps1
.\scripts\build.ps1 -Iteration 012-campaign-fidelity -Config release -Target all
.\scripts\launch-viewer.ps1 -Mode desktop
```


`desktop` открывает общий web/WASM интерфейс в отдельном окне Edge/Chrome.
`-Mode web` открывает его в браузере, `-Mode native` — самостоятельное Rust-окно.
После сборки те же режимы доступны через `local/builds/012-campaign-fidelity/Launch-*.cmd`.
Для desktop/web консоль launcher должна оставаться открытой; Ctrl+C останавливает
его локальный сервер, окно браузера закрывается отдельно. Это переходная оболочка,
не новая реализация движка. Native сохраняет `inspect/view` и без аргументов
открывает каталог (Tab — авто/трассы, PgUp/PgDn — выбор).

Web/desktop: Esc — меню, H — приборы, F — заезд; диагностическая панель открывается
отдельно. В карьере и Quick Race загружаются выбранная модель Porsche и исходный SIM.
Физика пока реконструирована частично. Ниже сохранены команды принятой 004.

Ресурсы оригинальной игры читаются исключительно из локального каталога `local/game` в корне проекта (в Git не добавляются).

### Вариант 1. Веб-версия (Web / WebGPU в браузере)

Веб-версия работает локально через WebAssembly и WebGPU. Ресурсы игры по умолчанию автоматически подгружаются сервером из папки `local/game` в режиме read-only:

1. **Собрать проект** (при необходимости):
   ```powershell
   . .\scripts\tool-env.ps1
   .\scripts\build.ps1 -Iteration 004-track-topology -Config release -Target web
   ```
2. **Запустить локальный веб-сервер**:
   ```powershell
   py -3 scripts/serve-web.py --iteration 004-track-topology --port 8000
   ```
3. **Открыть в браузере**:
   Перейдите по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/) в браузере с поддержкой WebGPU (Google Chrome или Microsoft Edge).
   - Все 15 трасс и 24 автомобиля доступны сразу в выпадающем списке.
   - По умолчанию мгновенно загружается трасса `Skidpad` со спорткаром на стартовой позиции.
   - Нажмите клавишу **`F`** или кнопку **«Заезд (F)»** для включения режима аркадного заезда с гоночным HUD (спидометр, тахометр, передача).
   - Для загрузки внешних файлов используйте кнопки «Папка игры» / «Файлы».

---

### Вариант 2. Десктоп-версия (Desktop / Windows Native)

Нативное окно Windows с аппаратным рендерингом через Vulkan / DirectX:

1. **Собрать нативный исполняемый файл**:
   ```powershell
   . .\scripts\tool-env.ps1
   .\scripts\build.ps1 -Iteration 004-track-topology -Config release -Target native
   ```
2. **Запуск интерактивного просмотра трассы**:
   ```powershell
   # Запуск кругового полигона Skidpad
   .\local\builds\004-track-topology\windows\porsche-viewer.exe view --game-dir .\local\game --track skidpad

   # Запуск любой другой трассы (alps, autobahn, canyon, castle, monaco1...5 и др.)
   .\local\builds\004-track-topology\windows\porsche-viewer.exe view --game-dir .\local\game --track alps
   ```
3. **Запуск просмотра автомобиля**:
   ```powershell
   # Запуск просмотра модели 356a (или 911, 930, 993, 996, boxster и др.)
   .\local\builds\004-track-topology\windows\porsche-viewer.exe view --game-dir .\local\game --car 356a
   ```
4. **Консольная инспекция ресурсов**:
   ```powershell
   .\local\builds\004-track-topology\windows\porsche-viewer.exe inspect --game-dir .\local\game --track skidpad
   ```

---

## 🎮 Управление и горячие клавиши

| Клавиша | Режим заезда на авто (`F`) | Режим свободной камеры / орбиты |
|---|---|---|
| **`F`** | Выход в орбитальную камеру | **Вход в режим заезда на авто** |
| **`W` / `▲`** | Газ (ускорение) | Движение камеры вперёд |
| **`S` / `▼`** | Тормоз / Задний ход | Движение камеры назад |
| **`A` / `D` (или `◄`/`►`)** | Руление влево / вправо | Смещение камеры влево / вправо |
| **`Space`** | **Ручной тормоз с заносом (дрифт)** | — |
| **`C`** | Смена вида: Сзади / Капот / Свободный | Смена цвета кузова (в режиме авто) |
| **`P`** | Смена цвета кузова спорткара | — |
| **`R`** | Сброс машины на дорожное полотно | Сброс камеры к исходной позиции |
| **`T`** | Вкл / выкл 3D линий границ полотна (`.edg`) | Вкл / выкл 3D линий границ |
| **`Shift`** (удержание) | — | Ускорение перемещения камеры (x2.5) |
| **`ЛКМ` + движение мыши** | Вращение камеры вокруг автомобиля | Вращение камеры вокруг центра сцены |
| **`ПКМ` + движение мыши** | Панорамирование | Панорамирование |
| **`Колёсико мыши`** | Дистанция камеры | Приближение / удаление |

---

## 📁 Структура репозитория

```
porsche disasm/
├── docs/                 # Архитектурная документация, окружение и форматы
│   ├── track-topology-formats.md # Спецификация форматов .jnc, .edg, .map
│   ├── crp-format.md     # Спецификация формата архивов моделей и треков CRP
│   ├── building.md       # Подробные инструкции по сборке
│   └── agents.md         # Роли и правила автономной разработки
├── iterations/           # Завершённые и активные снимки разработки (snapshots)
│   ├── 001-car-viewer/   # Итерация 001: просмотрщик моделей CarModel (тег iteration-001)
│   ├── 002-track-viewer/ # Итерация 002: геометрия 15 трасс игры (тег iteration-002)
│   ├── 003-track-environment/ # Итерация 003: пропы .scn и скайбокс неба (тег iteration-003)
│   └── 004-track-topology/    # Итерация 004: топология, границы полотна, заезд на авто (тег iteration-004)
├── scripts/              # Автоматизация и инструменты
│   ├── build.ps1         # Универсальный скрипт сборки Windows native и WASM
│   ├── serve-web.py      # Локальный HTTP-сервер для WebGPU с доступом к local/game
│   ├── tool-env.ps1      # Инициализация окружения Rust и инструментов
│   └── research/         # Утилиты реверса и зонды (.edg, .jnc, .crp, disasm)
└── local/                # Локальные данные вне Git (игнорируются)
    ├── game/             # Оригинальные файлы игры (только чтение!)
    └── builds/           # Скомпилированные бинарники и веб-сайты
```

---

## 🏆 Пройденные вехи проекта

1. **`001-car-viewer`** (сентябрь 2026, тег `iteration-001`):
   - Восстановлены распаковщик CRP, иерархия деталей, геометрия и LOD-уровни.
   - Декодер FSH (BGR, BGRA, 8bpp палитровый) и альфа-маски окраски кузова.
   - Подтверждена корректная загрузка всех **44 моделей CarModel** игры с колесами и фарами.
2. **`002-track-viewer`** (сентябрь 2026, тег `iteration-002`):
   - Декодирование `karT` треков из CRP, триангуляция типов примитивов 1, 3, 4.
   - Поддержка 16-битных текстур FSH `0x7e` (ARGB 1555), батчинг мешей по материалам (-97% буферов).
   - 100% текстурирование и загрузка всех **15 трасс** игры без швов между блоками.
3. **`003-track-environment`** (сентябрь 2026, тег `iteration-003`):
   - Парсинг сценариев расстановки `.scn` и инстанцирование динамических библиотечных объектов (конусы, стрелки, указатели).
   - Рендеринг 360-градусной цилиндрической панорамы горизонта `horz` из `Sky/<track>.fsh`.
4. **`004-track-topology`** (сентябрь 2026, тег `iteration-004`):
   - Реверс и парсеры топологии: развилки `.jnc`, кромки полотна `.edg`, секции `.map`.
   - Рендерер 3D-линий границ дорожного полотна (`TopologyRenderer`) с защитой от z-fighting.
   - Аркадное вождение спорткара Porsche (`ArcadeCar`): динамика, руление с учётом скорости, дрифт, автоматическая КПП, обороты двигателя, привязка к высоте и уклону дороги.
   - Веб-версия с гоночным стеклянным HUD и дефолтной автоподгрузкой ресурсов `local/game`.
5. **`005-unified-driving`** (сентябрь 2026, тег `iteration-005`):
   - Унифицированные desktop/web лаунчеры (`launch-viewer.ps1`, `Launch-*.cmd`).
   - Spatial grid статической дорожной геометрии (`surface.rs`): аудит всех 15 трасс (109 707 полигонов, ошибка < 0.0002 м).
   - Скрываемый интерфейс, плавное руление и стабильная физика прототипа.
6. **`006-game-systems`** (сентябрь 2026, тег `iteration-006`):
   - Доказательная база реверса `nfs5.exe` (SHA-256 `c318af393d4c2b7071a820ca3d69e956bbd94769b6e5c2e3e49f498ecbc94906`).
   - Парсеры `SimCar` (88/88 `.sim`) и `AisCar` (22/22 `.ais`) в `nfs-formats/src/sim.rs`.
   - Архитектура сохранений `.sav`, каталоги `nfs5.car`, `nfs5.trk`, миссии `nfs5.fac` в `nfs-formats/src/career.rs`.
   - Детерминированные реплеи `replay.rpl` (8 суб-сэмплов/тик, RLE-поток) в `nfs-formats/src/replay.rs`.
   - 500-RPM сетка крутящего момента, воспроизводимый baseline стенд в `local/experiments/bench/sim_baseline.json`.


---

## 📚 Справочные открытые проекты (References & Acknowledgements)

В ходе исследования ранних бинарных форматов игры (CRP, FSH) в качестве отправных точек и сверки структур использовались следующие открытые наработки сообщества:

- **[CrpLib](https://auroux.free.fr/)** (Дени Ору / Denis Auroux, 2002):  
  Исторически первая реализация разбора контейнеров `.crp` и текстур для NFS: Porsche Unleashed на языке C. Описала базовые заголовки статей и блоки вершин/нормалей.
- **[OpenNFS / LibOpenNFS](https://github.com/OpenNFS/LibOpenNFS)**:  
  Мульти-движковый проект загрузки ресурсов игр серии NFS (NFS 1–6). Содержит общие описания заголовков FSH-текстур (`FshTypes.h`) и адаптацию оригинальной библиотеки `CrpLib`.
- **[dima424658 / LibOpenNFS](https://github.com/dima424658/LibOpenNFS)** (форк Дмитрия Панкова):  
  **Чем отличается от upstream LibOpenNFS**: в основном репозитории OpenNFS поддержка NFS5 опиралась на устаревший C-код `CrpLib`. В форке `dima424658` была предпринята модернизация парсера NFS5: написаны типизированные C++ структуры (`include/NFS5/CRP/Types.hpp`, `BasicTypes.hpp`, `CRPFile.cpp`), уточнены битовые поля заголовков статей (`HeaderInfo`), смещения и распаковка VIV-архивов. Использовался для верификации выравнивания байт и масок статей.
- **[FSHTool](https://auroux.free.fr/)**:  
  Утилита Дени Ору для анализа формата QFS/RefPack сжатия и блоков изображений FSH.

> **Важно**: Все загрузчики, парсеры и движок в этом проекте написаны **с нуля на чистом safe Rust** без использования C/C++ runtime или чужого кода. Форматы топологии трасс (`.jnc`, `.edg`, `.map`) и сценарии расстановки (`.scn`) отсутствовали в указанных проектах и были реверсированы напрямую из исполняемого файла `nfs5.exe` через Capstone и Ghidra (спецификация: [`docs/track-topology-formats.md`](docs/track-topology-formats.md)).

---

## ⚙ Требования к окружению

- **ОС**: Windows 10/11 x64 (также поддерживаются Linux и macOS).
- **Rust**: версия 1.98.1+ (MSVC toolchain на Windows, target `wasm32-unknown-unknown`).
- **Python**: 3.10+ (для локального веб-сервера и исследовательских скриптов).
- **Графика**:
  - Для Desktop: видеокарта с поддержкой Vulkan 1.2+ или DirectX 12.
  - Для Web: браузер с поддержкой WebGPU (Chrome 113+, Edge 113+).

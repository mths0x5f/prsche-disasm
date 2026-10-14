# v2 / 001 — план восстановления исходного кода

2026-10-14: compilation-first188/190:1053 разных Porsche.exe VA дали реальные
x86 COFF:923 общего корпуса +130 thiscall leaves, пересечений0. У27 leaf bodies
машинные байты совпадают с оригиналом. Это candidates, не игровой EXE/fidelity acceptance;
production baseline476full+6partial и game-link173267symbols/303refs неизменны.
184:3312TUs reused;2460 changed covered37batchedcl +12pilot/153priorfailures,
syntax733→923, missing-global errors25306→16818,0lost/0ambiguousfallback.
188:733objects reused/190new,3 /MP6 batches43.416с,0codegenerrors;
384undefinednames/747refs автоматического поднабора.187:127COFF/32fail, only__fltused8refs.
186:1258/1301 inferred RET extents match;42mismatch/1noRET, missingcallargs remainopen.
190 завершён:127leafCOFF reused/3new,29ошибок остаются. Далее189 exactscalar-slices;
byte-identical reuse и originalABI/data evidence сохраняются. EXE пока нет.

Решение пользователя 2026-10-08: сохранить v1 как есть, получить полный
дизассемблированный/декомпилированный корпус и восстановить собираемый оригинал.
Владелец — координатор. Приоритет: C/C++ startup → линковка → реальный запуск.
Текущий принятый пакет —173:476 full +6 registered partial;173 запушен6952020.
Общая MSVC Win32 сборка:157 projects /292 unique TUs;137 comparison/alias targets,
9 native OS и3 link fixtures. Все12 native/link checks прошли.
15 свежих original-x86 reports /24560 comparisons, включая8791 production repeats,
плюс4 component-proven composed cases. Game-link267 symbols/303refs,0compilererrors/otherdiagnostics; noEXE.
Manual index40 /36627 entries. Приняты46new:167output16,168transport8,170parse10,171constructors12.
00580ad0 сохраняет canonical io_find owner;168 напрямую компилирует/вызывает его какregression.
167 обе сборки4991actualnativeoriginalcases;170 обе3800native+Unicorncases;
полные arena/return/ABI/x87state, observer/production semanticfingerprints равны.
37208output+16216parser intermediateevents; Unicorn1356FPU/390NaNmemory/432NaNstage
расхождений сохранены явно; actualoriginalhardwareauthoritative, flags не маскируются.
168385cases,1712441cases. Constructors включают intermediate/final native vptrs;
RTTI owners/actual provider/worker effects ещё открыты. Raworiginalvtables в productionstoresнеподключены.
11cache/refresh testsPASS; automaticrefresh сохраняет productionfilename/build/trace-offmode,
а ambiguous/missingmode не подменяется instrumentedсборкой. SHA121proofreports/701uniquehashesPASS.

Приоритет2026-10-12: цель первого запуска не должна ждать глубокой приёмки каждой
из тысяч функций. Восстанавливать полный компилируемый граф механически из оригинальных
инструкций/ветвлений и точных ABI; исправлять реальные compiler/link blockers.
Непроверенные compile candidates не считать verified и не выдавать за готовую игру.
Первый запуск candidate — отдельный local/experiments эксперимент с originalcomparison;
никаких guessedimplementations/stubs в production, originalresourcesreadonly.
Семантические проверки сохраняются в backlog и выполняются пакетами; полная fidelity
обязательна для окончательной приёмки. Авторизованный C/C++ путь сохраняется.

Текущие владельцы2026-10-14: pcode_180_resume (gpt-6.1-sol/medium) —189
exact scalar subpiece fields.190 (gpt-6.1-sol/high) завершён:32retried,3new,
127reused,130leafCOFF/29failures. Root —checkpoint190;0c0308b опубликован.
Batchbuilder188 (gpt-6-luna/medium) готов; новые nativeпакеты используют его
с pinned source/header/compiler/options closure и fresh output directories.
184:923syntaxpass (+190),8488missing-global diagnostics устранены;4604native
layouts checked,837conflicts/681invalidnames/2MXCSR identities остаютсяявными.
3312TUs reused +2295batchchecked +153priorfailures +12pilot =5772;37clinvocations,
0ambiguousfallback.188733COFFreused+190new,3/3batchesPASS,43.416с.
186nativeABI /Od,/O2:165calls/403conditions each;12originalCOFF +1tracedcaller.
ThiscallRET census1258match/42mismatch/1noRET; printedreceiver/arg loss blocksblanketrewrite.
187safe159:127COFF/32fail,27bodybytesexactoriginal,3batches39.579с;
noacceptedowners/calleradapters/indirectcalls.188923+190130 disjoint=1053nativeVAs;190127reused+3new,29failures остаются.
Candidates remain isolated; fullgame/noEXE, production173 baseline unchanged.
172/174/175ready176queue;131audio/00525ec0 isolated. Deeporiginalvalidations
batchedthroughbacklog; nofullcorpus/nativeproofrepeats aftereverylocal/doc edit.
New generated reports/header/source outputs write explicitLF BEFORE hashing;
raw frozenGhidra/186/187 report bytes preserved via scopedGitattributes.
Следующий шаг:189 source/helper proof→changedTUbatch;
then188builder expands objectgraph with all newfailures/symbols explicit.
190 retry32 выполнен;29failures сохраняют конкретные diagnostics, не guessedtypes.
Actualsharedglobalstorage/aliases/callerABI/initialization/OS/game loop are open.
После проверенного C/C++ baseline —архитектурная схема и Rust native/web.

## Цель и готовность 001

Все бинарники `local/game` имеют SHA, архитектуру и отдельный каталог корпуса.
Все обнаруженные Ghidra инструкции и функции экспортированы. Каждая функция
проходит попытку декомпиляции с результатом/ошибкой. Непроанализированные
исполняемые байты и неразрешённые связи явно учтены. Результат воспроизводим
из неизменяемых входов. Число восстановленных/совпавших функций не смешивается
с числом автоматически экспортированных функций.

## Дальнейшие этапы v2

1. Полный корпус, данные, зависимости и список пропусков.
2. Определение семейства/версии компилятора, CRT, ключей, layout и ABI;
   первый обычный исходник компилируется с совпадением машинного кода.
3. Восстановление деклараций, глобальных данных, классов/vtables и модулей
   в полном графе программы. Ручной исходник остаётся привязан к SHA/VA.
4. Полная native Windows/x86 сборка с исходными карьерой, физикой, ИИ,
   экономикой, повреждениями, UI и звуком. Сверка функций/данных/модулей,
   реальная езда и прохождение. Неопределённая логика не заменяется заглушкой.
5. После полного разбора/восстановления кода построить общую схему работы
   игры в `docs/architecture/`: startup/shutdown, главный цикл, модули/граф вызовов,
   потоки/callbacks, данные/ресурсы и связи всех игровых подсистем.
   Схемы связываются с C/C++ файлами и original module/SHA/VA; неизвестное отдельно.
   Критерий: прослеживается запуск→меню→гонка→результат/сохранение→выход.
   Подробное задание — раздел общего PLAN «Схема устройства игры после восстановления кода».
6. После проверенного C/C++ baseline и архитектурной схемы переписать игру
   на Rust для native/web (решение пользователя2026-10-10). Схема заранее
   раскрывает границы модулей, владение/жизненный цикл данных и обмен подсистем;
   перенос сохраняет игровую семантику и проверяется на тех же original oracles.

## Подтверждённое

- v1 checkpoint `dc6b9d8`, запушен; 012 не завершена.
- Прежний индекс: 26 путей, 25 уникальных хешей; 24 уникальных PE,
  36 510 функций, 2 825 280 инструкций. Один NE не покрыт PE-анализом.
- Ghidra 12.1.3 содержит NeLoader; его отдельный импорт возможен.
- Porsche.exe SHA ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39,
  PE linker 6.0, Visual C++ runtime строка VA 0x5c1e5c.
- SpaceRangersHD_decomp документирует recovered Delphi + whole-EXE SHA
  verification; это образец методики, не перенос его компилятора в Porsche.

## Гипотезы и неизвестное

MSVC-era происхождение вероятно; точный компилятор, CRT и параметры неизвестны.
Ghidra autoanalysis не гарантирует полноту границ, косвенных целей или типов.
Псевдо-C не собирается автоматически. Издательские модули/патчи/установщики
учитываются полностью, но их необходимость для игрового baseline ещё выясняется.

## Выполнено в Run 002

Run 001: полный корпус 24 PE + 1 NE, 36 587 функций / 2 827 310 инструкций;
36 583 псевдо-C, 4 failed/timeout, 5639 функций с предупреждениями,
3 199 385 unclassified executable bytes. Porsche.exe: 5772/5772 псевдо-C.

Выбор пользователя: сразу C/C++, первый запуск игры может быть позже.
Созданы source/include, source/recovered/<module>, полный адресный каталог
25 модулей / 36 587 функций и отдельная сборка porsche_original.lib/probe.
Переход 0x4b6710..0x4b67a4 восстановлен с четырьмя stdcall аргументами;
175 C++/x86 случаев совпали. Неизвестный 0x4b6a50 — записывающая граница только
в тестовом probe. 1 проверенная ручная функция, 0 байтовых совпадений/модулей.
Startup: четыре стадии, 3093 статически достижимые функции; косвенные
цели и пропуски открыты. Полный отчёт: runs/002-cpp-startup.

## Выполнено в Run 003

Найден реальный fe.txt (13 805 байтов), экспортированы
48 definitions / 144 values / 7 actions (с терминаторами), 53 имени машин,
42 исходных global words. C++ producer/file/arguments/dispatcher включён
в библиотеку; все 236 случаев совпали с оригинальным x86. Сравнены поток,
длины записей, глобальные поля, buffers, callbacks и порядок file/heap вызовов.
Реальный fe.txt даёт 23 записи / 47 слов с терминатором (188 байтов), аргументы
поверх него — 25 записей / 51 слово. Indexed/string/vector/action ветки
проверены отдельными таблицами только в памяти стенда; оригинальные таблицы
в библиотеке не заменялись. Нестандартная обработка # и empty-file ветка
сохранены по инструкциям оригинала.

Запрос индекса: FE_Data_Stream/fe.txt → callers/callees 0x4b6660/0x4b5ee0/
0x4b60d0 → assignment/token/value/action 0x4b5470/0x4b51e0/0x4b5250/0x4b5430
→ dispatch/record length 0x4b4b80/0x4b4cd0. Porsche.exe SHA указан выше.
Типизированные таблицы: 0x5d1e40/0x5d63a0/0x5cc5c8/0x5d61e8.
Свидетельства и команды: runs/003-fe-stream/README.md, verification.json,
tables.json, source-functions.jsonl, source-calls.jsonl.

Итого 10 проверенных ручных функций, 0 байтовых совпадений/целых модулей.
Неизвестные file/heap/callback callees остаются extern в библиотеке. Их
записывающие замены находятся только в fe_stream_probe; оригинальный CRT
compare исполнен в C locale, native стенд проверяет равенство ASCII строк.
Это не восстановление эффектов callbacks, VFS, allocator или смены locale.
Реальный игровой запуск и визуальная приёмка открыты.

## Выполнено в Run 004

Восстановлены 11 функций собственного heap: 0x5697f0 init,
0x531ca0 allocation, 0x531f90 free, 0x569640 resize;
helpers 0x531c60/0x5320b0/0x556620/0x556650/0x56e2c0/0x5323e0/0x5b0000.
Запрос индекса: FE allocation/free/resize → callers/callees → ссылки
таблицы 0x6b4f20 → constructor 0x5697f0 и startup wrapper 0x5aef80.
Исходные VA/ranges/calls, globals и toolchain сохранены в runs/004-original-heap.

Все 551 случай совпали с исходным x86: полная арена после каждого шага,
включая физические headers, свободные списки, payload, suffix/name/guard,
returns и внешние вызовы. Flag 0x10 выбирает верхний конец, 0x20 — самый
большой подходящий блок; граница split строго >0x40. Resize сохраняет pointer,
может ограничить рост доступным соседним пространством; -1 запрашивает максимум.
16-byte header / 64-byte control block подтверждены native/x86 сравнением.
005deb10 исходно равен 1, остальные copy flags равны 0 — проверены по PE данным.

Исправлен ABI free (возврат 1); 236 FE регрессий повторены в новом
runs/004-original-heap/fe-regression, реестр ссылается на новые SHA.
Run 001–003 сохранены как исторические. Итого 21 проверенная ручная функция.
В библиотеке FE allocator/free/resize теперь разрешаются в heap.cpp;
FE regression всё ещё использует свой записывающий heap. Совместное FE/heap/IO
исполнение ещё не проверено. CRT formatting/fill, OS locks, SIMD-copy targets
и allocation-failure callback проверены на записывающих границах, не восстановлены.

## Выполнено в Run 005

29 новых C++ функций файловых requests/queue/status/completion/chunk read
и списков операций сверены с x86 на 89 joint FE/heap/IO случаях.
551 heap и 236 FE регрессий сохранены в новых подпапках Run005.
Проверены byte group, serial wrap, сортировка с равными ключами, поиск/удаление,
EOF/short read/отказ, primary/fallback и настоящий fe.txt (23 записи/188 bytes).
Whole heap/device/operation/list/buffer/name/stream/global state и calls совпали.

3 missed callbacks 0x533cd0/0x567bf0/0x5684c0 добавлены в supplementary
SHA/body index: 36 587 automatic + 3 manual. Всего 50 проверенных ручных
функций, 0 byte matches/модулей. ABI bool open сравнивается по AL, read/close
по EAX. Source/VA/calls/layout/globals/toolchain и границы проверки —
runs/005-original-files/README.md и verification.json.

FE связан с реальными heap и IO frontend в joint probe. Worker выполняет
completion немедленно только в fixture: исходный scheduler ещё не восстановлен.
Disk/archive/VirtualAlloc wrappers, OS/CRT/SIMD и эффекты FE callbacks внешние.
Archive opcodes и fatal/concurrent/locale/runtime-null-name состояния не приняты.
Старые runs 001–004 сохранены; registry указывает актуальные Run005 SHA.

## Выполнено в Run 006

6 новых функций page wrappers/list constructors/default key/device init
сверены на 474 случаях с x86. 89 совместных FE/heap/IO случаев повторены
с настоящими page wrappers; recording allocation теперь на Win32 imports.
Signed page-rounding с LEA/IDIV/IMUL и EAX VirtualFree сохранены.
Всего 56 проверенных функций. Heap/FE standalone отчёты Run005 актуальны
по SHA; старые runs не изменены. Общий отчёт — runs/006-file-device.

Worker 0x568530..0x5688cc (925 bytes) и default key 0x580670..0x580674
добавлены в supplementary SHA/body index. Каталог: 36 587 automatic + 5.
Worker пока unrecovered, вне счётчика 56; OS/thread/event/lock/diagnostic
и raw disk/archive остаются границами. Fixture thread start поставляет лишь
исходную initialized=1 запись; выполнение worker loop и concurrency не принято.

## Выполнено в Run007 — worker и completion

Запрос индекса: `00568530`, таблица `005688d0`, consumers `005806e0/005808f0`.
SHA/11 targets/bytes — runs/007-file-worker/dispatch.json. Координатор владеет
file_worker.cpp, io_worker_lists.cpp, ABI, интеграцией и приёмкой.
worker_probe (worker, gpt-6-sol, medium) — native probe и x86 verifier.
Восстановлены C++ ветви 0..10, отмена, group gate, completion и callback.
69 differential случаев прошли, включая полную арену и промежуточные состояния.
3 новые функции приняты, всего 59. Все шесть MSVC Win32 стендов собираются.
OS/backend/event/lock пока записываемые границы; concurrency не доказана.

## Выполнено в Run008

Operation wait 0x567f70 сверён на 87 unit случаях. Общий files_probe выполняет
настоящие worker/wait/find/status вместо имитации completion; 89 joint случаев
совпали по всей арене и промежуточным event snapshots. Реальный fe.txt даёт
23 записи / 188 байтов (assertion). Всего 60 функций, семь собираемых стендов.
Registry 29 файловых функций переведён на текущий Run008 joint report.
Старые runs сохранены. OS/backend/thread/pump/CRT/SIMD/FE callbacks ещё границы.

## Выполнено в Run009

15 event/sleep wrappers 0x55f740/0x55fb20..0x55fce0 сверены на 249 случаях.
3751 IAT адрес исправлен при сохранении 4217 path/dll/symbol/order записей.
Исходные u32/HANDLE return signatures восстановлены, recording probes исправлены.
Device/worker/wait/joint регрессии 474/69/87/89 прошли; registry указывает новые
Run009 reports. Реальный fe.txt 23 records/188 bytes. Всего 75 функций и восемь
стендов. Сравнение событий пока unit; в joint event wrappers ещё границы.
Назначения worker_probe/import_index завершены, незавершённых поручений нет.

## Выполнено в Run010

10 thread функций и 94 full-state сравнения с original x86 приняты.
Event wrappers в joint FE/heap/IO выполняются в C++; 89 случаев прошли.
Всего 85 verified функций, девять стендов; supplementary trampoline делает
каталог 36593 записи. Старые reports не менялись. Run010 README и reports
сохраняют SHA, адреса, наблюдаемые возвраты и ограничения handshake/concurrency.

## Текущий шаг и передача

Координатор — интеграция и приёмка; worker_probe и import_index завершили Run010.
По запросу пользователя разбор параллелен. disk_backend (formats, фиксированный
сильный профиль) владеет только file_disk.hpp/cpp, disk_probe, verifier и Run011:
0x591ce0/0x591df0/0x592140/0x592290; open 0x5919a0 при подтверждённой семантике.
fe_callbacks (worker, gpt-6-sol medium) — только новые callback header/source/probe,
verifier и Run012: 0x4119e0/0x411a80/0x411b40. Оба восстановлены после quota;
их незавершённые файлы исключены из принятого Run010 checkpoint.
Ближайший шаг координатора: commit/push Run010, подключить отдельные targets,
исправить общий FE callback return ABI и повторить затронутые FE/joint proofs.
После disk/callback acceptance — thread shutdown 0x55f1c0/exit registration,
совместное выполнение thread consumers, archive и startup 0x4b6a50.
Unknown callees — явные записывающие границы; OS concurrency и игровой запуск
не приняты. Timer rate writer 0x5deb48 и compiler/CRT/flags остаются открытыми.

Текущие команды:

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
    py -3 scripts/research/verify-v2-file-threads.py
    py -3 scripts/research/verify-v2-file-events.py
    py -3 scripts/research/verify-v2-file-device.py
    py -3 scripts/research/verify-v2-file-worker.py
    py -3 scripts/research/verify-v2-file-wait.py
    py -3 scripts/research/verify-v2-files.py
    py -3 scripts/research/test_index_binaries.py
    py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
    py -3 scripts/research/structure-v2.py
    py -3 scripts/research/trace-v2-startup.py
    py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification

История runs не меняется. Heap/FE standalone SHA proofs Run005 актуальны.
CRT/main-loop/render/audio/input, compiler/flags, четыре decompile errors и
unclassified bytes открыты. MSVC 19.44.35229 — измеренный современный инструмент,
не доказанный оригинальный compiler. local/game только читается.
Игровой EXE и visual acceptance отсутствуют; итерация не закрыта.

2026-10-09: Run010 checkpoint 6839d44 запушен. Оба агента возобновлены после quota;
11 targets подключены. FE callback ABI исправлен на u32 EAX=0 по Run012;
затронутые proofs повторяются в свежих Run012 regression folders.

Run013: fe_callbacks (worker, gpt-6-sol medium) — новые input_state header/source/probe,
verifier и run; 532e10/56fce0/56fd00/56fd30, controlled DirectInput vtables.
Run014: heap_locks (worker, gpt-6-sol medium) — новые lock header/source/probe,
verifier и run; 5321f0/532250/5322b0/5322c0/5322d0, exact pool и Win32 calls.
Координатор владеет общими файлами, checkpoints и следующим joint disk binding.

## Выполнено в Run011/012 — 2026-10-09

4 disk consumers сверены на31 случаях, 3 FE callbacks на1320.
Ближайшие consumers подтверждены индексом; Button4119e0 вручную дополнен
по body SHA/97bytes/двум RET, каталог36594 (7 supplementary).
FE callback u32 ABI изменён в header/table/exporter/probes. Все затронутые
proofs повторены в новых Run012 regression folders; registry обновлён.
Всего92 verified функций,11 собираемых стендов. OS I/O/concurrency/getstate
пока явные boundaries. Игрового EXE и visual acceptance нет.
Диск-backend Run011 принят; следующий disk_backend Run016 — только новые
physical-open файлы и x86 fixtures. Run013 input и Run014 locks активны.
Координатор: checkpoint Run011/012, build новых targets, joint disk/callback
binding в Run015. Незавершённые agent sources исключены из corpus manifest.

## Принято Run013/014/015

100 полностью verified C++ functions и1 частичная532e10. 1026 input/31locks/
89 joint disk/1320 callback cases прошли; 14 MSVC targets собраны.
Run017 input modes и Run018 lock bootstrap evidence приняты, не исполняемые proofs.
Назначения после возобновления: input_check (worker,gpt-6-sol medium) — Run019
только новые input_buffer files/verifier/run, consumers56fdb0/56fff0.
heap_locks (worker,gpt-6-sol medium) — Run020 новые bootstrap_probe/verifier/run,
совместный55f320→lockpool/pages/Win32. fe_callbacks (worker,gpt-6-sol medium)
переназначен на Run016 новые disk_open files/verifier/run вместо отсутствующего
disk_backend. Прежний input_state принадлежит принятому Run013; больше не менять
до нового назначенного переноса. Координатор: интеграция, builds и checkpoints.
Ближайший шаг: commit/push100, затем targets готовых016/019/020, x86 proofs,
thread shutdown/exit и startup4b6a50. No gameplay approximations; original only.

## Run016/019/020 и приоритет первого запуска

103 full functions,2 partial. Physicalopen1672/inputproperty37/jointbootstrap27
native-original comparisons прошли. 17 Win32 targets собираются. Joint graph
55f320→55f3b0→5321f0/532250→56e5f0 использует настоящий source, подтверждает
BSS flag order и прекращение вложенной init; OS contention ещё не принято.
Fresh Run020 input1026/callback1320 reports записаны с текущими build SHA.
По запросу ускорения выбираем следующий код по startup path4b6a50, а не счётчику
мелких functions. Всего3 worker slots + координатор, общие buildsпоследовательны.
Актуальные назначения (worker,gpt-6-sol medium): heap_locks→Run022 только новые
startup_services2consumers4a5410/4a5c30; input_check→Run023 новые resource_paths
59d650; fe_callbacks→Run024 новые render_startup467470. C++ consumers сверяются
по original asm; их неизвестные callees остаются типизированными границами.
Run016/019/020 приняты, прежние assignments выполнены. Root: checkpoint103,
затем Win32 bindings/shared startup state и общий startup consumer4b6a50.
Первый игровой window/menu требует реальных constructor/renderer/FE bindings;
принятые probes не объявляются игровым запуском. Startup fields/aliases должны
совпадать с исходными consumers, не создавать независимые дубликаты globals.

## Run030 — интеграция startup пакета, 2026-10-09

Приняты Run022–027: 12 новых полных функций и один display prefix; всего115 full,
3 partial. Запросы индекса, SHA/адреса и boundaries — в README каждого run.
23 MSVC Win32 probes собраны общей командой; новые fixtures сверены с x86.
Fresh input/callback/diskopen/inputbuffer регрессии находятся в Run030.
Прежние assignments Run020/013/014 — история, не активные назначения.

Владельцы: startup_heap — allocator Run031 и heap init Run033;
display_ctor — THRASH Run028 и display constructor Run032;
window_runtime — Run029 RegisterClass53ac20/конфигурация/caller53b8d0.
Координатор — общая линковка/Win32 bindings, обновление registry и checkpoint.

Проверки: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1`
и `py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification`.
Все proof commands/fresh directories — Run030/README. Дальше интеграция028/029/031
и настоящий startup/window путь. Unit CreateWindow fixture ещё не реальное окно.

## Run036 — нативный оконный стенд, 2026-10-09

Run030 checkpoint1e8d25c запушен. Приняты028/029/031/033/034: всего129 full,
3 partial. Supplementary index9 функций; новые53a7f0/53aba0 привязаны к SHA/RET.
Общая сборка28 comparison probes + native_window_smoke проходит. Fresh input,
callback,diskopen,inputbuffer,paths,renderer reports — под036; история не изменена.
Фактический запуск Win32 EXE: HWND/client640×480, зарегистрирован recovered WndProc,
39 default messages, корректное уничтожение,exit0. Точные входы/ограничения и хеши —
036/native-window-result.json. Это platform fixture, не original game acceptance.

После лимита прежних агентов назначены gpt-6-luna/high workers:
window_worker_recovery — shared-state correction035, затем handler table038;
display_recovery — полный constructor4677e0, mutable032;
heap_init_recovery — joint real application allocator/heap040 (037 evidence ready,
пока не принят). Координатор — common linking, actual Win32 bindings, главный startup.
Архитектурный остаток: единый storage/aliases original window configuration; source
units с одинаковыми VA не должны иметь независимые копии globals. Неизвестные calls
не связываются silent no-op. Прежде полного EXE восстановить4b6a50 и нужные callees.

Проверки: scripts/build-v2.ps1; inventory-v2.py с require-listing,
require-decompile-attempts,write-verification; proof commands028/029/031/033/034;
036native_window_smoke реально выполнен отдельно. Следующий checkpoint — принятые
035/032/038/040 и расширенная исходная startup chain, без заявлений о готовой игре.

## Run041 — общая startup-сборка, 2026-10-09

Приняты032/035/037/038/039/040/042/043/044. 150 full,4 partial; 20 supplementary
bodies и36607 indexed функций. Запросы индекса/SHA/VA/layout — README пакетов;
принятый отчёт/ограничения/точные команды — runs/041-startup-chain/README.md.
37 probes + native_window_smoke собираются. 4848 comparisons, 6 alias assertions,
actual HWND640x480/recovered WndProc/39messages/clean close прошли. Run037 частичный,
original qsort005a112b остаётся typed boundary, не std::sort. История runs сохранена.

Следующий конкретный шаг: checkpoint041; принять045 messages,046 DirectInput setup,
047 FE startup; завершить048 window positioning,049 render activation,050 instance.
Дальше связать оригинальные callback VAs с native C++ pointers и OS/CRT adapters,
восстановить оставшийся main004b6a50 и проверить настоящую startup chain. Отсутствие
silent no-op обязательно; доказательства fixture не заменяют game/visual acceptance.

## Следующая интеграция после b16d4f0

Run041 принят и запушен как b16d4f0. Новые изолированные пакеты045–054/056 готовы,
но ещё не входят в common CMake/registry. Root готовит061-startup-platform-integration.
Run055: отдельная библиотека source/platform/win32_core.cpp и реальный OS smoke;
Run057: реальные original thread init/start/trampoline/unregister/shutdown на Windows,
оба no-arg/worker-arg пути прошли. Native результаты/хеши сохранены в055/057/native-result.json.
Остаются два явных CRT fixture boundaries (fill и exit-registration), game не запускался.

На приёмке исправлен053: callback loop обязан перезагружать base006c1534 после callback,
а не кешировать; unsigned32 arithmetic избегает C++ pointer-before-begin UB. Новый
mutating-callback case прошёл; теперь8 случаев. В048 исправлена ошибка чтения стека:
учёт двух PUSH показал инициализированный RECT;66 случаев включают live ESP assertions.
045 mouse route5728b0 и056 renderer route обращаются к одному consumer;060 добавляет
единый implementation/adapters. 046557380 уже восстановлен037,050557370 инлайнен,
047 main fragment не standalone function: не считать их новыми целыми функциями.

Следующий шаг root: ревью готовых пакетов и canonical aliases; новые common targets,
пересборка, fresh061 differential reports и6 CMake-dependent regressions; supplementary
index недостающих callback bodies; обновление registry/plans и промежуточный commit/push.
058 main оставляет очистку6573e8/3e24 явной boundary до общего FE storage: запрещён
memset по адресу одиночного global. 059 закрывает оставшиеся callbacks перед реальным
window_init. Ни byte-match, ни целый game executable пока не приняты.

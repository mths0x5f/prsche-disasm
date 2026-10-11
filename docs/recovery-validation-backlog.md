# Отложенные проверки восстановления v2

Прямое требование пользователя 2026-10-10: возвращаться к пропущенным проверкам.
Координатор обновляет этот список при каждом checkpoint и проверяет его
перед архитектурной приёмкой/переносом на Rust; пункт закрывается только
со ссылкой на фактически выполненную проверку. Сборка, bounded differential oracle
и визуальное соответствие — отдельные результаты.

- [ ] Собрать игровой EXE и выполнить исходный startup с настоящими ресурсами.
  Блокер: Run165 game-link имеет273 unresolved symbols /308 references;
  compiler errors и other linker errors —0. Возврат: после устранения
  зависимостей; сначала запуск/выход, затем кадр, ввод, меню и режимы игры.
- [ ] Проверить закрытие через WM_CLOSE→GetMessage=0→исходный timer callback,
  включая producer времени006b7c40. Run086/098 проверяет другую исходную ветку
  cleanup message0x466→destroy→join. Возврат: после подключения исходного diagnostic callback/init и live timer-thread fixture. Run110 нашёл пропущенный
  worker00565270..533e (207B), исходный setup565030 передаёт его в55f420.
  Run112 worker восстановлен и интегрирован111 (6/6 oracle cases); setup/
  thread/timer packet118 интегрирован121: 9 cases, persistent28-byte ThreadRecord,
  live event/id loop retests. OS shutdown bindings125 проверены6 дочерними процессами.
  123 lifecycle(21 cases),127 wait(16) и130 stop→wait integration(3) приняты126.
  Живое расписание таймера и end-to-end WM_CLOSE ещё не выполнены.
- [ ] Проверить полный startup context004d1a90→004d3420→004d1ba0 внутри app_main.
  Review128/129: оригинал резервирует0x188 stack bytes, объект0x180 bytes передаётся
  в ECX; старый caller описывал лишь два DWORD и fixture скрывал это расхождение.
  Run129 исправляет caller/storage/ABI;4 span cases и15 main cases с реальными
  ctor/dtor прошли изолированно. Общая приёмка126 прошла: [15 composed main cases](../iterations/v2/001-original-recovery/runs/126-event-integration/application-main/verification.json) с реальными ctor/dtor.
  Возврат: после полного parser/context graph и live startup;
  полный004d3420 (8589B), vtable и его реальные зависимости остаются открытыми.
  Также открыть единственный owner/extent строки005e8e50: Run081 нашёл две
  раздельные модели пустой строки;129 использует существующий owner без новой догадки о размере.
- [ ] Проверить реальные DirectInput devices и caps/read paths со связанной
  оконной цепочкой. Run096 проверяет consumer0055feb0 с контролируемыми границами;
  native lifecycle fixture не подключает весь input graph. Возврат: после bindings.
- [ ] Выполнить THRASH driver dispatch, fullscreen transitions и настоящий кадр.
  stdcall declarations и успешные oracle checks не доказывают реальный драйвер.
  Возврат: после восстановления driver/service/vtable зависимостей game-link.
- [ ] Воспроизвести MAD stream/playback/audio/render loop целиком. Run094
  восстанавливает только header consumer; не использовать его как полную004dc850.
  Возврат: после восстановления stream/decoder/audio consumers.
- [ ] Сравнить producers путей0065b32c/334/360 и movie service0069ed0c с оригиналом.
  Текущие единые BSS owners не доказывают исходную инициализацию/валидные assets.
  Возврат: при восстановлении соответствующих startup producers. Run116
  нашёл startup_subsystem004b6ff0: install.txt→60pointer table65b2a0..65b38f.
  Run117: 9 component oracle cases и 7 composed checks подтвердили49 записей
  настоящего install.txt и пять shared table views. Реальный startup с assets
  ещё не выполнен; movie service0069ed0c остаётся открытым.
- [ ] Проверить длинные пути и исходные границы stack buffers у00427a60/0059dd00.
  Run103 oracle ограничен префиксами, помещающимися в100-byte local buffer;
  исходный overflow за пределами этих случаев не проверен. Возврат: вместе
  с path producers и контролируемым isolated original-x86 experiment.
- [ ] Подтвердить compiler/CRT/flags и байтовое совпадение там, где оно требуется.
  Run100 no-op семантически совпадает, но MSVC RET0 отличается от original RET.
  Ноль binary matches не скрывается за количеством recovered functions.
- [ ] Полная визуальная и игровая приёмка: оригинальные кадры/переходы,
  Quick Race, обе карьеры, физика/повреждения/ИИ/экономика/сохранения/звук.
  Возврат: после рабочего original baseline; текущие probes этого не доказывают.

- [ ] Завершить полный original formatter: float/wide/locale paths, runtime callback
  initialization, file-write/auxiliary/descriptor-preparation effects и lowio startup.
  Run136 соединяет production108 wrapper→124 parser→119 helpers→132 cleanup;
  canonical descriptor имеет32 bytes, wrapper пишет только исходный16-byte prefix.
  Непроинициализированный opaque tail не обнуляется; seeded test adapter отдельно.
  Run124:62 cases после lead-byte table, zero hexadecimal prefix и wide padding fixes.
  Run132:23 cases, flags перечитываются после callback, tail не декодируется до early exit.
  Run134:12 connected cases с actual wrapper и actual137 unsigned divide/remainder;
  Run137:72 runtime cases. Эти bounded проверки не доказывают live CRT/locale.
  Run138 принят в production archive:8 initial-image ranges /5057 bytes, PE relocations и pointer identities;
  callbacks не исполнялись, функций не добавлено. Это не runtime initialization.
  Возврат:005abee8→005a2e22 fatal path,005a0f5d callback writer и его float consumers,
  lowio initializer005a953e и реальные backend consumers.
- [ ] Восстановить полный EAX contract base destructor00525ec0.
  Run135: null-allocation branch сохраняет входной EAX в original x86, typed C++
  возвращает0; два разных seeds документируют расхождение. Partial destructor
  изолирован, в production library/реестр не подключён. Шесть full функций имеют
  отдельный scoped proof на16 cases, весь isolated packet —20 bounded contracts.
  Возврат: доказать caller-visible return/ABI всех веток и повторить composed
  ctor→context→dtor со связанными dependencies; vtable004d3420 остаётся открытой.
- [ ] Доказать signed mode domain audio initializer004a66b0 и полный consumer graph.
  Run131:8 isolated cases; signed timer half исправлен (−2→−1), query00565680
  заполняет все124 bytes. Index−9 ещё в pinned span,−10 выходит за него;
  original guard отсутствует. Не подменять чтение guessed clamp/throw.
  Возврат: проследить реальные producers mode и таблицы, проверить отрицательные
  значения с original x86 и затем общий startup/device graph. Пакет изолирован.

Владелец всех открытых пунктов — координатор. Состояние на checkpoint136:
ни один end-to-end пункт выше не объявлен выполненным. Run133 device имеет10
bounded cases после overlap/authoritative pointer-cell fixes; это не проверка
настоящего audio device. Активных назначений исполнителей нет.

Checkpoint143:28 новых полных функций приняты с исходными ABI/state/effect checks.
139 pooled memory callbacks,140 CRT bootstrap/fatal,141 application bridges,
142 audio lifecycle,144 strings/dialog,145 network lifecycle включены в общую библиотеку.
CRT error path:94 connected cases с реальными string/dialog bodies;17 свежих
original-x86 reports/7928 comparisons и4 composed cases не закрывают live startup.
Новые Win32 imports compiled и сверены с IAT, но отдельного live dialog/error OS
fixture ещё нет. Возврат: проверить реальные module-name/stdhandle/WriteFile и
lazy user32 resolution без terminal fatal до полноценного game startup.
142 устраняет duplicate656868/9 storage через aliases. Audio virtual mode
не ограничен исходным consumer004a6a00: signed-domain blocker131 остаётся.
145 storage trace подтверждает count/table005e8bfc/005e8c00, но максимальный
extent и canonical owner не доказаны; source таблица остаётся unresolved.
Готовые147/148/149 требуют общей приёмки; x87 Unicorn flags не считать аппаратной
истиной:147 содержит отдельный actual-original hardware oracle, принятие впереди.

Checkpoint153:35 новых full bodies приняты147..151.18 fresh original-x86 reports/
5816 comparisons (включая256 actual-original CPU x87 cases),4 composed cases и
8 native/link checks прошли. Native CRT error bindings проверены real OS fixture:
module path/truncation, stdhandles, WriteFile roundtrip/invalid handle и user32
symbol lookup. Live MessageBox, terminal fatal и полный CRT startup остаются открыты.
147 сохраняет128 Unicorn flag discrepancies; аппаратные FPU flags сверены с
реальными исходными24 байтами (единственный zero operand relocation проверен).
149 native walker read trace проверен private PAGE_GUARD/VEH observer; production
body без инструментации.150 context copy ещё использует typed005a1a40 boundary.
151 original vtable identities005b4968/70 ещё требуют canonical native relocation
и consumers; raw literal identity в oracle не доказывает native virtual dispatch.
152 lowio,154 context move,155 network sessions находятся в параллельной работе.

Checkpoint156:152/154/155 приняты,13 full bodies/4394 newcases.12 fresh reports/
8546 comparisons,4 composed и9 native/link checks прошли.154 exactmemorycopy
сравнивает130440 ordered accesses, включая overlap/selfcopy/alignment/DF.
152 Win32 bindings подтверждены IAT и real OS fixture, включая recursive lock /
cross-thread contention; это не full CRT inherited-handle/live concurrency acceptance.
155 teardown связывает реальные callees139/145/148/151; vtable5b4978 добавлен к
explicit native-relocation backlog вместе с5b4968/70.157/158/159 выполняются параллельно.
Batch SHA оптимизация не меняет критерии поведения:3 mutation/cache safety tests
прошли, benchmark9.2897→2.3805с/counts_equal=true. Перед checkpoint запускать
scripts/research/audit-v2-proofs.py с новым --report; исходники каждого уникального
файла хешируются один раз, изменения во время аудита отклоняются.

## Checkpoint160: CRT/text/network integration

- [x] Принять157/158/159:43 full bodies/10339 packet comparisons; общий build144 projects/270 TUs,
 12 fresh original reports/14491 comparisons +4 component-proven composed cases,
 10 native/link fixtures. Источники и границы —runs/160-crt-text-workers-integration.
- [x] Исправить canonical CRT lock-table prefix до26 DWORD: lock19 у text consumer,
 lock25 у locale setter;104 исходных байта/SHA, initial aliases, lazy/existing/unlock19/25 проверены.
- [x] Проверить10 новых Win32 IAT адаптеров: heap zero-fill/free, TLS/thread IDs/last error,
 thread isolation, Interlocked wrap и concurrent increments.
- [ ] Соединить новые CRT wrappers с настоящим smallblock allocator и original locale engines;
 live allocator/TLS startup/init/failure/concurrency проверить после161/162. Recording seams
 в original oracle не доказывают эти OS/game paths. Signal table005e5ec8 остаётся unresolved.
- [ ] Заменить raw original network vtable identity словами с canonical native relocations.
 163 доказал slot0/RTTI/HIGHLOW и пропуски index48ad70/48b340/5a1056;164 восстанавливает targets.
 Production native virtual dispatch ещё не принят.5e8e50 и5e8bfc/5e8c00 extent/owners открыты.
- [ ] Вернуться к полному004d3420 и запуску игры.279 unresolved symbols — текущая
 граница, не число всего остатка. Batch SHA/cache сокращает повторную работу, не заменяет original проверки.

## Checkpoint165: small heap, locale and groups

- [x] Принять161/162/163:25 full bodies/3909 packet cases;148projects/278TUs,
 13 fresh original reports/8082 comparisons +4 composedcases;11 native/linkfixtures PASS.
 161pins15207intermediate/14936preboundary snapshots иcopyalias835B/46HIGHLOW.
 162pins34 actualprotectedexceptions,originalscopes/handlerbytes/nativeFS restoration.
- [x] Проверить15 platform adapters с real Win32 heap/VM lifecycle,
 LCMapString/characterconversion/classification/CPInfo.Это OS smoke, не complete game parity.
- [x] Batch original SHA в manualindex:37functions→1binaryread/hash, concurrentchanges
 отклоняются;9cache/refresh/manualindex tests PASS. Historical reports unchanged.
- [ ] Live original smallblock allocator/TLS/locale initialization/concurrency/stackoverflow
 с настоящими ресурсами остаются открытыми. Native VM fixture не доказывает весьallocator.
- [ ] Принять164vtabletargets/166output; indexgap48ad70/48b340/5a1056 дополнитьпоSHA.
 Raw constructorvptr и identitycomparisons заменить вместе canonicalnativeowners;
 RTTI и sharedemptystring extent требуют originalconsumers, fixturedata не переноситьвgame.
- [ ] Полный игровой EXE:273unresolved/308refs;compile/otherdiagnostics0.
 Послеclosingfrontier вернутьсякstartup004d3420,режимам/карьерам/live/visual acceptance.

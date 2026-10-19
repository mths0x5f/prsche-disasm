# Разбор PR #2–#19, 2026-10-19

База проверки: `main` **16638e4**, Run309: 158 C++ TUs,
264 unresolved names / 300 references; рабочего EXE пока нет.
Проверены 18 открытых PR из `xfynx/prsche-disasm`, refs `origin/pr/2`–`origin/pr/19`.
На момент исходного review ничего не было слито; комментарии и reviews на GitHub
не отправлялись.

После разрешения пользователя: PR#3 слит42813f7 как отдельный Run400 packet.
Все21 TU скомпилированы;00412030/00425780 прошли свежие native comparisons.
Из PR#4 выборочно перенесены004a54b0/004a54e0 с canonical providers (Run311).
Четыре тела подключены в [Run310](../../iterations/v2/001-original-recovery/runs/310-pr-intake-integration/README.md):
10 native cases PASS,161 game TUs compiled,268 names/304 refs, EXE нет.
Whole PR#4 не слит: дополнительная проверка выявила cached-count ошибку401:44/46
против original00413f29, а402 повторяет compiled owner290 для00471b60.
Остальные решения исходного review ниже сохраняются; PR#4 применён частично.

## Решение

Переносить выборочно, начиная с новых функций **#3 и #4**. Это кандидаты,
а не принятые функции: сначала canonical ownership/ABI, затем воспроизводимые
native comparisons и свежая интеграция поверх Run309. Изолированный PASS со
заглушками вызываемых функций не доказывает корректность реальных связей игры.

**#19 целиком не принимать.** Он действительно содержит те же Git blobs всех
изменённых файлов #2–#18, но наследует их дефекты. Дополнительно содержит
Runs418–420, хотя заголовок PR заканчивается на417. Его база416ad07 предшествует
нашим shutdown-пакетам305/307 и их интеграциям306/309.

## Применимость каждого PR

- [#2](https://github.com/xfynx/prsche-disasm/pull/2), `ff179fa5dd4e`:
  исследовательская заготовка backend/census; не готовый полный x86/x87 backend.
  SIMD и проверка результатов x87 требуют исправления, подробности ниже.
- [#3](https://github.com/xfynx/prsche-disasm/pull/3), `29ff619d0668`, Run400:
  приоритетный источник 21 нового candidate VA. Шесть определённых символов
  совпадают с текущими unresolved: **00412030, 00425780, 004acb80, 00414eb0,
  00467740, 00563d30**. Production providers глобальных данных и callees в
  изолированном стенде отсутствуют; сначала проверка этих границ.
- [#4](https://github.com/xfynx/prsche-disasm/pull/4), `7f4ba1ccc597`, Runs401/402:
  следующий приоритет. Совпадают **00413ea0, 004a54b0, 004a54e0**. Последние две
  функции требуют реальных shutdown/context providers; зависимость0059eb20
  остаётся под HOLD Run303. Девять совпадающих символов #3/#4 не означают
  уменьшение общего frontier ровно на девять: появятся зависимости их тел.
- [#5](https://github.com/xfynx/prsche-disasm/pull/5), `61762e39fafd`, Run403:
  не переносить повторно:00425780/004acb80 уже есть в400, остальные два VA
  имеют canonical owners в main.
- [#6](https://github.com/xfynx/prsche-disasm/pull/6), `cd6874ab6045`, Run404:
  пять из шести VA уже имеют owners. Новый005a177b полезен для исследования
  logging ABI; его символ не совпадает с текущими wrappers. Проверять varargs
  и существующих callers, не добавлять ещё одного владельца.
- [#7](https://github.com/xfynx/prsche-disasm/pull/7), `a349d056a0dc`, Run405:
  три из четырёх VA уже приняты.0053c290 — полезный algorithm candidate для
  `heap_fill_0053c290`; нужны canonical binding и проверка контракта.
- [#8](https://github.com/xfynx/prsche-disasm/pull/8), `bb038e244520`, Run406:
  все четыре VA уже имеют owners; годится как независимая сверка.
- [#9](https://github.com/xfynx/prsche-disasm/pull/9), `223580ab7ee9`, Run407:
  три из четырёх VA уже приняты.0059d8e0 полезен для двух resource-loader
  wrappers, но текущие linker names не закрывает без проверенного binding.
- [#10](https://github.com/xfynx/prsche-disasm/pull/10), `4e51b931324f`, Run408:
  четыре из пяти VA уже имеют owners, включая heap free00531f90.
  Новый004b68f0 полезен, но C symbol не равен ожидаемому C++ symbol.
  Сохранить canonical heap free; отдельно восстановить реальные pipe callees.
- [#11](https://github.com/xfynx/prsche-disasm/pull/11), `2c402e0deb06`, Run409:
  два из четырёх VA уже имеют owners.004a88a0/004640b0 — кандидаты;
  нужны ABI bindings вместо замены существующих владельцев.
- [#12](https://github.com/xfynx/prsche-disasm/pull/12), `2f18edb6c1a4`, Run410:
  отложить.00412030/00414eb0 повторяют400,004dd600 уже имеет owner.
  Есть подтверждённые ошибки перечитывания состояния и ECX receiver.
  Оставшиеся0056a680/005a0f98 не закрывают прямые имена текущего frontier.
- [#13](https://github.com/xfynx/prsche-disasm/pull/13), `ff25fd7016e0`, Run411:
  отложить до исправления packet layout, адресов аргументов и импортов.
  Тела UI полезны как материал реверса, но не для прямого подключения.
- [#14](https://github.com/xfynx/prsche-disasm/pull/14), `0567df347b38`, Run412:
  сохранить как candidate004b4da0. Не принят: требуется полная проверка ABI,
  изменяемых globals/aliasing и немокированных event consumers.
- [#15](https://github.com/xfynx/prsche-disasm/pull/15), `95917ce9893b`, Run413:
  сохранить как candidate004a4a70. Не принят: нужны реальные render/UI providers,
  исходная инициализация данных и воспроизводимый differential стенд.
- [#16](https://github.com/xfynx/prsche-disasm/pull/16), `7313104082a6`, Run414:
  отложить: потерян ECX у реальных методов, тесты не сравнивают аргументы,
  README описывает отсутствующие сценарии разрешений.
- [#17](https://github.com/xfynx/prsche-disasm/pull/17), `b83ea3951535`, Run415:
  WinMain/инициализаторы уже восстановлены. Использовать для независимой сверки,
  не заменять canonical entry и не добавлять отдельные C-linkage owners.
- [#18](https://github.com/xfynx/prsche-disasm/pull/18), `72e88697413a`, Run416:
  три метода уже приняты в295/297. Использовать как cross-check.
  Вопреки заголовку, source416 **не определяет** storage00628960 и правильно
  сохраняет HOLD. Ошибочные определения появляются позднее в419/420.
- [#19](https://github.com/xfynx/prsche-disasm/pull/19), `f390509c15cc`:
  удобный набор материалов для выборочного переноса; общая интеграция не принята.
  Включает все перечисленные defects и новые storage/bridge defects ниже.

## Подтверждённые блокеры

Источник оригинала для адресов ниже: `Porsche.exe`, SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Навигация: `research/binary-index/README.md`, затем
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm` и canonical registry
`iterations/v2/001-original-recovery/source/recovered/functions.json`.

1. **Две разные ячейки00628960 в #19.**419 записывает
   `g_frame_service_root_00628960`; bridge420:10 определяет отдельную
   `frame_service_root_00628960 = 0` для потребителя290. Связи между ними нет.
   Свежие x86 COFF objects подтверждают два различных external definitions.
   В419:8–21 объявлен contiguous struct, но используется не он, а отдельные
   globals. C++ layout/допустимость unbounded copy не обеспечены этим struct.
   Конкретная текущая COFF-компиляция размещает root на+32; это не устраняет
   вторую ячейку420 и не доказывает корректность всего shared layout Run301.

2. **Подмена незавершённых heap данных нулевыми providers.**420:18–22 создаёт
   zero-filled default context и selector[16]. Run303 сохраняет HOLD на их
   реальные identity/init; исходный selector005e4fec указывает на006af374.
   418:6–10 также сохраняет разделённую arena storage: original index16 от
   006af3b4 обращается к guard006af3f4, а C++ индекс выходит за other_arenas[15].
   Компоновка символов не разрешает эти исходные зависимости данных.

3. **Потерянный this в #16.**Оригинал004d342e загружает ECX из00628130 и
   004d3440 вызывает00467fc0; callee00467fd7/00467ff9 читает объект через ECX.
   Source414:362 передаёт только четыре stack args. Аналогично00505810
   использует ECX, а source414:380 его не передаёт. Генератор определяет ABI по
   RET pop, что не отличает thiscall от stdcall. Моки этот receiver не проверяют.

4. **Ошибочные UI bridges #19.**417:73 объявляет free cdecl
   `ui_draw_screen_tree_0048cdf0()`, тогда как411 определяет метод
   `UiScreenContext::ui_draw_screen_tree_0048cdf0()` с ECX и byte return.
   417:85–90 вызывает метод другого, анонимного `UiScreenContextProxy`.
   Свежие cl/dumpbin показывают несовпадающие UNDEF/defined symbols; наличие
   скомпилированных translation units не закрывает эти вызовы.

5. **Неправильный packet layout #13.**411:366–369 выделяет pkt[0x50], затем
   записывает0x4c байта с+8 (конец+84) и0x34 с+0x28 (конец+92). Это выходы за
   80-байтный объект. Original0048de1b..0048de6c использует реальные смещения
   единого stack frame; перевод локальных переменных должен учитывать ESP
   после PUSH, а не копировать псевдо-C offsets на отдельные массивы.

6. **Адреса заменены нулями #13.**Original0048dff1 и0048dff7 делают
   PUSH immediate005b4980/00508e70 перед0055aaa0.411:14–16/399 передаёт значения
   самостоятельно определённых zero DWORDs.00508e70 — адрес кода, не zero cell.
   IAT005b2080 — GetTickCount;411:17/545–546 оставляет nullptr и пропускает вызов.

7. **Устаревший индекс после callback #12.**410:48 кэширует005e9410 до четырёх
   вызовов. Original00412039/0041204c/00412060/00412074 перечитывает его каждый
   раз.400 сохраняет перечитывания; fixture410 использует только постоянный2.
   В410 также отсутствует исходный ECX при вызове00467fc0 из004dd600.

8. **Backend #2 молча теряет вычисления.**`x86-cpp-backend-fpu.py:604–605`
   превращает MOVSS/MULSS/ADDSS и другие SIMD инструкции в no-op/comment.
   Original0059a660 реально использует MOVSS0059a673, MULSS0059a6ac и
   MOVSS0059a6da. FSQRT:278–282 возвращает+0 для отрицательного входа вместо
   x87 invalid/NaN и теряет знак-0. `verify-v2-x86-fpu.py:265–267` снимает
   ST0/ST1/status, но assertions430–467 не сравнивают эти результаты.
   Census означает отсутствие exception у translate(), не сборку/запуск5694 тел.

## Ограничения проверок и фактическая сборка

- 414 fixture сравнивает только tags/count вызовов, хотя записывает аргументы
  (`gen_run_414.py:746–775`). Comparator004d67b0 всегда возвращает1 вместо
  исходного SETNZ. README перечисляет resolution cases, которых нет в666–676.
- Генератор414 требует неверсированный `local/experiments/004d3420.c`.
  Некоторые upstream drivers перезаписывают source/старые runs: вслепую не запускать.
- Локальные upstream fixtures/receipts для400–409 отсутствуют. Заявленные PASS
  не опровергнуты, но здесь не воспроизведены. Полного native-прогона PR не было.
- В отчёте417:185 TUs,348 names/381 refs;420:188 TUs,415 names/446 refs.
  Это upstream reports, не свежие игровые сборки в этом review. EXE не получен.
  CMake417 включает298 вместо актуальной309, теряя подключения305/307.
  Более широкий граф естественно открывает новые зависимости; сами большие
  числа unresolved не являются доказательством ошибки алгоритма.
- Выполнено здесь: Git blob-сравнение всех изменённых файлов #2–#18 с #19
  (совпали); свежая MSVC14.44 x86 компиляция417 bridge,411,419,420 и dumpbin
  symbols (exit0 у всех). Это проверка конкретных ABI/storage findings,
  не native acceptance. Артефакты: `local/reports/pr-review/{review-checks.json,
  compile-crosschecks.json,*.log}`, inventory `local/reports/pr-inventory-20261019.json`.

## Ближайший шаг

1. Отдельный intake-пакет поверх309: выбрать новые400/401 функции без HOLD-зависимостей,
   проверить original CALL/RET, mutable globals и canonical providers. Не переносить
   новый owner для уже принятого VA. Проверить callback mutation отдельно.
2. Сохранить исходные PR blobs, подготовить воспроизводимые fixtures с проверкой
   ECX/ESP/nonvolatile, аргументов и изменяемой памяти; затем один batch native audit
   и свежий game-target build. Не ожидать заранее определённого числа unresolved.
3. После этого bindings для0053c290/0059d8e0/004b68f0/004a88a0/004640b0.
   UI/render и heap/root HOLD требуют исправлений до интеграции.
4. Закрытие/merge PR и отправку findings автору выполнять отдельным поручением;
   текущий результат — локальный разбор применимости, не GitHub review submission.

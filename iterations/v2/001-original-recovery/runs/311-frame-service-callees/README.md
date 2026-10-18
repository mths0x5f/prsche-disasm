# Run 311 — frame service callees

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

This run closes the external frontier that Run 290 left open. `frame_service_290.hpp`
declared the three callees of the recovered service cycle `00487e20` and the storage
cell `00628960` as unrecovered. Run 311 recovers the three bodies, so the Run 290
consumer links against real definitions for them. The storage cell stays on hold —
see below:

- `00423840..00423882` (67 bytes): `FrameIterator_290::advance_00423840` — in-order
  tree successor. `ECX` points at the iterator's single node-pointer slot; the node
  fields the body dereferences are `+0x04` parent, `+0x08` left, `+0x0c` right.
- `00482e50..00482e94` (69 bytes): `FrameTail_290::invoke_00482e50` — advances the
  `+0x04` timer of every active element of the `0x38`-strided array at `this+0x40`
  whose timer is not above the limit. Both the count at `this+0x18` and the base
  pointer at `this+0x40` are reloaded on every iteration, as in the original.
- `00476170..00476218` (169 bytes): `FrameAction_290::invoke_00476170` — per-element
  lifecycle transition and dispatch over the `0x38`-strided array at `this+0x0c`,
  counted by `[[this+0x04]+0x18]`. For each element holding an object it calls
  `00476710`, then either destructs the object through vtable slot `0x00` and carries
  six dwords from `element+0x1c` into `*(element+0x34)`, or dispatches vtable slot
  `0x1c`, and clears `element+0x08` in every case.

Total recovered PE body bytes: 305 bytes across 3 functions.

## Evidence

| Target | Range | Bytes | Body SHA-256 |
| --- | --- | --- | --- |
| `advance_00423840` | `00423840..00423882` | 67 | `8b75f5520e19b4380d2165f85398dfb9d39e71290de039430625dd5d7f6ef911` |
| `invoke_00482e50` | `00482e50..00482e94` | 69 | `ebc3fb1a31138079e8fc8ff47b5a7e6309bd69c607b7e14b27fb4bf763d1446b` |
| `invoke_00476170` | `00476170..00476218` | 169 | `0a4456508d1f9ad2a42da22096714106580b57fa5b16aa299fe2644f515b5d3e` |

The caller is the Run 290 body `00487e20`, which reaches `00476170` through the
resolver result, `00423840` on the iterator slot, and `00482e50` on the tail object
at `this+0x1c`. Catalog entries for the three VAs report the same body ranges and
byte counts as the extracted ranges above.

Read-only scalars that `00482e50` loads, verified against the image bytes:
`005b47d8` = `0000fa45` = `8000.0f` (limit) and `005b2764` = `00401c46` = `10000.0f`
(increment). The original compares with `fcomp` and then `test ah,0x41`, which tests
`C0|C3` — "not greater", with the unordered result also taken. The recovery writes
`!(timer > limit)` so a NaN timer takes the adjustment exactly as the original does.

### Storage cell 00628960

A HIGHLOW operand scan of `.text` finds exactly three stores into the cell, in two
owners, and `00628960` is a single 32-bit pointer cell:

- `00471b70` (initialiser): `00471bae` stores the object constructed by `004874a0`
  after `operator new(0x3c)` at `0059ef90` succeeds; `00471bb5` stores `0` when the
  allocation fails.
- `00471c40` (teardown): `00471c6d` stores `0` after destructing the object through
  `00487590` and freeing it through `0059f050`.

**Neither owner is recovered in this run, and the cell is deliberately not defined.**
This run contributes ownership evidence only.

A standalone zero-initialised definition would not be faithful. The string copy at
`00471b72..00471b97` is an unbounded `REP MOVSD` into `00628940`, which sits just 32
bytes before the cell, so in the original a source string of 32 bytes or more reaches
the cell's storage. Separate C++ objects lose that adjacency. The cell therefore stays
an unresolved link boundary until the shared original layout covering `00628940`, the
cell and `00628964` is recovered together.

## Validation

The fixture copies the three original bodies onto a `PAGE_EXECUTE_READWRITE` slab,
patches the two HIGHLOW scalar operands of `00482e50` (body offsets `0x20`, `0x30`)
and the single relative `CALL 00476710` of `00476170` (body offset `0x2b`), then runs
each case twice over the same scene memory: once through the original bytes and once
through the recovered C++. A case passes only when the post-state bytes and the
recorded call trace are identical.

The 12 controlled cases cover: successor through a right child with and without a
left chain; successor of a left child; a multi-level right-child ascent; the
single-element tree with its header, where the final guard must leave the iterator on
the header; a zero element count; selective timer adjustment by the active flag and
the limit; the limit boundary (`8000.0f` adjusted, `8000.001f` not) and a negative
timer; a zero count with a populated element; the destruct-and-carry branch; the
vtable `0x1c` branch; and a non-zero object flag taking neither branch.

```
python scripts/research/experiment-v2-frame-service-311.py --finalize --attempt 1
python scripts/research/audit-v2-frame-service-311.py
```

The experiment compiles with MSVC `/Od /Oi /Gy /GS- /GR- /EHsc /TP /W4 /Zl`
(no warnings), links with `/NODEFAULTLIB /ENTRY:entry /MACHINE:X86`, and reports
12/12 cases. The audit re-derives the body ranges, terminating `RET`, body SHA-256
values, both scalars and the three storage-cell writers from the retail image rather
than from `summary.json`, and checks the COFF symbols and build receipts.

The recovery object defines exactly the three function symbols that were Run 290's
frontier: `advance_00423840`, `invoke_00482e50` and `invoke_00476170`. It leaves
`00476710`, the two read-only scalars and `frame_service_root_00628960` undefined; the
fixture supplies the first two, and a game-target build still has to.

Fixture validation was itself checked by negative control: four separate mutations of
the recovered sources (dropping the final guard of `00423840`, using `<` instead of
"not greater" in `00482e50`, dropping the `element+0x08` clear, and carrying five
dwords instead of six) each failed only the cases that should catch them.

### Boundaries

- `00476710` (136 bytes), `00471b70` (198 bytes), `00471c40` (65 bytes),
  `004874a0` (230 bytes) and `00487590` remain unrecovered.
- `00476170` loads the object flag at `+0x04` before the null check that follows it,
  so the original dereferences the pointer reloaded after `00476710` unconditionally.
  The recovery reproduces that order rather than hoisting the check.
- Node offset `+0x00` and the opaque element ranges are named `opaque_*` because
  these three bodies never read them; their types are not established here.

---

# Запуск 311 — вызываемые функции frame service

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Запуск закрывает внешнюю границу, оставленную Run 290. В `frame_service_290.hpp`
три вызываемые функции цикла `00487e20` и ячейка `00628960` были объявлены
невосстановленными. Run 311 восстанавливает три тела, поэтому потребитель Run 290
линкуется с реальными определениями для них. Ячейка хранения остаётся на HOLD:

- `00423840..00423882` (67 байт): `FrameIterator_290::advance_00423840` — следующий
  узел дерева в порядке обхода. `ECX` указывает на единственный слот указателя узла;
  используемые поля узла: `+0x04` родитель, `+0x08` левый, `+0x0c` правый.
- `00482e50..00482e94` (69 байт): `FrameTail_290::invoke_00482e50` — увеличивает
  таймер `+0x04` каждого активного элемента массива с шагом `0x38` по `this+0x40`,
  если таймер не превышает предел. Счётчик `this+0x18` и базовый указатель
  `this+0x40` перечитываются на каждой итерации, как в оригинале.
- `00476170..00476218` (169 байт): `FrameAction_290::invoke_00476170` — переход и
  диспетчеризация жизненного цикла по массиву с шагом `0x38` по `this+0x0c`,
  количество — `[[this+0x04]+0x18]`. Для каждого элемента с объектом вызывается
  `00476710`, затем либо деструктор через слот vtable `0x00` и перенос шести dword
  из `element+0x1c` в `*(element+0x34)`, либо слот vtable `0x1c`; `element+0x08`
  обнуляется в любом случае.

Суммарный объём восстановленного PE-кода: 305 байт в 3 функциях.

Константы только для чтения, проверенные по байтам образа: `005b47d8` = `8000.0f`
и `005b2764` = `10000.0f`. Оригинал сравнивает через `fcomp` и `test ah,0x41`, то
есть `C0|C3` — «не больше», включая неупорядоченный результат; восстановление
использует `!(timer > limit)` и воспроизводит поведение для NaN точно.

Сканирование операндов HIGHLOW в `.text` находит ровно три записи в ячейку
`00628960` у двух владельцев: инициализатор `00471b70` (`00471bae` — объект после
`operator new(0x3c)`, `00471bb5` — `0` при неудаче выделения) и завершение
`00471c40` (`00471c6d` — `0` после деструктора и освобождения). **Ни один из
владельцев в этом запуске не восстановлен, и ячейка сознательно НЕ определена**:
предоставляется только доказательство владения. Отдельное определение с нулевой
инициализацией не было бы достоверным — копия строки в `00471b72..00471b97` это
`REP MOVSD` без границы в `00628940`, всего за 32 байта до ячейки, поэтому в
оригинале строка от 32 байт достигает её хранения. Ячейка остаётся нерешённой
границей линковки до восстановления общей исходной раскладки `00628940`, ячейки и
`00628964` вместе.

Поведение подтверждено 12 дифференциальными тестами на физическом x86-слебе памяти
оригинального бинарника: байты состояния и трасса вызовов совпадают для оригинальных
байтов и восстановленного C++. Дискриминирующая способность фикстуры проверена
четырьмя мутациями восстановленных исходников — каждая провалила только те случаи,
которые должна была.

Невосстановленными остаются `00476710` (136 байт), `00471b70` (198 байт),
`00471c40` (65 байт), `004874a0` (230 байт) и `00487590`.

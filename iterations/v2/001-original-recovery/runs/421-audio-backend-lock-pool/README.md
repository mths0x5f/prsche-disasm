# Run 421 — audio backend lock and pool helpers

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Ten leaf bodies of the audio backend, 239 PE body bytes, taken from the game link
frontier (Run 420, `build-003.json`). Six of them were already declared, with typed
signatures, by the canonical `source/include/porsche/application_audio_device.hpp` and
`application_audio_lifecycle.hpp`; two more by Run 400. Their recovery is compiled
against those declarations, so the mangled names and signatures are checked by the
compiler rather than copied.

## Recovered

| VA | Bytes | Symbol | What the body does |
| --- | --- | --- | --- |
| `0058e2d0` | 12 | `application_audio_backend_start_0058e2d0` | `InitializeCriticalSection(006b1800)` |
| `0058e2e0` | 12 | `application_audio_backend_stop_0058e2e0` | `DeleteCriticalSection(006b1800)` |
| `0058e2f0` | 12 | `audio_backend_enter_0058e2f0` | `EnterCriticalSection(006b1800)` |
| `0058e300` | 12 | `audio_backend_leave_0058e300` | `LeaveCriticalSection(006b1800)` |
| `005896d0` | 18 | `audio_backend_lock_005896d0` | enter, then 8-bit `++` of the counter `006b499f` |
| `005896f0` | 17 | `audio_backend_unlock_005896f0` | 8-bit `--` of the counter, then tail `jmp` to leave |
| `0058aa90` | 44 | `application_audio_backend_configure_0058aa90` | publish the buffer as the pool (`006b4a18`) and write its 5-dword header |
| `0058aac0` | 31 | `application_audio_backend_close_0058aac0` | `((size - cursor) * 100) / size`, signed |
| `0058fef0` | 31 | `application_audio_backend_configure_0058fef0` | zero `len` bytes at `dst` (`rep stosd` + `rep stosb`), only for `len > 0` signed |
| `0058ff10` | 50 | `application_audio_backend_quiet_0058ff10` | call `00565d60` for every 0x70-byte channel record |

**Three canonical names describe the bodies wrongly** and were kept only because they
are the link contract: `start`/`stop` create and destroy the lock rather than start or
stop anything, and `close` returns the pool usage percentage. The table above, the
source comments and the audit record what the bytes do. The audit proves the four lock
primitives from the import table, not from the names: `0058e2d0`, `0058e2e0`, `0058e2f0`
and `0058e300` call through the IAT cells `005b207c`, `005b2068`, `005b2078` and
`005b206c`, which hold `KERNEL32!InitializeCriticalSection`, `DeleteCriticalSection`,
`EnterCriticalSection` and `LeaveCriticalSection`.

Faithfulness points the fixture checks: the counter wraps at 8 bits in both directions;
`unlock` decrements **before** it leaves; `0058fef0`'s length test is signed, so negative
lengths do nothing; `0058aa90` writes the header in the original store order; the
`0058aac0` multiply wraps in 32 bits before the signed division; `0058ff10` reads the
count as a signed 16-bit value and reloads both the count and the table pointer after
every call.

Calls to Win32 go through the existing `platform_*_critical_section` wrappers in
`source/platform/win32_core.cpp`; no new platform code was added.

## Storage boundaries

None of the cells these bodies touch is defined here: the `CRITICAL_SECTION` at
`006b1800`, the counter `006b499f`, the pool pointer `006b4a18`, the channel count
`006b49a4` and the table pointer `006b4a00`. They are declared `extern` and stay link
boundaries. The counter sits 3 bytes after `audio_system_active_006b499c` and 5 bytes
before the channel count, so the backend state looks like one block; defining loose
cells before that layout is proven is what went wrong with `00628960`.

## Validation

30/30 controlled differential cases on a physical x86 memory slab holding the ten
original bodies. Every absolute operand, IAT cell and rel32 transfer is patched to
fixture storage or hooks, and each patch first checks the original value at its offset,
so a wrong offset fails initialisation. The lock chain stays original-to-original:
`005896d0` calls the slab copy of `0058e2f0`, and `005896f0` jumps to the slab copy of
`0058e300`. Each case runs twice over the same memory, original bytes and recovered C++,
and passes only when the post-state bytes, the call trace (including the lock counter
at the moment of each call) and any return value are identical.

```
python scripts/research/experiment-v2-audio-backend-421.py --finalize --attempt 1
python scripts/research/audit-v2-audio-backend-421.py
```

Compiled with MSVC `/Od /Oi /Gy /GS- /GR- /EHsc /TP /W4 /Zl` with no warnings, linked
`/NODEFAULTLIB /ENTRY:entry /MACHINE:X86`.

Negative control: six mutations of the recovered C++ each fail. They are leaving before
decrementing in `unlock`, incrementing by 2 in `lock`, skipping the byte tail of the
zeroing, an off-by-one pool limit, an unsigned division in the usage, and reading the
channel count only once. The last one first **passed**, because the callbacks only
changed the count on the first call, after which a single read sees the same value.
Three cases now change the count or the table on the second call, and it fails.

The object defines the ten functions plus `__Avx2WmemEnabledWeakValue`, a weak value the
MSVC STL emits into any translation unit that includes `<array>`, which the canonical
header does. It leaves undefined the five storage cells, `audio_channel_stop_00565d60`
(Run 400) and the four `platform_*_critical_section` wrappers.

### Boundaries

- Storage for the five cells, and the layout of the block they belong to.
- The pool allocator itself: only the header fields these two bodies write and read are
  named, and their roles beyond that are not claimed.
- Not integrated into the game target in this run.

---

# Запуск 421 — блокировка и пул аудио-бэкенда

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Десять листовых функций аудио-бэкенда, 239 байт тела PE, из фронтира линковки игры
(Run 420, `build-003.json`). Шесть из них уже объявлены с типами в каноническом
`application_audio_device.hpp` и `application_audio_lifecycle.hpp`, ещё две — в Run 400;
восстановление компилируется против этих объявлений, поэтому имена и сигнатуры проверяет
компилятор.

- `0058e2d0`, `0058e2e0`, `0058e2f0`, `0058e300` — `Initialize`, `Delete`, `Enter` и
  `LeaveCriticalSection` над `006b1800`; это доказано по таблице импорта (ячейки IAT
  `005b207c`, `005b2068`, `005b2078`, `005b206c`), а не по именам.
- `005896d0` / `005896f0` — вход с 8-битным `++` счётчика `006b499f` и 8-битный `--` с
  хвостовым переходом на выход; выход происходит **после** уменьшения.
- `0058aa90` — публикует буфер как пул (`006b4a18`) и пишет заголовок в исходном порядке;
  `0058aac0` — `((size - cursor) * 100) / size` со знаком; `0058fef0` — обнуление `len`
  байт только при `len > 0` со знаком; `0058ff10` — вызов `00565d60` для каждой записи
  канала с шагом 0x70, счётчик знаковый 16-битный и перечитывается после каждого вызова.

**Три канонических имени неверно описывают тела** (`start`, `stop`, `close`) и
сохранены только как контракт линковки.

Ячейки `006b1800`, `006b499f`, `006b4a18`, `006b49a4` и `006b4a00` здесь **не
определяются** и остаются границами линковки: счётчик лежит в 3 байтах после
`audio_system_active_006b499c`, то есть состояние бэкенда похоже на единый блок.

30/30 дифференциальных проверок на физическом x86-слэбе. Отрицательный контроль: шесть
мутаций восстановленного C++ проваливаются; одна сначала прошла, что выявило пробел в
случаях, и были добавлены три случая с изменением на втором вызове.

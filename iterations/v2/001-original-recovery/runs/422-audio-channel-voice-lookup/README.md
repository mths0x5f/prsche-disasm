# Run 422 — audio channel lookup and voice iteration

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Two leaf bodies over the audio channel table, 212 PE body bytes, both called only by
`audio_channel_stop_00565d60` (Run 400). With Run 421's lock and unlock, they leave
`audio_backend_stop_voice_0058a8b0` as that function's last unrecovered callee.

| VA | Bytes | Symbol |
| --- | --- | --- |
| `00589d20..00589d6e` | 79 | `audio_backend_find_channel_00589d20` |
| `00590340..005903c4` | 133 | `audio_backend_next_voice_00590340` |

The table is the one Run 421 reads: a signed 16-bit count at `006b49a4` and a pointer at
`006b4a00` to `0x70`-byte records. These bodies prove three record fields: `+0x00` the
channel handle, `+0x0f` an active byte, and `+0x1e` a voice group.

**`find_channel`** takes the channel index from the handle's low byte. It returns that
index only if the handle is non-negative, the index is below the signed count, the
record's active byte is non-zero and the record holds the same full handle; every
failure returns `-8`.

**`next_voice`** advances `*voice_slot` to the next voice of a channel's group and
returns 1, or returns 0 when there is none. An ungrouped channel (group 0) is its own
single voice: the first call, from a negative slot, stores the channel and returns 1,
and the next returns 0. A grouped channel scans forward from `slot + 1` for a record of
the same group whose active byte is **exactly 1** and whose handle is non-negative.
`find_channel` accepts any non-zero active byte, so a record with active `2` is found
but never iterated; the fixture covers that case. The slot is written before every
bound test, so it ends one past the last index tried. It is declared `uint32_t*` by
Run 400, but every comparison on it is signed, and the caller starts it at
`0xffffffff`. The table pointer and count are read once, which is correct here because
the body makes no calls.

## Storage boundaries

The count and the table pointer are declared `extern`, identically to Run 421, and left
undefined.

## Validation

17/17 controlled differential cases on a physical x86 memory slab holding both original
bodies, with the four absolute operands patched only after their original values are
checked. `next_voice` is driven the way its caller drives it, from slot `0xffffffff`
until it returns 0, and every `(result, slot)` pair is compared.

```
python scripts/research/experiment-v2-audio-channel-voice-422.py --finalize --attempt 1
python scripts/research/audit-v2-audio-channel-voice-422.py
```

Compiled with MSVC `/Od /Oi /Gy /GS- /GR- /EHsc /TP /W4 /Zl` with no warnings, linked
`/NODEFAULTLIB /ENTRY:entry /MACHINE:X86`.

Negative control: seven mutations of the recovered C++ each fail — a `<=` count bound, an
ignored active byte, comparing only the handle's low byte, accepting any non-zero active
byte while iterating, dropping the handle sign test, skipping the slot store before the
bound test, and an unsigned slot test for ungrouped channels.

The object defines exactly the two functions, whose mangled names match the game link
frontier, and leaves only the two storage cells undefined.

### Boundaries

- Storage for the channel table cells.
- `audio_backend_stop_voice_0058a8b0` and its callees (`00597010`, `0058ac30`,
  `00589c00`, and a function pointer inside each `0xf8`-byte voice record at
  `006b489c`) are a separate packet.
- Not integrated into the game target in this run.

---

# Запуск 422 — поиск аудиоканала и обход голосов

Оригинал `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Две листовые функции над таблицей аудиоканалов, 212 байт тела PE; обе вызываются
только из `audio_channel_stop_00565d60` (Run 400).

- `00589d20` (79 байт): индекс канала — младший байт дескриптора; возвращается, только
  если дескриптор неотрицателен, индекс меньше знакового счётчика, байт активности
  ненулевой и запись хранит тот же дескриптор; иначе `-8`.
- `00590340` (133 байт): переводит `*voice_slot` на следующий голос группы канала и
  возвращает 1, иначе 0. Канал без группы (0) — единственный голос самого себя. Для
  группы ищется запись той же группы с байтом активности **ровно 1** и неотрицательным
  дескриптором. Слот записывается перед каждой проверкой границы; все сравнения слота
  знаковые.

Ячейки счётчика и таблицы объявлены `extern` и не определяются. 17/17 дифференциальных
проверок на физическом x86-слэбе; семь мутаций восстановленного C++ проваливаются.

# Run 425 — audio voice stop and its callee tree

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

`audio_backend_stop_voice_0058a8b0` was the last unrecovered callee of
`audio_channel_stop_00565d60` (Run 400); with Runs 421 and 422 that function's whole tree is now
recovered. This run takes the voice stop and the three bodies it reaches, 551 PE body bytes.

| VA | Bytes | Symbol |
| --- | --- | --- |
| `0058a8b0..0058a907` | 88 | `audio_backend_stop_voice_0058a8b0` |
| `00597010..00597062` | 83 | `audio_voice_release_links_00597010` |
| `0058ac30..0058ac96` | 103 | `application_audio_backend_release_0058ac30` (canonical declaration) |
| `00589c00..00589d14` | 277 | `audio_channel_group_release_00589c00` |

- **`0058a8b0`** calls the voice record's stop callback (`+0xc8`, cdecl) with `&link_a` (`+0x2c`),
  then reads the flags, **after** the call: bit 1 clears `+0xf4`, otherwise bit 2 releases the link
  list. Independently, flag `0x10`, re-read from memory, makes the channel leave its group. Voice
  records are `0xf8` bytes from the table at `006b489c`, and a voice index is also a channel index.
- **`00597010`** walks the list at `+0xc4` and releases every node except the two embedded ones
  (`+0x2c`, `+0x64`), reading each `next` before releasing. The voice index is the signed word at
  `link_b + 2`. That word overlaps the next pointer of `link_b` at `+0x64`, so `link_b` can only end
  a list.
- **`0058ac30`** removes an entry from the pool's allocation table. The table grows downward from
  `end_marker` in 8-byte `{offset, size}` entries, with a negative count at pool `+0x14`, a field
  beyond Run 421's header. It moves the count toward zero, grows `+0x0c` by 8 and shifts the lower
  entries up to close the gap. The body returns `-8`/`0` in `eax`; the canonical declaration is
  `void`, and the only caller ignores it.
- **`00589c00`** counts the live members of the channel's group and remembers the **last** one with
  the leader byte `+0x1b` set. It then releases the channel (active 0, group 0, stamp from
  `006b49a8` into `+0x20`), releases both a two-member pair, or promotes a self-leader from active 1
  to 2.

**Faithfulness note.** When no member has the leader byte and the count is not 1, the original
indexes record **-1**, 0x70 bytes before the channel table. It reads that record's active byte and,
with exactly two members and active 2, releases it too. The recovery computes the same address and
does the same; it does not add a bound the original lacks. The fixture places a guard record there,
and a mutation that bounds the index fails.

## Storage boundaries

`006b489c` (voice table) and `006b49a8` (stamp) are new `extern` cells, alongside Runs 421/422's
pool, channel count and channel table. None is defined here.

## Validation

22/22 differential cases on a physical x86 slab holding all four bodies, chained
original-to-original, with 11 absolute operands patched only after their original values are
checked. The stop callback is a shared hook that can rewrite the flags, which proves they are read
after the call. Negative control: eight mutations of the recovered C++ each fail.

```
python scripts/research/experiment-v2-audio-voice-stop-425.py --finalize --attempt 1
python scripts/research/audit-v2-audio-voice-stop-425.py
```

The object defines the four functions plus the MSVC STL weak value `__Avx2WmemEnabledWeakValue`
(from the canonical header's `<array>`), and leaves only the five storage cells undefined.

---

# Запуск 425 — остановка аудиоголоса и дерево её вызовов

Восстановлены `0058a8b0` (остановка голоса: callback записи, флаги читаются после вызова), `00597010`
(освобождение узлов списка, кроме двух встроенных), `0058ac30` (удаление записи из таблицы аллокаций
пула со сдвигом) и `00589c00` (выход канала из группы), всего 551 байт. При отсутствии лидера и числе
участников не равном 1 оригинал обращается к записи с индексом **-1** перед таблицей; восстановление
воспроизводит это точно. 22/22 дифференциальных проверок, восемь мутаций проваливаются. Ячейки
`006b489c` и `006b49a8` объявлены `extern` и не определяются.

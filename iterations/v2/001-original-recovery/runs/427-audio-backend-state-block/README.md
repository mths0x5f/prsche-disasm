# Run 427: the audio module's state as one block with original offsets

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Runs 400, 421, 422 and 425 left eight audio backend cells as `extern` boundaries. Run 421 noted
that they "look like one block". This run proves the layout and supplies the storage.

## Evidence

- **Extent.** Every HIGHLOW target in `006b00c0..006b4a44` (175 targets, 723 sites) is referenced
  from the audio code: `00589xxx`–`0059cxxx` and the `00565xxx` wrappers. The neighbours belong to
  other modules: `006b00a0` from `00531c30`, and `006b4a60+` from `0057x`/`0058x`. The block lies
  in the zero-fill tail of `.data`, which is RW and non-executable.
- **Widths.** Every reference to the eight cells is a direct access of the declared width, or an
  address taken for the CRITICAL_SECTION at `006b1800`. This covers 15 sites in functions that
  only pointer calls reach, which the catalog and the Ghidra export miss: the timer callback
  `00589520` (address taken at `005657c8`), `00565920` and the `00596890`–`00596f07` group.
- **The cells are not independent.**
  - The 16-byte records at `006b4a08`, indexed by `& 0x1f` (`00565c70`, `00590250`), reach the
    pool cell `006b4a18` as record 1, field +0.
  - The byte array at `006b4886`, indexed by `& 0x1f` (`00590250`), reaches the voice table
    pointer `006b489c` at index `0x16`.
- **Shared with canonical storage.** The canonical `application_audio_device_state_006b48c0`
  (0x18c bytes from `006b48b0`; `data()` is `006b48c0`) already spans `006b499c/9f`,
  `006b49a4/a8`, `006b4a00` and `006b4a18`. `00565720` writes those cells through it, while Runs
  421/425 read them by name. Separate definitions would split one memory into two objects, the
  same defect class as `00628960` in Run 419.

## Storage

`audio_backend_state_427.asm` is generated from the `LAYOUT` table of the experiment script. It
is one MASM data object of `0x4984` bytes in an uninitialized, RW, 64-byte-aligned section. It
has a public label at the original offset of each of the nine C++ names:

| VA | Name |
| --- | --- |
| `006b1800` | `audio_backend_lock_cs_006b1800` (24 bytes) |
| `006b489c` | `audio_voice_table_006b489c` |
| `006b48b0` | `application_audio_device_state_006b48c0` (0x18c bytes) |
| `006b499c` | `audio_system_active_006b499c` |
| `006b499f` | `audio_backend_lock_depth_006b499f` |
| `006b49a4` | `audio_backend_channel_count_006b49a4` |
| `006b49a8` | `audio_backend_stamp_006b49a8` |
| `006b4a00` | `audio_backend_channels_006b4a00` |
| `006b4a18` | `audio_backend_pool_006b4a18` |

C++ cannot place one global inside another, so the labels are the only faithful way to keep
these names on shared memory without changing every consumer's declaration. The bytes between
labels belong to cells whose owners are not recovered yet. They are part of the block, not
separate objects. The block's edges remain boundaries: an index that runs past `006b4a44`
(records at `006b4a08` above index 3) or below `006b00c0` is not reproduced.

## Validation

```
py -3 scripts/research/experiment-v2-audio-state-block-427.py --check
```

- **PE checks:** the original-PE checks above.
- **COFF offsets:** each label's offset in the object equals its original VA minus `006b00c0`.
- **Native fixture:** 19 checks pass. The fixture includes the canonical header and the
  Run 421/425 headers, so a type mismatch fails to compile. It checks:
  - each name's original VA;
  - 64-byte alignment;
  - that the whole block starts zero;
  - aliasing in both directions between the named cells and the device state view;
  - that record 1 of `006b4a08` is the pool and byte `0x16` of `006b4886` is the voice table.
- **Negative control:**
  - Moving the pool label to `006b4a14` fails three fixture checks.
  - Moving it to `006b4a1c` is rejected by the PE reference check.

---

# Запуск 427 — состояние аудиомодуля единым блоком

Нулевая статическая память аудиомодуля `006b00c0..006b4a44` (175 HIGHLOW-целей, 723 места; все
ссылки из аудиокода) задана одним MASM-объектом с публичными метками девяти C++-имён на исходных
смещениях. Ячейки не независимы:
- записи `006b4a08` (индекс `&0x1f`) достигают пула `006b4a18`;
- байты `006b4886` достигают указателя таблицы голосов `006b489c`;
- каноническое `application_audio_device_state_006b48c0` (`006b48b0..006b4a3c`) уже покрывает
  шесть ячеек.

Отдельные определения разорвали бы общую память. 19 нативных проверок проходят; сдвиг метки пула
ловится. Края блока остаются границами.

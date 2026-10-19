# Run 428: audio state block and input caps buffer in the game target

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

The CMake wraps Run 426 and makes four changes:
- enables `ASM_MASM`;
- adds Run 427's `audio_backend_state_427.asm` to `porsche_game_entry_bridges`, assembled with
  `/safeseh`;
- defines `PORSCHE_AUDIO_STATE_BLOCK` for `porsche_original`;
- with that macro, the canonical `application_audio_device.cpp` compiles out its definition of
  `application_audio_device_state_006b48c0`, because the block owns that storage. Run 133 and
  the device verifier still build the definition unchanged.

**Input caps buffer.** `input_caps_buffer_006bde20[0x21c]` is now defined in the canonical
`input_state.cpp`, next to the slots. Its only users are `00532e10`, which takes its address,
and `0056fdb0`, which clears exactly `0x21c` bytes. Nothing indexes it. The two input probes no
longer define it. Run 423's fixture generator now relies on the canonical definition; its
native fixture was regenerated and passes 24/24 (attempt 2). The original's distance of
`0x220` bytes from the slots is not reproduced, and only the unrecovered negative-index path
could depend on it.

## Build

```
py -3 scripts/research/build-v2-game-link-428.py --phase configure --attempt 001
py -3 scripts/research/build-v2-game-link-428.py --phase build --attempt 001
```

Result: 192 sources, 0 compiler errors, 0 other linker errors. The frontier went from 412 names /
439 references to **398 names / 419 references**, with no new name.
- **Nine storage names closed:** the eight audio cells and `input_caps_buffer_006bde20`.
- **Five audio backend functions left the frontier for a different reason:**
  `0058a4f0`, `0058a690`, `0058aae0`, `0058e0e0`, `0058fdb0`. They are still unrecovered.
  - Only `00565720` and `005656d0` in `application_audio_device.obj` reference them.
  - The linker used to pull that object from the `porsche_original` static library solely for
    its storage symbol. The block now provides that symbol, so the object is no longer linked.
  - Its functions have no caller in the current game graph. They will return to the frontier
    when that graph reaches them.

No EXE yet.

---

# Запуск 428 — блок состояния аудио и буфер caps ввода в игровой цели

ASM-блок 427 подключён; каноническое определение `application_audio_device_state_006b48c0`
исключено макросом только в игровой цели. `input_caps_buffer_006bde20` определён в
`input_state.cpp`. Фронтир: 412/439 → 398/419. Закрыты 9 имён хранения. Ещё 5 функций бэкенда
ушли из фронтира, потому что `application_audio_device.obj` больше не подтягивается из
библиотеки: его функции не вызываются текущим графом. EXE пока нет.

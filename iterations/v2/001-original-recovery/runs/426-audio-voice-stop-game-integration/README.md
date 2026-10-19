# Run 426 — audio voice stop in the game target

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Adds Run 425 (voice stop tree) to the game target on top of Run 424. Fresh build (`build-001.json`):
**192** sources, zero compiler and zero other linker errors.

The frontier stays at **412 names** and goes from 436 to **439 references**:

- **2 closed:** `audio_backend_stop_voice_0058a8b0` and `application_audio_backend_release_0058ac30`.
- **2 new**, the storage cells Run 425 declares and leaves undefined: the voice table pointer
  `006b489c` and the release stamp `006b49a8`. They are read at several sites, hence the higher
  reference count.

With this, every function in `audio_channel_stop_00565d60`'s tree is recovered and linked. What
remains of that path in the frontier is storage: the audio backend state cells (`006b1800`,
`006b499c`, `006b499f`, `006b49a4`, `006b49a8`, `006b4a00`, `006b4a18`, `006b489c`), which look like
one block and need their layout recovered before they are defined. No EXE was produced and the
game was not run.

```
python scripts/research/build-v2-game-link-426.py --phase configure --attempt 001
python scripts/research/build-v2-game-link-426.py --phase build --attempt 001
python scripts/research/audit-v2-audio-voice-stop-integration-426.py
```

---

# Запуск 426 — остановка аудиоголоса в игровой цели

Run 425 добавлен в игровую цель поверх Run 424: 192 исходника, 0 ошибок. Фронтир остаётся 412 имён
(436 → 439 ссылок): закрыты 2 функции, добавлены 2 ячейки памяти, оставленные границами. Всё дерево
`audio_channel_stop_00565d60` восстановлено и слинковано; остаётся раскладка блока состояния
аудио-бэкенда. EXE нет, игра не запускалась.

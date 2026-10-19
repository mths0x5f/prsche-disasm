# Run 424 — input and audio in the game target

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Adds Runs 421 (audio backend lock/pool) and 422 (channel lookup, voice iteration) and a new
platform adapter, `source/platform/win32_input.cpp`, to the game target on top of Run 420.
Run 423's `_getstate` completion is canonical and was already in the graph.

`win32_input.cpp` provides the five input boundaries with the exact imports the original uses,
each traced from its call site:

| Boundary | Original call |
| --- | --- |
| `startup_input_get_module_handle` | `0055fd49`: `call [005b2138]` = `KERNEL32!GetModuleHandleA(NULL)` |
| `startup_input_direct_input_create` | `0055fd50`: thunk `0056e940` = `jmp [005b202c]` = `DINPUT!DirectInputCreateA(hinst, 0x500, &006a5b14, NULL)` |
| `startup_get_keyboard_type` | `00564e71`: `esi = [005b2298]` = `USER32!GetKeyboardType`, called twice |
| `startup_joy_get_num_devs` | `00564abe`: `call [005b2354]` = `WINMM!joyGetNumDevs` |
| `startup_joy_get_dev_caps` | `00564ad0`: `edi = [005b2358]` = `WINMM!joyGetDevCapsA` |

**Platform deviation:** current Windows SDKs ship `dinput8.lib` but no `dinput.lib`, so the same
`DINPUT.dll!DirectInputCreateA` export is resolved on first use with `LoadLibraryA` /
`GetProcAddress`. Arguments and the DLL entry are unchanged. Where the original EXE would fail to
load without `DINPUT.dll`, this returns `E_FAIL` from the call. `winmm` is added to the game
link libraries.

## Result

Fresh build of the explicit `porsche_original_game_link` target (`build-001.json`):
**191** C++ sources, zero compiler errors, zero other linker errors. The link frontier, counted
with the corrected parser from Run 420, goes from **423 names / 446 references** (Run 420
`build-003.json`) to **412 / 436**:

- **17 closed:** the ten Run 421/422 audio functions, the two `_getstate` boundaries Run 423
  removed, and the five input adapters above.
- **6 new**, exactly the storage cells those runs leave as declared boundaries: the five audio
  backend cells (`006b1800`, `006b499f`, `006b4a18`, `006b49a4`, `006b4a00`) and the mode-2 caps
  buffer `006bde20`.

No EXE was produced and the game was not run.

```
python scripts/research/build-v2-game-link-424.py --phase configure --attempt 001
python scripts/research/build-v2-game-link-424.py --phase build --attempt 001
python scripts/research/audit-v2-input-audio-integration-424.py
```

The audit re-derives the frontier from the link log with the producer's parser, requires it to
match the report, and checks the exact closed and new sets against Run 420.

---

# Запуск 424 — ввод и звук в игровой цели

Добавляет Run 421 и 422 и новый платформенный адаптер `source/platform/win32_input.cpp` к
игровой цели поверх Run 420. Адаптер даёт пять границ ввода с точными импортами оригинала
(`GetModuleHandleA`, `DirectInputCreateA`, `GetKeyboardType`, `joyGetNumDevs`, `joyGetDevCapsA`),
каждый прослежен от места вызова. Отклонение платформы: `dinput.lib` больше нет в SDK, поэтому тот
же экспорт `DINPUT.dll` разрешается при первом вызове.

Свежая сборка: 191 исходник, 0 ошибок компилятора и прочих ошибок линковки. Фронтир: 423 → 412 имён
(446 → 436 ссылок): закрыто 17 контрактов, добавлено 6 — ровно ячейки памяти, оставленные этими
запусками как объявленные границы. EXE нет, игра не запускалась.

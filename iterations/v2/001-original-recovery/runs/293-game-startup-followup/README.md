# Run293: fresh current-source game-target build

The actual MSVC Win32 game target compiled **all151 C++ translation units** in
its eight-project dependency graph. The log's151 source names match the actual
project graph. This build uses current sources, including the typed291 resolver,
the292 single48-slot CRT lock prefix, and the original logging newline restored
at its canonical `app_main` call. It does not reuse the old game libraries.

Linking still fails with **269 unresolved names /305 references**. Compared with
Run289, the getter contract is now resolved. There are zero compiler errors and
zero other linker errors. Three C4005 macro warnings come from unchanged platform
sources defining WIN32_LEAN_AND_MEAN again. **No game EXE was produced or run.**

The original string at005d6e84 is24 bytes including newline/NUL. `logging-literal.json`
pins the original PUSH/CALL sites and the one canonical source correction. The
fresh `application_main.obj` contains those exact bytes. The logging bridge
continues forwarding its input unchanged.

`build-002.json` pins380 source/dependency inputs before and after the build.
Configuration passed. Build001 stopped at the build-system check without useful
diagnostics; the separately approved build002 completed compilation outside the
sandbox in9.136 seconds. Both receipts/logs are retained. An earlier graph lookup
was corrected before any build invocation: the excluded game target must be
resolved directly, since ALL_BUILD intentionally omits it.

Independent `audit-v2-startup-followup-293.py` verifies512 getter cases,112 lock
cases, exact native oracle bytes, the two precise canonical extent changes,
four original HIGHLOW sites, compiled newline, source immutability and the actual
269/305 diagnostics. It performs no recompilation or native rerun. Historical
26-slot source-pin reports describe their parent revision;292 supplies the new
storage proof. Raw187's void-return getter is excluded from this source build.

```powershell
py -3 scripts/research/audit-v2-startup-followup-293.py
```

Do not rerun completed producer attempt names. New changes require a new captured
build attempt through `build-v2-game-entry-293.py`. The next connected frame work
is00628960 storage/initialization plus remaining callees00423840 (67B),00476170
(169B),00482e50 (69B). Their algorithms/providers remain explicit boundaries.
Original startup state, rendering/resources/input and complete gameplay still
require recovery and original comparison; source compilation is not game acceptance.

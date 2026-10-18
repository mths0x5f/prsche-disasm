# Run289: connect logging and frame traversal to game entry

An actual normal-entry link reuses the five cached game libraries and adds one
new archive containing exactly four game objects: the Run287 logging bridge,
the unchanged175 stdio object (eight original bodies plus its buffer cells),
and the two new Run290 frame-service objects. No fixture provider, guessed
implementation, forced unresolved symbol or original executable code is linked.

Compared with Run285, two real `app_main` edges are now implemented:
`application_main_log` and `application_main_function_00471b60`. The latter
reaches original `00487e20`, exposing four callee contracts and one global
storage contract. Thus the observed frontier changes **267→270 names** and
**303→306 references**; direct unresolved `app_main` services decrease20→18.
There are no other linker errors. **No game EXE was produced or executed.**
This is connected source recovery, not a percentage estimate for the game.

[The link](logging-frame-001.json) and [integration manifest](logging-frame-001-integration.json)
pin the actual archive, object identities, commands, logs and receipts. The
independent audit passes22 merged input pins, verifies12 unique public symbol
definitions across the four objects, excludes fixture/global providers, checks
the actual270/306 diagnostics, and records the two removed/five exposed names.
The added library is searched normally; WHOLEARCHIVE, NOENTRY, custom ENTRY and
FORCE are absent. This step compiles nothing: one archive plus one link only.

Run287 passed224 native cases. Run290 passed six original/native cases and98
original PE bytes. Those bounded fixtures do not prove the real four frame
callees, global00628960, or full output/runtime composition. In its original
oracle, `004898f0` executes its actual PE body; the other three frame callees
are controlled cutpoints. Its pointer return is the next connected packet291.
The lock-prefix48 requirement and original logging newline remain open in the
validation backlog. Startup constructors, resources, rendering, input and real
gameplay still need original comparison.

The standalone CMake entry builds reviewed sources and then the existing
Run102 game target. Configuration succeeded as MSVC Win32 in
`local/builds/v2/game-startup-link-289`; a complete fresh CMake build was not
run at this checkpoint. Cached linking is explicitly separate from that build.

```powershell
py -3 scripts/research/audit-v2-game-entry-289.py
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/289-game-startup-link -B local/builds/v2/game-startup-link-289 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/game-startup-link-289 --config Release --target porsche_original_game_link --parallel 4
```

Do not rerun a completed integration attempt name. Exact object inputs for the
captured no-compile attempt are in its archive receipt. New reviewed objects
require a new attempt and pinned proof packets. Run274's whole candidate archive
is not a dependency of this game link; in particular old187's void-return getter
must not silently compete with its correctly typed291 replacement.

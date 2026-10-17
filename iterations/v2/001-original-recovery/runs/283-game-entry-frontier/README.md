# Run283 — normal game-entry link frontier

Existing target: `porsche_original_game_link`, defined in
`runs/102-original-game-link/CMakeLists.txt`, using `host-entry.cpp`. It is already
an entry-driven `WIN32 EXCLUDE_FROM_ALL` target, without WHOLEARCHIVE/NOENTRY or
an explicit /ENTRY override. The actual cached COFF chain is:

`_WinMain@16` → `?win_main_004b6710@porsche@@YGHPAX0PADH@Z` →
`?app_main_004b6a50@porsche@@YAHHPAPAD@Z`.

The five canonical libraries are porsche_original, porsche_recovered_links,
porsche_window_links, win32_window_bindings and porsche_platform_win32, plus SDK
imports/default MSVC runtime libraries. Actual cached project references contain
146 compile roots; this is build closure, not proof all archive members load.
The frozen Run173 actual entry-link result is267 unresolved names /303 references
across58 diagnostic archive members, including20 unresolved contracts directly
from app_main. This is the relevant historical entry frontier. Run274's414 names
come from a different NOENTRY/WHOLEARCHIVE diagnostic and are not launch blockers
for this entry root. That candidate archive contains none of the original entry,
WinMain or app_main VAs and cannot replace the missing entry chain by itself.

Most recent compatible cached five-library set remains the Run173-used
`local/builds/v2/original-game-link-098/common/...` set. Their member counts are
134/1/1/1/8. Four are newest by mtime among19 matching libraries; only window
bindings has a newer same-sized1-member variant under original-game-link-102.
Its semantic equivalence is not claimed. The complete SHA/mtime/size/member
comparison is in summary.json. All283 Run173 source pins still match current
files, but this does not turn the cached476-function production build into the
current1125-candidate raw archive. Cached .map is empty; no game EXE exists there.

The unexecuted proposal at
`local/experiments/v2-game-entry-frontier-283/entry-link-proposal.rsp` uses those
actual five Release project dependencies, verified host-entry.obj and VC/SDK x86
library paths. It preserves normal CRT entry selection and adds explicit
OPT:REF/ICF, VERBOSE:LIB and a separate output/map. It is a proposed diagnostic
command, not a captured historical linker invocation; the old link tlog is empty.
The coordinator reused its pinned inputs in Run285 with independently owned
output paths. This Run283 performed no compile/link/native execution, and the
proposal JSON/RSP remain unchanged.

Existing CMake command (not executed here):

```powershell
cmake --build local/builds/v2/original-game-link-098 --target porsche_original_game_link --config Release
```

For a no-compile diagnostic replay, invoke the pinned link.exe with a copy of
the proposal arguments and a new run's OUT/MAP. No full-corpus rebuild is needed
to observe this cached entry frontier. A fresh current source build is a separate
validation step and must not be implied by the replay.

Run284 independently proves the actual original PE entry is005a2d1a, before
004b6710. The host WinMain bypasses its original environment/setup/callback and
constructor sequence. Missing original startup/constructor owners include
005a940c/005a91bf/005a9106/005a2441/005a0f45 and first constructor004035e0.
Modern MSVC CRT provides its own process initialization, not proof of those
original global-state effects/order. A faithful first launch needs these state
contracts, actual entry-reachable implementation/provider closure, resources
and rendering; no fake bootstrap or original-machine-code fallback is supplied.
Exact original CRT evidence is linked/pinned from Run284 rather than duplicated.

Audit command (read-only, refuses completed output):

```powershell
py -3 scripts/research/audit-v2-game-entry-frontier-283.py
```

Validation passes323 pins, actual three-entry COFF identities,7 project files,
five existing library paths, actual recorded267/303 diagnostics, source freshness
and19-library comparison. No source/index/shared plan was edited. Counts are
diagnostic evidence, not a game-execution or playability claim.

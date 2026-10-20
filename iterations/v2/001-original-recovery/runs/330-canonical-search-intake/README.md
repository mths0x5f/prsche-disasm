# Run330 — canonical character-search graph intake

**READY:** add the existing
`source/recovered/Porsche.exe/formatter_search.cpp` once to the game target.
No source/header edits, new aliases, selective body copies or data providers
are needed. Root owns game integration332. This packet makes no game-graph
change and counts zero newly recovered original functions.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first entries are `005a2780` character search, `005a1e10` substring and
`005ae3c0` comparison. Run172 owns all three canonical implementations and
the shared original return tail `005a2770..005a2774`/interior `005a2786` behavior.
Absent registry entries do not erase that canonical ownership. All tracked run
C++ mentions were checked; only the existing327 character-search call appears.
Actual328 game COFF has no definition containing any of these three original
addresses and no native symbol collision with the canonical TU.

## Existing proof reused

Both172 `verification.json` and `production-verification.json` report9374
native/original comparisons:4028 character,1207 substring and4139 comparison
cases. All22 recorded normalized source/header/script/index pins still match
current files. Both saved probe executables match their recorded SHA256 values.
The character body188B, substring128B plus shared5B tail, and comparison208B
body hashes were independently reread from the pinned original PE.

Proof covers all byte characters, alignments0..3, ordered memory reads and
shared entries. The production report removes the private read observer;
native return/state/arena/boundary comparisons remain. Existing327/004 also
links this exact canonical search source in10240 controlled routing cases;
its source and receipt pins still match. Neither172 nor327 native tests were
rerun for this intake.

## Actual current dependency closure

An isolated uninstrumented Win32 compile of the exact canonical TU defines
exactly these symbols:

- `formatter_search_character_005a2780`
- `formatter_search_substring_005a1e10`
- `formatter_search_compare_005ae3c0`

Its six undefined symbols already have unique providers in actual328 game
objects, rather than merely in source files:

- CRT lock/unlock `exit_registry_lock_api_005a4ba4` and
  `exit_registry_unlock_api_005a4c05`: existing `formatter_crt_runtime.obj`,
  built from `source/recovered/Porsche.exe/formatter_crt_runtime.cpp`.
- Locale/writer/readers `006afd80`, `006c02e4`, `006c02e8` and lowercase
  `formatter_text_lower_inner_005a22b7`: existing `formatter_text.obj`, built
  from `source/recovered/Porsche.exe/formatter_text.cpp`.

The new object has no trace-hook, common-storage or weak-symbol dependency.
Every actual328 object, the build receipt/log, current source closure and
isolated compile are pinned in `summary.json`; actual provider COFF tables and
paths are retained there. The first isolated compile omitted the SDK UCRT
include path and failed at `malloc.h`; its failed log/receipt is preserved in
the local330 directory. The corrected compile passes without changing source.
System headers were observed and hashed after this inspection compile; this
compile is COFF readiness evidence, not a replacement native behavior proof.

## Integration recommendation and limits

Prefer one `target_sources(... formatter_search.cpp)` addition using the
existing canonical file. Expected search-only delta over328: source count+1,
one unresolved name/reference closes, zero new names. The closing symbol is
`?formatter_search_character_005a2780@porsche@@YAPBDPBDH@Z`, currently demanded
by `file_device_name_00568e90` in `resource_device_327.obj`. Root332 must verify
the actual complete-build frontier delta alongside the other packets.

An archive, `/Gy` function selection or COFF extraction is unnecessary.
Standalone327 lacked the surrounding production closure and its direct
`/Gy /OPT:REF` link still required the six unrelated names. Game328 already
has their canonical providers. Do not carry327's fixture-local zero/fail-fast
locale definitions into production and do not add another formatter-text TU
or fresh locale storage. Existing objects already supply the closure once.

Run236's EOF/table-initializer and general locale-domain concerns remain
recorded. This intake neither changes that storage nor claims to close those
holds; it exposes no new locale provider or native ABI view. The three proven
search bodies retain their existing ownership. Full-game link/startup,
real locale engines, visual acceptance and other recovery holds remain open.
Fresh REA333/001 also confirms `005a2780..005a283b`,188B, on the same original
SHA. Its completed receipt and character-search dossier are pinned in330;
this corroborates the index and does not replace or repeat native proof.

Verification without compilation or native execution:

```powershell
py -3 scripts/research/audit-v2-search-intake-330.py --check
```

The default capture mode refuses an existing330 summary. Local supplementary
probe/optional REA pins are reproducible with
`py -3 local/experiments/v2-search-intake-330/supplement.py`.
No existing source/header/CMake file, completed run or game data was edited.

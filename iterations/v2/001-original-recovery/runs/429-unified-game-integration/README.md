# Run 429: one game graph on upstream's chain

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Until now the game build ran as two chains that only shared Run 298:
- **upstream:** 298 → 306 → 309 → 310 → 314 → 318 → 321;
- **fork:** 298 → 417 → 418/419 → 420 → 424 → 426 → 428.

The upstream review of PR 19 rejected the fork chain as a whole: it was built on 298 (so it
lost 305/307), and it carried storage and bridge defects. This run wraps Run 321 and
re-applies the fork's work as explicit source lists. Every defect named in that review is
either fixed here or kept out of the graph.

## What is in the graph

| Added on top of 321 | Source |
| --- | --- |
| 19 Run 400 bodies not already integrated by upstream Run 310 | `runs/400-frame-loop-clusters/*.cpp` |
| `00413ea0`, corrected | `frame_clock_00413ea0_429.cpp` |
| `00471b70`/`00471c40` frame root lifecycle, corrected | `frame_root_lifecycle_429.cpp` |
| Frame root storage `00628940..00628a64` | `frame_root_block_429.asm` |
| Audio backend, channel lookup and voice stop | Runs 421, 422, 425 |
| Audio module state block `006b00c0..006b4a44` | Run 427 |
| Input Win32 adapters and caps buffer | Run 424, canonical `input_state.cpp` |
| Proven aliases only | `entry_bridges_429.cpp` |

## Fixes for the PR 19 review

- **00628960 and the 8-versus-4 gap (item 1).**
  - The root cell is still one symbol.
  - The storage is now one MASM block with the original offsets: name at `+0`, root at
    `+32`, path at `+36`. The old `pfroot` C++ section put the path 8 bytes after the
    root, and a 40-character track name now reaches the root and the path as in the
    original.
  - The block also shows that the path is not a 256-byte object in the original:
    `006289e4..00628a20` are cells of unrecovered code.
- **Zero-filled heap providers (item 2).** Gone: the 420 bridges are not in the graph,
  and `0059eb20`'s dependencies stay unresolved as in upstream.
- **Run 418's arena (item 2).** Out of the graph. Its `arena_slot` splits
  `006af3b4..006af3f4` across separate canonical cells, so index 16 does not reach the
  `006af3f4` guard. Fixing it means turning upstream's canonical cells into one block,
  which is its own change.
- **Wrong UI bridges (item 4).** Gone: no free-cdecl stand-in for a thiscall method
  remains. Run 411's TU, with the packet layout and zeroed immediates of items 5–6, is
  out of the graph.
- **`00413ea0` cached index (PR 4).**
  - The corrected copy re-reads `005e8bfc` after each `00413960` call (`00413f29`).
  - It uses the canonical `global_005e99f4`/`global_006573e8` instead of new names for
    the same cells.
- **More defects found in Run 419 against the original**, fixed in the corrected copy:
  - an invented null check on `[00628bc0]`;
  - the missing x87 pop (`fstp st(0)` at `00471c2b`) after `005323a0`;
  - an error format truncated to `"ERROR - Couldn't load track: '"`, where the original
    passes `"...'%s'\n"`.

  Run 419's callees with a canonical owner (`0059ef90`, `0059f050`, `005a0fbf`,
  `005a177b`, `005e8e50`) use it, instead of new C names.

## Left out (explicit boundaries)

- **Runs 404/405/407/408/409.** These TUs define second owners of VAs that already have a
  canonical ABI, such as `application_main_function_005a177b(uint, uint)` next to the
  canonical `formatter_stdio_printf_005a177b(const char*, ...)`. They correspond to the
  items upstream queued from PRs 6/10/11/14/15, and they come back one at a time.
- **Run 418 and Run 411**, as above.
- **Sources upstream already owns** (Runs 310–313): `00412030`, `00425780`,
  `004a54b0`/`004a54e0`, `0053c290`, resource open.

## Validation

```
py -3 scripts/research/experiment-v2-frame-clock-429.py
py -3 scripts/research/experiment-v2-frame-root-429.py
py -3 scripts/research/build-v2-game-link-429.py --phase configure --attempt <id>
py -3 scripts/research/build-v2-game-link-429.py --phase build --attempt <id>
```

The fixture templates are versioned without game bytes. The scripts read the original
bodies, their operand sites and the referenced string literals from the PE at build time.
- **`00413ea0`:** 9/9 cases equal the original 296 bytes, with 31 operand sites. Two cases
  have the dispatch shrink or grow the count. Run 401's uncorrected source fails them, so
  they detect the cached count. Result in `frame-clock-validation.json`.
- **Frame root:** 9/9 checks against the original 198 + 65 bytes (30 sites), with the real
  block linked:
  - layout `+32`/`+36`;
  - load ok, load failure and allocation failure;
  - 31- and 40-character names;
  - teardown with and without a root.

  Each case compares the call trace (strings by content), the whole block, ABI registers
  and the x87 TOP. Two mutations fail: a `void` `005323a0` (no pop) and the truncated
  format. Result in `frame-root-validation.json`.

## Build

| | Sources | Unresolved names | References |
| --- | --- | --- | --- |
| upstream Run 321 | 166 | 266 | 295 |
| **Run 429** | 192 | 300 | 332 |

- **Errors:** 0 compiler errors and 0 other linker errors.
- **Why the frontier is wider:** the graph holds 26 more TUs, and the `00471b70` alias
  pulls in the frame root's unrecovered callees: `FrameServiceObjectProxy`, `0059fd90`,
  `005323a0` and three data cells.
- **Build attempts:**
  - `build-001.json` is the first union, with no bridges and Runs 404–409/418 still in it
    (317 names, no duplicate definitions).
  - `build-003.json` drops them (299).
  - `build-004.json` adds the proven aliases (300/332).

No EXE yet.

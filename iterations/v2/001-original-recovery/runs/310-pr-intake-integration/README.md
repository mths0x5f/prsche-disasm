# Run310 — selective PR intake in the actual game graph

PR [#3](https://github.com/xfynx/prsche-disasm/pull/3), commit
`29ff619d06682819483d588143f028b18d834cc2`, was merged as immutable Run400 research
sources in merge commit `42813f7`. All21 C++ bodies compiled in one fresh batch;
only **00412030 and00425780** received new native comparisons and entered this
game graph. The other19 bodies remain candidates, not newly accepted game code.
The upstream README/summary/native claims are preserved; the upstream untracked
fixture was unavailable, so this packet supplies an independent reproducible one.

From [#4](https://github.com/xfynx/prsche-disasm/pull/4), commit
`7f4ba1ccc5973fa4e453f7888635282b85ce2302`, only **004a54b0 and004a54e0** were
adapted in [Run311](../311-pr4-shutdown-helpers/README.md). They use canonical
install-path cleanup, network storage and allocation release, with typed external
boundaries for0048ff30 and0059eb20. The whole PR was not merged:401 caches the
entity count instead of reloading005e8bfc at original00413f29 after callback;
402 also defines00471b60, already owned in the game graph by290.

## Original evidence and finite checks

Original `Porsche.exe` SHA-256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries:00412030,00425780,004a54b0,004a54e0 in
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/{functions.jsonl,disassembly.asm}`.
Four original bodies total **275 bytes**. Fixtures relocate only selected original
instructions into private oracle memory; these bytes and fixture providers are
excluded from the actual game sources.

- Run310 native002:21 C++ sources compile, zero compiler warnings/errors;
  five differential cases/18 assertions for226 original bytes. Cases exercise
  disabled/enabled control release, mutation of005e9410 after the first release,
  virtual callback arguments and mutation of0060c9f4 before notification/next poll.
  Boundaries and selected state are compared; full x86 flags, arbitrary memory
  aliases/faults and all possible virtual consumers are not claimed.
- Run311 native007:five cases/49 original bytes; null/non-null network, cleanup
  changing the pointer before its load, destruction/free changing it after the
  load, final clearing, ECX receiver, ESP/nonvolatile preservation and tail JMP.
  Callee implementations remain outside these comparisons.

## Actual game build

Build002 compiled **161 C++ sources in eight actual projects**, preserving all158
sources from309. Four old top-level contracts closed; **eight genuine data/callee
dependencies were exposed**, leaving **268 unresolved names/304 references**
(309:264/300). There were zero compiler errors and zero other linker errors.
No fake data provider, duplicate00471b60, fixture source or original-byte oracle
was added. MSVC's CRT COMDAT flag is distinguished from original game storage.
**No game EXE was produced or run.**

The source build took4.834s;402 source/dependency pins remained unchanged. The
389-pin immutable manifest is reused with13 delta pins. Batch audit checks source
pins, tool/receipt/object hashes, original bytes, fresh COFF definitions, all161
printed compiler inputs and the exact closed/new frontier sets.

Earlier attempts are preserved: native001 stopped at quoted-header dependency
resolution before compilation; build001 stopped inside the sandbox before any
compiler events and is not a completed game build. The final wrapper explicitly
rejects such an empty capture. Run311 documents its separate failed attempts.

```powershell
py -3 scripts/research/verify-v2-pr3-intake-310.py --attempt 003
py -3 scripts/research/verify-v2-pr4-helpers-311.py --attempt 8
py -3 scripts/research/build-v2-game-entry-310.py --phase configure --attempt 002
py -3 scripts/research/build-v2-game-entry-310.py --phase build --attempt 003
py -3 scripts/research/audit-v2-pr-intake-310.py
```

The first four commands create new attempts; the final audit rechecks the captured
successful native002/007 and build002 without recompiling. A fresh game-build
acceptance must account for compiler output from a fresh target, not assume that
an incremental no-op proves recompilation of every source.

Remaining: original storage/init for005e940c/005e9410/005e9420 and0060c9f4/0060c9c4,
real005338d0/0048ff30/0059eb20 callees, the other Run400 bodies and corrected401.
Root/arena/context HOLD296/301/303 and full-game visual/runtime acceptance remain.
Next bounded candidate: already-merged005338d0 (53B), with original vtable+0x20
ABI, slot bounds and callback mutation checks before its integration.

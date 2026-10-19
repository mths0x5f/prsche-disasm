# Run318 — original scalar fill in the game graph

The sole added production source is [Run317/005b0980.cpp](../317-scalar-fill-backend/005b0980.cpp),
implementing the existing Run312 scalar-fill contract. Original `Porsche.exe`
SHA-256: `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query `005b0980` locates 184 indexed bytes in two ranges; the186-byte raw
oracle includes the original two-byte gap. Source provenance, cdecl callers,
algorithm and native inputs are documented in [317](../317-scalar-fill-backend/README.md).

Run317 attempt002 passed1296 native comparisons/9075 checks:16 alignments,
27 lengths in0..129, three DWORD patterns, every guarded buffer byte, EAX,
ESP and nonvolatile registers. The typed return core and void dispatcher alias
represent one original VA. This coverage does not establish behavior for invalid
pointers or enormous lengths. Original instruction bytes and fixture providers
are excluded from the game graph; no original writable-data provider was added.

Fresh build001 compiled **all164 C++ sources in eight actual projects**, retaining
the entire Run314 graph. One unresolved name closed, with no new dependencies:
`?heap_fill_scalar_005b0980@porsche@@YAXPAXII@Z`. Link frontier is now
**268 names/297 references**, versus269/298 in314. Compiler and other linker
errors: zero. **No EXE or game execution.** The new COFF object defines only the
scalar contract and typed core, with no undefined symbols.

Build time:7.02s. All412 source/dependency pins remained unchanged; the389-pin
shared base is reused with23 delta pins. A read-only batch audit verifies native
inputs/tools/libraries/logs/objects/EXE, original PE bytes, all164 fresh compiler
events, source closure, COFF definitions and exact frontier difference. It hashes
each shared input once; it does not rerun successful native fixtures.

```powershell
py -3 scripts/research/audit-v2-scalar-fill-integration-318.py
```

For a fresh build use unique attempt IDs:

```powershell
py -3 scripts/research/build-v2-game-entry-318.py --phase configure --attempt 002
py -3 scripts/research/build-v2-game-entry-318.py --phase build --attempt 002
```

Remaining: original MMX005b0a40 and SSE005b0b00 memory writes/state behavior,
low-level resource-open dependencies, root/arena/context296/301/303 holds,
full-game linking/startup/render/gameplay. REA316 provides analysis evidence;
it does not replace native acceptance. PR closeout and deferred candidates remain
in `docs/research/pr-triage-2026-10-19.md` and `docs/recovery-validation-backlog.md`.

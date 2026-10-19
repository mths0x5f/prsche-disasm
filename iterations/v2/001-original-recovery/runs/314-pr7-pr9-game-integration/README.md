# Run314 — selective PR7/PR9 game integration

Two original functions were adapted from PR7 `a349d056a0dc981b770e34121c5d2b5476295393`
and PR9 `223580ab7ee93c7decb14d2be09ee10367afdbfc`. Whole PRs were not merged:
their other functions already have owners. The installed bodies are
[312/0053c290](../312-pr7-fill-dispatch/README.md),77B, and
[313/0059d8e0](../313-pr9-resource-open/README.md),206B. Original module is
`Porsche.exe`, SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`;
index queries/calls, exact bytes, sources and receipts are recorded in312/313.

312 passed28 native cases/211 checks: feature-branch precedence, cdecl arguments
and MMX EMMS/x87 tag behavior. The original three fill backends remain unresolved;
no host memset was substituted.313 passed9 native cases: disabled roots, primary
and fallback hits, failure callback, null callback and callback/path mutation.
It reuses canonical file globals and formatter and supplies both existing
pointer-returning resource-open aliases. Its low-level open/exists callees remain
explicit boundaries. No new original writable-data provider was created.

Build001 compiled all **163 C++ sources in eight actual projects**, retaining
all161 from310. Three old contracts closed; four real dependencies opened:
`005b0b00`, `005b0a40`, `005b0980`, and pointer-returning `00561ca0`.
Frontier: **269 unresolved names/298 references**, versus310's268/304.
Zero compiler errors and zero other linker errors. **No EXE or game execution.**
The original-byte oracles and fixture providers are absent from the game graph.
The only extra readonly COFF COMDAT is the proven original `%s%s` literal005cc588.

The fresh source build took5.755s. All408 source/dependency pins stayed unchanged;
the389-pin shared base is reused with19 delta pins. The read-only batch audit
checks original PE, both standalone native receipts/inputs/tools, all163 compiler
inputs, fresh COFF definitions and the exact closed/new frontier differences.
It shares one proof cache across the two native packets and game-source pins.

```powershell
py -3 scripts/research/audit-v2-pr7-pr9-integration-314.py
```

The two packet READMEs contain commands for fresh native attempts. The game build
driver is `scripts/research/build-v2-game-entry-314.py`, with configure/build
phases and unique attempt IDs; completed receipts are never overwritten.

Remaining: real fill-backend memory writes, low-level file open/exists behavior,
their stateful composition, full-game link/startup/render/gameplay, root/arena/
context holds296/301/303. Next connected candidates are the three original fill
backends, beginning with scalar005b0980; inspect existing owners before recovery.
The earlier005338d0 callback/slot task remains in the validation backlog.

# 242 — one scalar cell, two native integer views

One writable physical int32 cell at original identity `0060c95c:4` supplies both current signed/unsigned native views. Original `Porsche.exe` SHA256: `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. No new game function, algorithm, second cell, canonical source edit, production or union change.

Preflight independently checked all **125** HIGHLOW target sites against exact indexed PE instructions: **122 reads / 3 writes**, all direct absolute MEM4 MOV operations. No unindexed target, address-taking/nonscalar instruction, interior target, in-cell relocation or current cross-VA overlapping view was found. Original `.data` is readable/writable/non-executable; the cell is beyond initialized raw bytes but inside virtual extent, so its original loader initial bits are zero. This is virtual-zero-fill evidence, not a claim of four literal zero file bytes. Four actual cached consumer COFFs require `?DAT_0060c95c@@3HA` and `?DAT_0060c95c@@3IA`; both metadata variants name exactly the same four-byte span. Live canonical/WIP source scan found no match. See `preflight.json` for exact sites, instructions, consumer objects and exclusions.

`summary.json` has collector kind `original-writable-data`, support id `shared-scalar-cell-0060c95c-242`. Its actual i386 object defines only signed symbol `?DAT_0060c95c@@3HA` in writable `.ogw$sv`, four zero initial bytes, no code/undefineds/relocations. SHA256: `d174e99731b35ee6b4ce1d70f0e2ff74d7056093bd094ac57ba40c53815370d6`.

Separate `binding-summary.json` has kind `proven-link-contract`, support id `signed-unsigned-cell-binding-0060c95c-242`. Actual COFF `.drectve` contains precisely:

```text
/alternatename:?DAT_0060c95c@@3IA=?DAT_0060c95c@@3HA
```

Alias object SHA256: `4a3422287313630048512c8d7f74d1ee5bb50e35ba265d80652018c039656207`. It has no external definitions/undefineds, writable/executable payload or relocations; compiler `.debug$S` / `.chks64` metadata is retained. The binding supplies no storage. Both summaries must be supplied separately to the support collector; together they are **two support objects, one physical cell, one exact alias, zero functions**. No relative-layout or absolute-native-address mapping is claimed.

One `/MP6` batch compiled five TUs: cell, alias, independent signed/unsigned fixture boundaries, fixture main. Actual measured compiler exit0, **1.636858 s**, no diagnostics; private link exit0 (0.351363 s), native fixture exit0 (0.026140 s). Each receipt was saved before attribution. The first postcompile check rejected harmless compiler metadata sections; original driver, original prepare/compile receipt and attribution-failure note are preserved under `local/experiments/v2-shared-scalar-views-242`. Finalization validated the same captured command/source inputs and reused all five COFFs. **No second compiler batch** was run; game C++ sources were unchanged.

Separate-TU native calls prove zero initial bits and address identity, then write/read both directions using six patterns (`0`, `1`, `7fffffff`, `80000000`, `80000001`, `ffffffff`) and restore zero. Signed fixtures use explicit corresponding positive/negative int values, not an inferred pointee type. Actual fixture PE contains exactly four virtual `.ogw` bytes with read/write permissions and no relocation in the cell. Fixture/object hashes were saved before native execution. Fixture SHA256: `2ef30f052ead449e4834a4ea951320bc752c32ee763dd9db634d9e087957098a`.

45 input pins passed mutation guards. `audit.py` independently rereads PE/COFF bytes, all125 references/relocation targets, actual directive, both summary hashes, fixture hashes and durable receipts; `audit.json` records PASS. It does not recompile, relink or rerun the fixture.

```powershell
py -3 scripts/research/audit-v2-shared-scalar-views-242.py
py -3 scripts/research/experiment-v2-shared-scalar-views-242.py
# Captured run finalized after the metadata-only audit correction:
py -3 scripts/research/experiment-v2-shared-scalar-views-242.py --finalize-existing
# Read-only audit of the finished packet:
py -3 iterations/v2/001-original-recovery/runs/242-shared-scalar-views/audit.py
```

These are current direct integer views only. Global meaning, whole-program computed pointers/aliases, surrounding layout, loader-time changes, lifetime and game behavior remain deferred. No broader signed/unsigned alias rule or generic data allocation is introduced.

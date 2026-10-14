# Run 192 — scalar-slice native COFF

Run189 added one syntax-pass translation unit, VA `00553a70`, to the 923
candidate Run188 set. The Run192 incremental build reused all 923 matching
Run188 objects and compiled that new TU into a valid x86 COFF object. The single
`/MP6` batch succeeded, with zero fallbacks and zero code-generation failures.
Elapsed time was 2.732 seconds.

The new object's SHA-256 is
`3db42dae24fcd89b849c44f60c3ca5d52c62e8adaeef02ccfaf19f29fd0b5667`.
Its defined function symbol is `?FUN_00553a70@@YAPAMPAM0M@Z`; it also refers
to `__allshl`, `__aullshr`, and `__fltused`. The 924-object archive is
1,042,768 bytes. It reports 384 unresolved symbol names across 750 references.
These are compile and archive results, not a game executable or behavioral
acceptance.

The frozen Run189 owner audit recorded SHA-256
`1206eb99f84a2999a948e17b0945b7c5fb5ff5a872b4293d8984ee1eadb2f1db` and
verified source/helper/header guards. Run192 rechecked the audit, selected
sources and headers, the Run188 prior closure and compiler/tool pins during the
build. Compiler binary SHA matched Run188's current pin; historical Run178/181
compiler binary identity remains unproven because those runs did not record it.

```powershell
py -3 scripts/research/build-v2-corpus-batch-188.py --audit local/experiments/v2-scalar-slices-189/full/audit.json --prior iterations/v2/001-original-recovery/runs/188-batched-corpus-objects/summary.json --output local/experiments/v2-build-corpus-192 --summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json
```

Full row-level object hashes, symbol tables, cache provenance, input pins,
batch command and log hashes are in `summary.json`. The generated COFF objects,
archive and logs are under `local/experiments/v2-build-corpus-192`.

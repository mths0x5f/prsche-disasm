# Run 188 — batched automatic COFF candidates

The new runner compiles identical forced-header cohorts in up to 64-TU
invocations using MSVC `/MP6`. A nonzero batch exit, missing object, or invalid
x86 COFF member causes the entire batch to be retried individually in a fresh
directory. Cache reuse requires a byte-identical generated TU and header set,
matching source body, compiler binary and code-generation flags, plus a
validated Run185 input and builder-source closure.

The full Run184 audit compiled successfully. Of 923 syntax-pass candidates,
733 objects were reused from Run185 and 190 were newly compiled. All three
64-TU-capacity batches succeeded; there were no individual fallbacks or code
generation failures. The resulting 1,040,376-byte archive reports 384
unresolved symbol names across 747 references. Total elapsed build time was
43.416 seconds.

The 12-TU Run183 mechanism pilot remains in `pilot-reviewed-summary.json`:
12 objects compiled, zero failures, one successful batch, no fallback. It
validates batching and COFF parsing independently of the full Run184 pass.
The Run184 owner verified all 5,772 generated-source hashes and 2,461 header
pins before handing off the frozen audit. The Run188 runner also guarded the
audit, compiler, prior cache closure, selected sources and headers before and
after building.

```powershell
py -3 -m py_compile scripts/research/build-v2-corpus-batch-188.py
py -3 scripts/research/build-v2-corpus-batch-188.py --audit local/experiments/v2-pcode-types-183/prototypes-cpp-0000/audit.json --output local/experiments/v2-build-corpus-188/pilot-reviewed --summary iterations/v2/001-original-recovery/runs/188-batched-corpus-objects/pilot-reviewed-summary.json --limit 12 --disable-cache
py -3 scripts/research/build-v2-corpus-batch-188.py --audit local/experiments/v2-declaration-compat-184/full/audit.json --output local/experiments/v2-build-corpus-188/full --summary iterations/v2/001-original-recovery/runs/188-batched-corpus-objects/summary.json
```

Full counts, batch commands/log hashes, object hashes, symbol tables, reuse
provenance, compiler/input pins and unresolved references are in
`summary.json`; objects and raw logs are under
`local/experiments/v2-build-corpus-188/full`. The archive is syntax/codegen
evidence, not an executable or behavioral acceptance. Run185's current compiler
binary SHA matched; Run178/181 did not record compiler binary SHA, so historical
binary identity remains unproven. No shared source, original game data, or
frozen prior runner was changed.

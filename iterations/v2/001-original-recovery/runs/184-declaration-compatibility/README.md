# Run184 — per-TU global declarations

Compile experiment over the same5772 Porsche.exe pseudo-C bodies; original SHA
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navigation starts at `research/binary-index/README.md`; the declaration evidence
is frozen179 `export/globals.jsonl` and `export/types.jsonl`, including consumer
VAs, native C declarators, type classes, byte lengths, alignment and RAM storage.
No new recovered functions or game behavior are claimed.

Final syntax passes733 ->923 (+190, zero lost); missing-global errors25306
->16818, all error diagnostics61173 ->53108. Error-limited functions63 ->48
remain listed explicitly. The merged5772-row provenance is3312 unchanged183
results,2295 batched checks,153 retained individual failures and12 pilot results.
The accepted batched census used37 compiler invocations, zero fallbacks and
447.129 seconds after candidate selection (437.698 seconds inside compiler
batches). Earlier partial attempts are separate; no overall speedup is claimed.

The184 type vocabulary is deliberately narrow: existing precisely sized scalar
types, pointers to supported types with4-byte x86 layout, fixed arrays, and
typedef chains whose byte width/alignment match their bases. Canonical
`/undefined` and `/float` are absent from179 DataTypeManager iteration but their
complete class/width/alignment metadata is supplied by globals[].type; only
identically matching primitive records seed those paths. The manifest records
every contributing identity. Strings retain the native179 `char name[N]`
declaration and exact exported storage length. Unsupported pointer targets,
function pointers, composite layouts, scoped class identities and non-C++
symbol spellings remain excluded. No pointer32 guess or raw types.h import.

Each TU receives only unambiguous Global-scope, single-RAM-storage declarations
whose consumer list includes that VA and whose exact name occurs in that source.
Native extern declarators are copied unchanged. Every declaration has MSVC x86
`sizeof` and `alignof` assertions against179 metadata. No storage definitions,
address aliases, overlapping-data coalescing, global prototypes, ABI changes or
function stubs are added. All837 conflicting identities remain excluded.
The two unnamed MXCSR register symbols at005b0ecc/005b0fce are explicitly
preserved in `omitted-nonmemory-globals.json`, with original register storage and
type metadata; neither becomes a RAM declaration.

One combined type probe validates4604 supported global identities. Expanded
12-TU pilot: missing-global errors332 ->152, zero new/lost syntax passes. The
pilot therefore establishes declaration/layout compatibility and diagnostic
reduction, not complete function compilation. Full scope is2460 changed TUs,
with3312 byte-identical183 results reused and the12 identical pilot results
preserved. Raw179 input bytes remain pinned, including CRLF/BOM where present.

The full runner uses64-file `/MP6` batches. A12-file mixed pilot (eight failing,
four no-error TUs) reproduces individual compiler diagnostics by source, line,
column, severity, code and message. For comparison only, MSVC's localized
trailing "compiling source file ...VA.cpp" annotation is removed; raw messages
and logs are preserved. Each batch requires every filename exactly once and
unique attribution of every diagnostic. Shared-header, unattributed or incomplete
coverage falls back to individual compilation. Aggregate process exits are
recorded; per-TU batch exit codes are null. No silent success is invented.

An interrupted initial individual run left173 complete compiler logs. Error-
bearing, uniquely owned logs are retained as proven syntax failures with null
exit codes and explicit provenance; no-error logs require the completed batch
check. Their absence of saved individual exit-code sidecars is disclosed. The
first mixed-pilot comparison rejected the added MSVC filename annotation, then
passed with only that annotation normalized. Partial attempts remain local.

```powershell
py -3 scripts/research/experiment-v2-declarations-184.py --jobs 6
py -3 scripts/research/experiment-v2-declarations-184.py --full --jobs 6
```

Full output: `local/experiments/v2-declaration-compat-184/full/audit.json`.
The merged schema retains all5772 rows and183 keys, with actual per-row
`generated_source`, `forced_headers: []`, `compatibility_header` and optional
`declaration_header`/hash. Global header hashes are pin-only metadata, never a
global forced include. Exact inputs, generated source bytes and declarations
are guarded by hashes; logs and headers remain local. Root owns shared plans,
registry, actual-object integration and subsequent storage/ABI acceptance.

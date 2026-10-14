# Run178 — isolated pseudo-C compilation audit

Frozen diagnostic packet. Read-only source: Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`,
research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c (5772 bodies).
Existing ExportRecoveryCorpus emits decompiled function bodies but no complete
type/global/prototype header; generic functions.jsonl signatures are not the
inferred getC signatures. Defined-data records contain type paths, not C
definitions. Agent179 owns read-only full header export and shares paths here.

178 owns only this new run and scripts/research/audit-v2-compile-corpus.py.
Generated sources/logs live in local/experiments/v2-compile-corpus-178.
MSVC Win32 /Zs checks one original body per isolated TU in C/C++ modes, with
VA provenance. Phases: raw, exact-width scalar vocabulary, copied forward
prototypes, and externally exported179 headers. No link/run or source-corpus
mutation. No guessed globals, function stubs or algorithm substitutions.
Extended floats remain opaque10/16-byte storage, so unsupported arithmetic
is recorded rather than silently changed to MSVC's64-bit long double.

Full5772-body censuses completed with MSVC19.44 x86, six compiler processes.
Exact-width scalar scaffolding in C:1151 syntax-pass/4621 fail,83.462 seconds.
Of those1151 passes,665 retain implicit-function C4013 warnings;486 avoid that
specific issue. Copied forward prototypes with scalar scaffolding in C++:
707 syntax-pass/5065 fail,93.485 seconds. These are different compatibility
phases, not a controlled one-change language comparison.

C++ diagnostics include25301 missing-global/address symbols,11794 prototype/
call conflicts,3801 thiscall/this diagnostics and691 p-code helper diagnostics.
Counts are observed diagnostics (65 functions hit compiler error limits), not
unique root causes. Full per-body compiler logs/results remain under local;
summary.json preserves aggregate counts, examples, pass/error-limit VAs,
input report hashes and source SHA pins.

Corpus-wide lexical findings:329 functions use extended floats,257 p-code
helpers,155 partial scalar field accesses,172 hidden register/stack values,
770 overlapping-global warnings. Existing exporter omits header declarations;
179 investigates that large mechanical opportunity. Free-standing __thiscall
requires explicit ABI-preserving lowering; prototypes conflict across some
callers/callees; x87 precision and overlapping storage require real models.
No arbitrary return or float10-to-double substitution was introduced.

```powershell
py -3 scripts/research/audit-v2-compile-corpus.py --phase primitives --language c
py -3 scripts/research/audit-v2-compile-corpus.py --phase prototypes --language cpp
py -3 scripts/research/report-v2-compile-corpus.py --audit local/experiments/v2-compile-corpus-178/primitives-c-0000/audit.json --audit local/experiments/v2-compile-corpus-178/prototypes-cpp-0000/audit.json --output iterations/v2/001-original-recovery/runs/178-compile-corpus/summary.json
```

The raw-C first30-body sample produced0 passes; samples and an optional full
raw census remain local exploratory artifacts, outside this frozen acceptance
summary. Header179 and bulk-compatibility180 experiments are subsequent work.
Syntax success is separate from linking and semantic validation; the existing
validation backlog is preserved. Root owns shared documents and integration.

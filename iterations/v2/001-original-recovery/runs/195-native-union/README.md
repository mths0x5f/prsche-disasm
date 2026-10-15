# Run195 — frozen native candidate union and diagnostic link

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first inputs are the original address catalog, Run179 inferred functions
and globals, canonical recovered-function registry, and frozen Run192/190
source/header/object records. No original data, analysis project, recovered
source or registry is changed.

The 924 ordinary Run192 COFF objects and 130 compiled Run190 thiscall leaves
have disjoint VAs: **1054 real x86 objects, zero new compilations**. SHA guards
cover all recorded input closures, selected generated sources, actual quoted
include closures, object bytes, compiler/tool binaries and eligible x86 platform
libraries. All 6437 unique pins pass before and after finalization. Symbols
are independently reread with `build-v2-compile-corpus.py::coff_symbols` and
equal their frozen records. Three repeated compiler constants have identical
section bytes and select-any COMDAT selection2; there are no duplicate ordinary
definitions.

The actual `lib.exe` archive is 1,191,546 bytes, SHA256
`91daba1a74c4d612df27da63aec7714439f2c1ad8ec619175f8691d56b8968b5`.
Its raw COFF frontier is **387 symbol names / 763 object references**:
145 `FUN_` names, 225 data names, 17 other names. References mean distinct
referring objects, not source CALL counts.

An actual diagnostic `link.exe /DLL /NOENTRY /WHOLEARCHIVE` uses explicit x86
VC14.44.35207 and SDK10.0.26100.0 UCRT/UM search paths, with libcmt,
libvcruntime, libucrt and kernel32 libraries. `/VERBOSE:LIB` preserves searches
including implicit OLDNAMES/uuid. LNK1120 reports **377 unresolved names**;
LNK2001/2019 supply 564 diagnostic occurrences. Ten machine CRT helper names
resolve through the platform libraries, and no additional unresolved names
come from the extracted CRT closure. The 763 raw object references and 564
linker diagnostic occurrences are different measures. No DLL or EXE is emitted.

The 145 unresolved function VAs have no body in this candidate union:
36 already have canonical recovered owners outside the union, and 109 have
neither a compiled union body nor a canonical owner. There are zero unresolved
`FUN_` names whose VA is already compiled under a different symbol in this set.
Every frontier row retains the exact symbol, referring objects, original
catalog entry, inferred179 signature, and canonical owner where present.

All 225 data names exactly match their Run179 HighSymbol names and have one
observed type/storage variant in that export. Their original PE sections and
initial file bytes are retained; 13 lie in nonwritable sections. These facts
do not establish native storage ownership or permit allocating globals from
inferred types. Native definitions, alias/overlap treatment and initialization
remain open.

Seven printed CRT names remain unresolved:
`?__amsg_exit@@YAXH@Z`, `?__cintrindisp2@@YAXXZ`, `?__ftol@@YA_JXZ`,
`?__local_unwind2@@YAXHH@Z`, `?__nh_malloc@@YAPAXIH@Z`, `?_rand@@YAHXZ`,
`?_strncpy@@YAPADPAD0I@Z`. Their decorated source contracts need original
consumer evidence; this experiment adds no bridges, stubs or renamed calls.

Commands used for the final capture and parser-only finalization:

```powershell
py -3 scripts/research/audit-v2-native-union-195.py --output local/experiments/v2-native-union-195/final
py -3 scripts/research/audit-v2-native-union-195.py --output local/experiments/v2-native-union-195/final --finalize-existing
```

The second command reuses pinned archive/log bytes and performs zero lib/link
commands. It corrects localized diagnostic parsing to select decorated symbols
rather than parenthesized C argument types. The initial parser report remains
in `final/first-parser-summary.json`; its parsed metrics are superseded by
`summary.json`. Completed-output guards reject overwriting this snapshot.
The earlier incomplete attempt at the experiment root is retained separately.
All new text artifacts use LF before hashing.

`summary.json` contains row-level symbols/provenance and the exact frontier.
Archive, response file and raw normalized tool logs are under
`local/experiments/v2-native-union-195/final`. This is a dependency diagnostic,
not a game target, runtime test, source recovery acceptance or fidelity claim.
Next: recover the missing original bodies and evidence-backed storage/ABI
contracts, then relink a fresh changed-object union. Existing canonical owners
must retain ownership when linked into a later graph.

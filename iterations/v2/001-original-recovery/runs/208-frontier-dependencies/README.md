# Run208 — nine newly exposed function dependencies

Frozen diagnostic candidates. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Scope is exactly the nine new function dependencies of206:0041ebf0,
00565cd0,00565e70,00589df0,00589f40,00590250,00590340,00590c60,00590d10.
Index/catalog and179 metadata identify the original bodies. The current189
audit is parsed once and only those nine rows are retained in the local input
extraction. No full corpus compile or Ghidra/oracle execution occurs.

Canonical entries and original catalog/manual body ranges were checked for
exact/interior ownership; recovered-source definitions were checked for WIP
ownership. No implementation overlaps exist.00565cd0's only definition is
`frame_services_boundary_00565cd0` in frame_services_probe.cpp: an event-only
scripted boundary, not the original algorithm. It is recorded separately.

Only exact179 per-consumer global declarations are added through the frozen184
type/layout resolver. Their original storage/type metadata and layout asserts
are retained. Unsupported metadata would remain explicit; none is silently
invented. Existing sources, forward prototypes and forced-include context are
preserved. Every body byte after its `/* VA */` marker is unchanged. No casts,
qualified-call rewrite, algorithm, shared global owner or alias allocation is
introduced. Native ABI/behavior acceptance remains open.

One actual MSVC Win329-TU `/MP6 /Od /Gy /TP /W3` batch produces three fresh
valid i386 COFF objects: **00589df0,00589f40,00590340**. There are six failures
and zero warnings. Observed batch exit2 and measured time2.858542 seconds are
persisted immediately in `native-capture.json`, before diagnostic attribution.
`prepare.json` preserves all pre-batch rows,49 input/include/tool/source pins,
command, response hash and successful pre-compile guard. The post-batch guard
passes; every filename and diagnostic is uniquely attributed.

The remaining failures are exact and unmodified:

-0041ebf0: missing DWORD/string spellings plus caller/type/return conflicts.
-00565cd0: FUN_00590290's printed prototype rejects two arguments.
-00565e70: FUN_00565ea0's printed prototype rejects two arguments.
-00590250: FUN_005901b0 has conflicting function/global views and callable/type errors.
-00590c60/00590d10: generic code-pointer signatures reject arguments.

No guessed signatures or casts are supplied. The three objects have a
standalone raw frontier of6 undefined names/8 object references; precise COFF
symbols are in summary.json. The observed exit2 belongs to the whole batch;
successful individual exits are unknown and stay null. Successful rows carry
actual-COFF/zero-owned-error certification compatible with204. No archive,
union, production change or commit is made.

```powershell
py -3 scripts/research/experiment-v2-frontier-dependencies-208.py
py -3 iterations/v2/001-original-recovery/runs/208-frontier-dependencies/audit.py
```

Fresh-output guards preserve this snapshot. Artifacts are under
`local/experiments/v2-frontier-dependencies-208`. Source/header/RSP/log/JSON
files use LF before SHA. Validation reads preserved inputs/objects/logs and
does not rerun the compiler. The next bounded work is exact original consumer
and CALL/RET evidence for the six failures, especially the two direct callee
prototypes; successful code generation alone is not original-fidelity proof.

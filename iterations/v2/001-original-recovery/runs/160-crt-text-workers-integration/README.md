# Run160: CRT, text and network worker integration

Accepted baseline:386 full C++ functions and6 registered partial consumers.
This checkpoint adds43 full bodies from157 CRT heap/TLS/locks(17),158 text
consumers(11),159 network workers/members(15). Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries, complete VA/body pins, imports and comparison boundaries are
recorded in the three packet READMEs and fresh verification reports here.

Common MSVC Win32 build:144 projects/270 unique TUs,126 comparison/alias
targets,7 native OS fixtures and3 link fixtures. All10 native/link executables
passed. Fresh original-x86 verification:12 reports/14491 comparisons plus4
component-proven composed cases. New packet comparisons:1972 CRT(production
and instrumented runs),8178 text,189 network. Text observes116631 ordered
reads; the CRT trace independently checks5568 ordered memset writes.

Integration found a concrete storage defect:157 originally owned only the
lock-table prefix0..18, but158 accesses lock19 and locale setter005a6895
accesses lock25. Canonical storage now covers the proven26-cell prefix
005e57a8..005e580f,104 bytes, SHA256
`201fb156260657e94de030a839494cc2ea1dde442715ea851578126f2f95dd4b`.
Additional cells are originally null. Initial aliases and lazy/existing/unlock
paths19/25 match original x86. No total table extent is guessed.

Ten native adapters use the original Kernel32 IAT identities: HeapAlloc/Free,
TlsAlloc/GetValue/SetValue, Get/SetLastError, GetCurrentThreadId and
InterlockedIncrement/Decrement. The native fixture tests zero-filled heap
allocation/free, TLS isolation across threads, thread IDs/error preservation,
atomic signed wrap and concurrent increments. This proves these OS adapters,
not live original allocator/TLS startup or the complete game.

Actual game-link:0 compiler errors,279 unresolved symbols/312 references,
0 other diagnostics. There is no game EXE. New bodies expose further callees;
the frontier is not the total remaining function count. Smallblock allocation,
locale engines, signal table005e5ec8, network native vtables and data owners
remain explicit dependencies.131 audio-init and00525ec0 stay isolated.

Acceptance retains the156 optimizations: related function packets, parallel
independent comparisons and refresh, one cached SHA pass per unique file,
and mutation detection. Historical results are immutable. SHA audits do not
replace original differential checks or live/visual acceptance.

Reproduce using a fresh report directory after this checkpoint is committed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1 *> local/reports/v2-common-build-160.log
py -3 scripts/research/verify-v2-formatter-crt-runtime.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_crt_runtime_probe.exe --report-dir iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration/formatter-crt-runtime
py -3 scripts/research/verify-v2-formatter-text.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_text_probe.exe --report-dir iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration/formatter-text
py -3 scripts/research/verify-v2-network-workers-members.py --probe local/builds/v2/001-original-recovery/bin/Release/network_workers_members_probe.exe --report-dir iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration/network-workers-members
py -3 scripts/research/refresh-v2-proofs.py --report-root iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration --update-registry
py -3 scripts/research/verify-v2-native-fixtures.py --report-root iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration
py -3 scripts/research/audit-v2-proofs.py --report iterations/v2/001-original-recovery/runs/160-crt-text-workers-integration/proof-sha-audit.json
```

Next common packet:161 small heap,162 locale engines,163 network groups.
164 recovers network virtual dispatch targets;166 traces formatter output.
See acceptance.json, compile-link-proof.json, proof-sha-audit.json,
original-game-link/link-report.json and docs/recovery-validation-backlog.md.
Full original game behavior is the target, followed by architecture mapping
and the Rust native/web port.

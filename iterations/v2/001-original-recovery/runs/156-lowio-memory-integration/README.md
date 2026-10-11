# Run156 - lowio, exact memory copy and network session integration

Checkpoint after153(311dd1a), original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Accepts13 complete bodies:152 CRT descriptor initialization/lifecycle(7),154
original memory move(1),155 network session teardown/control(5).4394 new packet
cases pass.152 preserves the signed inheritance-count/address distinction,
record flags, error-cell writes, table reloads and lazy locks using canonical138
banks/limit. Detach does not close OS handles.154 implements forward/backward
byte/DWORD sequences rather than host memmove;3215 cases compare130440 ordered
native/original accesses including overlap, self-copy, alignment, EAX/ABI/DF.
155 connects real139/145/148/151 callees, proving initial5d07d0 and zero628c78
storage through original references/writers. Session member492770 and worker
55bfd0 remain explicit boundaries; vtable5b4968/70/78 native relocations remain
in the validation backlog.131 audio init and525ec0 partial are still isolated.

Eight Win32 lowio bindings follow exact IAT identities recorded in152. The new
native fixture checks STARTUPINFOA layout/inheritance fields, three standard
handles, SetHandleCount, pipe/invalid-handle type, recursive critical sections
and cross-thread acquisition. It does not claim full CRT startup, real inherited
process handles, allocator/concurrency parity or game launch. All prior eight
native/link checks also pass.

Acceptance:343 full +6 registered partial functions. ALL_BUILD139 projects /
262 unique TUs;122 comparison/alias targets,6 native OS and3 link fixtures.
12 fresh original-x86 reports cover8546 cases plus4 component-proven composed
cases. Actual game-link:0 compiler errors,282 unresolved symbols/314 references,
0 other diagnostics (153:282/313). No game EXE or full startup/gameplay acceptance.

Acceptance tooling now reads each proof JSON/index once and computes each
unique normalized dependency SHA once per audit. Cache entries reject source
changes during reading/reuse/final checks. Three cache safety and four refresh-plan tests pass. An identical
current corpus/registry inventory before and after the optimization reports equal
counts and takes9.2897s versus2.3805s (3.90x in this local run, not game speed).
The standalone batch SHA audit covers107 current reports/618 unique source
hashes; it does not rerun behavior tests. Refresh automatically preserves the
connected strings, production/wrapper modes and runs the timer/formatter
composite with its three actual component probes. Historical committed results
remain immutable. These changes reduce repeated acceptance work, not fidelity.

Reproduce into a fresh output run for future checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1 *> local/reports/v2-common-build-156.log
py -3 scripts/research/verify-v2-formatter-lowio.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_lowio_probe.exe --report-dir iterations/v2/001-original-recovery/runs/156-lowio-memory-integration/formatter-lowio
py -3 scripts/research/verify-v2-context-move.py --probe local/builds/v2/001-original-recovery/bin/Release/context_move_probe.exe --report-dir iterations/v2/001-original-recovery/runs/156-lowio-memory-integration/context-move
py -3 scripts/research/verify-v2-network-session.py --probe local/builds/v2/001-original-recovery/bin/Release/network_session_probe.exe --report-dir iterations/v2/001-original-recovery/runs/156-lowio-memory-integration/network-session
py -3 scripts/research/verify-v2-native-fixtures.py --report-root iterations/v2/001-original-recovery/runs/156-lowio-memory-integration
py -3 scripts/research/test_v2_proof_cache.py
py -3 scripts/research/refresh-v2-proofs.py --report-root iterations/v2/001-original-recovery/runs/156-lowio-memory-integration --update-registry
py -3 scripts/research/audit-v2-proofs.py --report iterations/v2/001-original-recovery/runs/156-lowio-memory-integration/proof-sha-audit.json
```

See acceptance.json, audit-benchmark.json, proof-sha-audit.json, compile-link-proof,
original-game-link/link-report.json and docs/recovery-validation-backlog.md.
Next parallel packets:157 CRT heap/TLS/locks,158 text/locale and159 network worker
services. Complete original game functionality remains the target; architecture
mapping and Rust native/web follow the recovered and validated C/C++ baseline.

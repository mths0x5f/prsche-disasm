# Run143 - runtime, audio and network integration

Checkpoint after136(ec8c49a). Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Accepts28 complete original bodies:139 allocator/pool/free/tree(7),140 CRT
bootstrap/fatal/error routing(6),141 application audio/network bridges(4),
142 audio lifecycle(4),144 CRT strings/lazy dialog(4),145 network reset/lists(3).
Index queries, caller/ABI checks, original byte hashes, state/effect comparison
and remaining call boundaries are recorded in each packet report and README.

The connected formatter error probe executes real bootstrap/error routing,
strlen, copy/concat/copy_n and lazy dialog bodies. Its94 cases compare whole
message buffers and effect order; MessageBox and OS calls are recording seams.
Exit2490 and decimal/format engines remain explicit boundaries. Production
Win32 wrappers bind GetModuleFileNameA/GetStdHandle/WriteFile/LoadLibraryA/
GetProcAddress by original IAT identity; no live dialog/error OS acceptance yet.
144 separately compares3291 string/dialog cases with exact byte/word/DWORD
read/write widths and order, then repeats against uninstrumented production
code. There is no observer in production string bodies.

Review preserves pooled-free mode and callback reloads, signed audio mode,
network signed half-interval and tick wrap.142 aliases existing656868/9 frame
bytes; only655d40/6568e4 receive new zero-fill owners. The audio source count/
table5e8bfc/5e8c00 extent and shared5e8e50 storage are still unresolved.
131 audio init and partial525ec0 destructor remain isolated, unregistered and
unlinked in the production library; no guessed clamp or EAX normalization.

Acceptance:295 full +6 registered partial functions. ALL_BUILD passes128
projects/243 unique TUs,113 comparison/alias targets,4 native OS and3 link
fixtures. All7 native/link checks pass.17 fresh original-x86 reports cover7928
comparisons plus4 component-proven timer/formatter cases. Unchanged historical
proofs remain pinned in the registry. The actual game target has0 compiler
errors,285 unresolved symbols/314 references and0 other linker diagnostics
(previous136:259/278); newly connected bodies expose further dependencies.
No game EXE or complete startup/menu/gameplay acceptance exists.

Reproduce from repository root, selecting a fresh output run for future checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1 *> local/reports/v2-common-build-143.log
py -3 scripts/research/verify-v2-formatter-bootstrap.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_error_integration_probe.exe --connected-strings --report-dir iterations/v2/001-original-recovery/runs/143-runtime-network-integration/formatter-error-integration
py -3 scripts/research/verify-v2-formatter-strings.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_strings_probe.exe --production-probe local/builds/v2/001-original-recovery/bin/Release/formatter_strings_production_probe.exe --report-dir iterations/v2/001-original-recovery/runs/143-runtime-network-integration/formatter-strings
py -3 scripts/research/verify-v2-native-fixtures.py --report-root iterations/v2/001-original-recovery/runs/143-runtime-network-integration
. ./scripts/tool-env.ps1
py -3 scripts/research/verify-v2-original-game-link.py --build-dir local/builds/v2/original-game-link-098 --report iterations/v2/001-original-recovery/runs/143-runtime-network-integration/original-game-link/link-report.json --log local/reports/v2-original-game-link-143.log
```

See acceptance.json, compile-link-proof.json, corpus-verification.json and
original-game-link/link-report.json. Deferred checks remain in
`docs/recovery-validation-backlog.md`. Next: accept147 float helpers,148 network
services and149 context ranges, then continue context/parser004d3420, network
lifecycle and CRT lowio dependencies. Architecture mapping and Rust follow the
complete recovered and validated C/C++ baseline.

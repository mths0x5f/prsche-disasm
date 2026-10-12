# Run169 — native network tables and formatter output

Accepted baseline:430 full C++ functions and6 registered partial consumers.
Nineteen new bodies:164 network slots(11) and166 formatter output(8).
166 also compares005abf35, already accepted132; it remains a single algorithm
in formatter_cleanup.cpp, exported through its typed header and called directly
by the output probe. It is neither duplicated nor counted as a new recovery.
Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Index queries and full body/data/import pins are in164/166 READMEs and the
fresh reports here. Three missing complete targets were verified against the
original PE and added to manual-functions.jsonl:48ad70..48ae2b(188B,RET12),
48b340..48b3b9(122B,RET12),5a1056..5a105e(9B,fatal25 noreturn; original
unreachable RET retained). Manual index40; catalog36627, Porsche.exe5812.

Four currently recovered constructor/destructor vptr stores now use actual
native addresses of canonical164 table.send slots. Private151/155/159 identity
probes reject raw original table VAs and normalize only the three canonical
native identities. Their private identity tables never dispatch send;164's
separate572-case probe dispatches the real production tables. Preceding COL
words remain three unsized unresolved RTTI owners, with no null replacements
in production. Component evidence is vtable-relocation-proof.json. Remaining
constructors and RTTI consumers are open; short-packet indeterminate tails
are explicitly excluded from byte parity claims.

Formatter output preserves original CRLF chunking/partial-write arithmetic,
bank reloads, error mapping, descriptor allocation and locale reader protocol.
SetFilePointer uses verified IAT005b223c. Native OS checks exercise successful
seek/read, negative offsets, validFFFFFFFF result with error0 and invalid-handle
FFFFFFFF with error6. Other original/OS services retain their canonical owners.

Common MSVC Win32 build:151 projects/284 unique TUs,131 comparison/alias
targets,9 native OS fixtures and3 link fixtures. All12 native/link checks pass.
Twenty-nine fresh original-x86 reports total26409 comparisons, plus4 composed
component-proven cases. SHA audit checks115 current reports and672 unique
dependency hashes with mutation guards. Full-body proof refresh includes the
existing formatter consumers affected by exporting the canonical helper.

Actual game-link:0 compiler errors,274 unresolved symbols/310 references,
0 other diagnostics; no game EXE. Connecting real tables exposes RTTI/lower
transport dependencies, so the frontier increased from273. This is neither
total remaining function count nor complete-game/visual acceptance.
131 audio-init and partial00525ec0 remain isolated. Validation backlog is open.

Optimizations: connected recovery packets, parallel independent checks,
cached once-per-unique-file SHA audit and once-per-original-PE manual indexing.
Measured156 inventory9.2897→2.3805s;165 manual-index audit0.0566→0.0186s.
These are local verification measurements, not an overall recovery speedup.

Reproduce into fresh report paths after committing this checkpoint:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1 *> local/reports/v2-common-build-169.log
py -3 scripts/research/verify-v2-network-vtables.py --probe local/builds/v2/001-original-recovery/bin/Release/network_vtables_probe.exe --report-dir iterations/v2/001-original-recovery/runs/169-vtable-output-integration/network-vtables
py -3 scripts/research/verify-v2-formatter-output.py --probe local/builds/v2/001-original-recovery/bin/Release/formatter_output_probe.exe --report-dir iterations/v2/001-original-recovery/runs/169-vtable-output-integration/formatter-output
py -3 scripts/research/verify-v2-native-fixtures.py --report-root iterations/v2/001-original-recovery/runs/169-vtable-output-integration
py -3 scripts/research/refresh-v2-proofs.py --report-root iterations/v2/001-original-recovery/runs/169-vtable-output-integration --update-registry
py -3 scripts/research/audit-v2-proofs.py --report iterations/v2/001-original-recovery/runs/169-vtable-output-integration/proof-sha-audit.json
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification
```

Next: integrate ready167 float output/168 network transport and170 parse/pack;
171 network constructors and172 next CRT block continue independently. Then
repeat actual game-link and recover startup/004d3420/RTTI owners. Full original
game → architecture map → Rust native/web remains the goal.

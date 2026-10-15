# Run197 — unfinished CALL-free ABI checkpoint

Status: **blocked before Ghidra capture; zero new COFF objects**.
Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

The frozen Run186 RET census was ranked by original size and absence of CALL.
Besides the already isolated Run193 callee, only two local-RET mismatch bodies
are CALL-free: `004930f0` (15 bytes) and `0043f8a0` (86 bytes). `005a1496`
is an external tail JMP with no local RET and is excluded. RET0 cases
`0040fff0`, `005a2eae`, `005aa907` are explicitly excluded from automatic repair.
The complete ranked queue is in `contracts-before-analysis.json`.

Preparation checked all **44 selected original instructions** against the
immutable PE bytes, all local branches and RET sites, and four indexed local
CALL setup/return-consumer snippets. Both selected functions first read incoming
ECX as `MOV EDX,[ECX]`, consume entry stack+4 as a32-bit output-address, leave
stack+8 unread locally, and finish every local path with `RET8` and
`EAX = entry stack+4`. The unused slot remains part of the ABI; it is not deleted.
`CALL0043f876→0043f8a0` followed by `0043f87b MOV EAX,[EAX]`, and
`CALL004914cd→004930f0` followed by `004914d2 MOV EAX,[EAX]`, demonstrate actual
uses of that raw returned output-address. Complete caller high IR and incidental
outgoing volatile-register compatibility remain unverified.

The proposed bounded experiment locks only raw32 ECX/stack+4/stack+8 inputs and
raw32 EAX output, then performs Run186 native method lowering on a copied project.
Semantic types, source classes and lifetimes remain unknown. No production,
registry, original corpus or game data is changed.

Attempt001 created an independent copy, then failed in the Ghidra launcher
before any exporter execution: the sandbox denied the required write to
`C:/Users/steew/AppData/Roaming/ghidra/ghidra_12.1.3_PUBLIC/java_home.save`.
The original project's before/after manifest matches. The attempt is preserved
under `export/attempt-001` and `local/experiments/v2-abi-analysis-197/project-001`.

Attempt002 requested escalation for this exact command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/experiment-v2-abi-leaves-197.ps1 -Attempt 2
```

The tool returned **`aborted by user after 436.0s`** while approval was pending.
No attempt002 directory or after-capture/result file exists. The command is not
automatically retried. A read-only process inventory was unavailable under the
sandbox; this checkpoint relies on the explicit aborted tool status and artifact
inventory, and does not claim a process-level audit.

Next step, after the required infrastructure approval is available: run the
exact fresh Attempt002 command above. The wrapper preserves the failed001
attempt, hashes the whole original project before/after, uses `-noanalysis
-readOnly` on the separate copy, and requires both before/after captures.
Only after capture succeeds, run:

```powershell
py -3 scripts/research/experiment-v2-abi-leaves-197.py --attempt 2
```

The second stage is prepared to verify raw storage/widths and native RET8,
lower the two emitted bodies through Run186's native method mechanism, and
compile only these changed TUs in one `/MP6` batch. Neither this stage nor the
Ghidra corrections have executed. Existing 1070 distinct candidate VAs are
unchanged by197; any proposed increase to1072 must await actual validated COFF.

`checkpoint.json` records the exact status and artifact SHA pins. This checkpoint
is evidence/queue preservation, not a successful ABI correction, native compile
result, accepted function increment or closed iteration.

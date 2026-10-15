# Run197 — two bounded CALL-free ABI corrections and native COFF

Status: **two isolated native candidates compiled**. Attempt002 completed after
the infrastructure approval became available; the earlier blocked checkpoint
is preserved unchanged in `checkpoint.json` and `README-blocked-checkpoint.md`.
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

The initial tool request returned **`aborted by user after 436.0s`** while approval
was pending. This is the exact historical state captured by `checkpoint.json`.
The coordinator subsequently executed the approved fresh Attempt002, which
completed with `ABI197_CAPTURE_COMPLETE original_project_unchanged=True
functions=2 stages=2`. Both before/after captures now exist. No further Ghidra
execution was performed for native compilation.

The wrapper preserves the failed001 attempt, hashes the whole original project
before/after, uses `-noanalysis -readOnly` on the separate copy, and requires
both before/after captures. After the successful capture, native compilation ran:

```powershell
py -3 scripts/research/experiment-v2-abi-leaves-197.py --attempt 2
```

The second stage verifies exact raw database parameter storage/widths, EAX
return storage, RET8 and extra-pop12, then lowers the emitted bodies through
Run186's native method mechanism. Ghidra refines the raw database slots into
pointer32 views in getC. The audit distinguishes those inferred views from the
raw database contract: original32-bit MOV dereferences establish width and
storage, while signed pointee semantics, source types/classes and lifetimes
remain unaccepted inference.

The first actual `/MP6` batch compiled0043f8a0 and rejected004930f0 because getC
assigned an inferred pointer to an undefined4 memory word. The sole source
correction is `reinterpret_cast<undefined4>(puVar1)` at that store, justified by
original004930fa `8910 MOV [EAX],EDX`, the matching HighFunction STORE inputs,
Clang assignment tokens and native pointer/rawword width assertions. No field
or class reinterpretation is introduced. The failed batch and exact driver
remain under `native-002/first-*`;0043f8a0's unchanged source/object are reused.
One further `/MP6` batch compiles only changed004930f0.

Both final objects have no undefined/common/weak symbols or text relocations.
Native RET8 retains the locally unused entry stack+8 slot.004930f0's complete
15-byte text equals the original bytes;0043f8a0's text differs, so full original
execution/state equivalence remains open. No native execution/oracle suite,
caller lowering, game linking or accepted-function increment is claimed.

`summary.json` records both valid COFF objects, batch/reuse provenance and input
guards before/after. Its result rows and compiler/input closure are compatible
with Run198's repeatable `--thiscall-summary` input. The two VAs are disjoint
from the frozen1070-candidate Run198 set, giving1072 distinct VAs when combined;
this run itself does not relink that union.

`historical-artifacts.json` maps changed historical paths to byte-preserved
artifacts, including the pre-capture driver and blocked README. It preserves
the old checkpoint identities without presenting the previous blocked status
as current. `validation.json` checks those identities, the final storage and
object/provenance rows, source/hash guards, and disjointness against Run198.
Next: combine197 with the existing union through the198 CLI without recompiling;
complete caller high-IR/native and original execution/state checks remain open.

# Run194 ? bounded printed-global access evidence

Frozen evidence packet:12 aliases/eight functions,26 printed occurrences,21 original instruction records verified against Porsche.exe bytes and independently decoded with Capstone5.0.7. Ten aliases have direct memory access width evidence; one string is address-only and one has no original-reference link. Eight aliases additionally have direct Clang RAM address/width agreement. No native declaration, storage allocation or compile delta was applied; no complete body semantics are accepted.

Original module SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navigation/query: binary-index Porsche.exe; printed `_DAT`/DAT and string names in179/189. Sources and179 inputs are byte-pinned in summary.json. PrintC::pushMismatchSymbol (printc.cc:2135?2152) prepends `_` for a same-address symbol whose formal extent is insufficient. Blind `_DAT`?DAT renaming therefore loses a size mismatch.

The initial LOAD/STORE-only report missed direct RAM varnodes. Actual004851a4 `d81d2c245b00` FCOMP reads four bytes at005b242c: raw Sleigh FLOAT2FLOAT has RAM input005b242c/4, and the Clang token has RAM005b242c/4 with high type float; formal symbol is undefined/1. The separate verify-capture.py now records every exact-address raw RAM input/output, and compares original memory operand width and direction. It preserves initial-report-driver.py and initial-summary.json unchanged; the capture Java and original Python driver remain unchanged.

Twenty memory instruction records agree on width. Three FSTP instructions at00485d0f/00485d5d/00485da7 have an independent direction discrepancy: Sleigh FLOAT2FLOAT RAM output is a write while Capstone reports read. This remains explicit. DAT006b0068 tokens are unique varnodes, and _DAT00655a0c tokens are register varnodes; neither receives a guessed storage link. Seven `_DAT` float consumers plus _DAT005e6664 undefined4 store have direct token RAM/width evidence. Integer COPY store width does not prove signedness. x87 float10 conversion semantics remain unresolved beyond this access evidence.

Strings remain separate:005a0c50's char30 symbol has no captured direct-reference instruction and its token has no varnode;00432b60 only pushes005cd1a0, which proves an address use, not a15-byte memory read. No conflict identity is selected arbitrarily. The00540390 cluster is outside this pilot. Requested196 consumers00485100/00485c50 are present; their remaining body/type errors require separate work.

The historical readiness.json truthfully records the aborted first approval attempt and is superseded by actual summary.json/validation.json. The first approved relative-path launch failed before Java with `Path element starting with . is not permitted`. Root's absolute-path launch completed result.json and all12 cases. Host PowerShell nevertheless returned1 because its Stop preference promoted Java's sun.misc.Unsafe warning to NativeCommandError. There were no API/ERROR/Exception failures; validation checks the actual completion, module SHA, source pins and before/after Program changed flag. Root independently guards all79 original-project files. No Ghidra rerun occurred during reporting.

Verification command on existing capture:

```powershell
py -3 iterations/v2/001-original-recovery/runs/194-global-aliases/verify-capture.py
```

Reproduction of capture (requires the same approved external tool access; do not rerun prepare or overwrite current capture pins):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command ". ./scripts/tool-env.ps1; `$ErrorActionPreference = 'Continue'; & ./local/tools/ghidra_12.1.3_PUBLIC/support/analyzeHeadless.bat 'F:/claude/porsche disasm/local/experiments/binary-index-ghidra' binary-index -process Porsche.exe -noanalysis -readOnly -max-cpu 2 -scriptPath 'F:/claude/porsche disasm/scripts/research/ghidra' -postScript ExportGlobalAliases194.java 'F:/claude/porsche disasm/local/experiments/v2-global-aliases-194/export' 'F:/claude/porsche disasm/local/experiments/v2-global-aliases-194/cases.json' -log 'F:/claude/porsche disasm/local/experiments/v2-global-aliases-194/headless-absolute.log' *> 'F:/claude/porsche disasm/local/experiments/v2-global-aliases-194/headless-absolute-console.log'"
```

The Continue preference above documents warning transport; it did not change the pinned exporter or the already-completed launch.

Next bounded native delta: use the seven proven float4 `_DAT` consumer views in an isolated per-TU header, backed only by extern declarations (no allocations), and preserve the original address/storage identities in metadata. Consume189/184 cache and only changed sources/headers with /MP6; retain float10/body warnings and storage ownership as open. _DAT005e6664 may receive only its existing exact unsigned representation contract after integer-context checks, not signedness inferred from COPY. DAT006b0068 and _DAT00655a0c need an explicit normalized-token producer/consumer-to-storage link before a declaration repair. No fictional next-run script is claimed to exist; the runnable gate is verify-capture.py above.

Next mass export class: mechanically join ClangVariableToken RAM address/extent, HighSymbol extent/offset, high type and exact original instruction raw RAM operands plus Capstone width/direction, once per selected function. Require all occurrences and typed consumers to agree; reject register/unique tokens without a proven chain, mixed interpretations, address-only/string uses, booleans and conflicts. Seven float4 examples establish the mechanism; they do not establish corpus-wide acceptance. `_DAT` static candidates cover757 of1431 printed-gap bodies/1025 tokens; strings330/664 and pointer spellings5/5 give a potential union1046 bodies, not proven coverage. Current189 has5526 `_DAT` C2065 diagnostics in752 bodies. A separate reviewed packet can select those candidate functions in batches and raise the current12-alias export cap; it must not export all5772 or compile unchanged TUs. Address-only string classes need a separate bounds/consumer contract and are not folded into this first mass class.

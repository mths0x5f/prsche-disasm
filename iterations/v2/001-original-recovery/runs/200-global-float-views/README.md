# Run200 ? exact per-consumer float4 extern delta

Seven Run194 aliases in five consumers were added as per-TU `extern float` views. No definitions, allocations, alias coalescing, formal-type replacements or body edits occur. Each new wrapper includes its small new header and the exact frozen generated source; the original source/dependencies are SHA-guarded before and after compilation. Per-row dependency hashes contain the actual include closure; forced_headers is empty. Run194 raw original RAM4/x87 instructions, bytes and token float4 evidence are retained per alias.

One MSVC x86 /c /O2 /MP6 batch took2.027s and produced one new real COFF:00485100. It retains nine C4244 float?undefined4 warnings and unresolved __ftol3, __fltused and extern globals. Native compilation is not original-fidelity proof. No syntax-only second pass or full corpus/oracle/Ghidra rerun was performed. The ordinary189 pass count stays924; the frozen196 146 objects remain reusable, with one additional leaf object available here. Root owns union integration; this packet does not rebuild cached objects or claim a new final union.

Results:00401060 ordinary has23 errors (__thiscall/prototype plus remaining globals);00405a90 leaf has one remaining _DAT005b24a8 error, whose proof in another consumer is deliberately not transferred;00456d70 has eight DAT005ceae4/_DAT005b253c errors;00485c50 has six DAT006b0068 errors, whose unique-varnode/storage and FSTP decoder-direction ambiguities remain open.00485100 compiles with nine warnings.00401000 has no proven float4 case in194 and is unchanged. The seven mappings are00401060:005b23f8;00405a90:005b2480,005b2520;00456d70:005b3e3c;00485100:005b242c,005b24a8;00485c50:005b2680.

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Run194 summary SHA91f1c6dd27131c1e33ffe4d6e7e3b4505b276a9670e95fddcdf4a44e06663216. Original storage ownership, x87 float10 behavior, float?raw integer store semantics and all remaining errors are explicitly unresolved. No production/registry changes.

Commands (compile driver refuses existing output objects to prevent stale-object acceptance):

```powershell
py -3 scripts/research/experiment-v2-global-views-200.py
py -3 iterations/v2/001-original-recovery/runs/200-global-float-views/finalize-metadata.py
```

The second command only narrows conservative dependency guards to exact per-TU include closures, rechecks input SHA guards and finalizes reports; it never invokes the compiler. All new reports/headers/logs are LF before hashing. Summary/validation and local audit hold actual paths, byte hashes, raw diagnostics, compiler response/log and object symbol inventory. Compiler batch exit2 reflects the four explicitly failing TUs; object existence and all diagnostics are uniquely attributed per consumer. Frozen194/196/198 remain unchanged. No scope expansion follows this packet.

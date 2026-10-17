# Run265 — automated original frontier queue (Run245 planner)

Input: `iterations/v2/001-original-recovery/runs/264-heap-release-union/summary.json`; actual archive SHA `2fd9f221a696431ef25839d9c1292967c12353eda80c96c1562e6e9d21577502`. Summary/validation/archive/link-log provenance and before/after source/registry/index pins passed. Reparsed actual link: **419 unresolved names / 581 diagnostics**; 417 research tasks, 22 resolved raw-frontier rows excluded.

The script reuses validated union symbol/closure snapshots and scans canonical/platform C++ definitions; it reads no decompiler corpus and invokes no compiler/linker/native/Ghidra. WIP/probe/interior/duplicate ownership and ABI mismatch remain separate. Ranking schedules proof work; it approves no implementation, data allocation or alias.

Priority classes: compiled_VA_symbol_contract_review=1, accepted_owner_reuse_review=30, canonical_provider_contract_review=9, WIP_exact_definition_review=2, accepted_partial_owner_trace=2, scalar_storage_proof_required=102, original_body_trace_required=85, shared_data_view_trace_required=51, data_layout_trace_required=128, external_native_contract_review=7. Full exact contracts/reference IDs are in `summary.json`; the original frontier is not copied wholesale.

Top bounded review targets:

- 1. `00531f90`: compiled_VA_symbol_contract_review, fanout10, indexed bytes278.
- 2. `005925d0`: accepted_owner_reuse_review, fanout4, indexed bytes57.
- 3. `00568200`: accepted_owner_reuse_review, fanout4, indexed bytes95.
- 4. `005682a0`: accepted_owner_reuse_review, fanout4, indexed bytes236.
- 5. `005a4c05`: accepted_owner_reuse_review, fanout3, indexed bytes21.
- 6. `005a4c05`: canonical_provider_contract_review, fanout3, indexed bytes21.
- 7. `0053c290`: WIP_exact_definition_review, fanout3, indexed bytes77.
- 8. `005a4ba4`: accepted_owner_reuse_review, fanout3, indexed bytes97.

Executed:

```powershell
py -3 scripts/research/plan-v2-link-frontier-245.py --union-summary iterations/v2/001-original-recovery/runs/264-heap-release-union/summary.json --run iterations/v2/001-original-recovery/runs/265-link-frontier-queue --output local/experiments/v2-link-frontier-queue-265
```

Six meaningful parser/owner guards passed (runtime known/unknown/dedup and wrongSHA, duplicate owner VA, unmapped refs, compiled ABI frontier, comments/strings). Optional `--runtime-misses` accepts an identity-pinned entry list, retaining unknown VAs as index gaps. It is only an input parser; game-native execution/miss capture is **not implemented** until an EXE exists. Future batches remain manual proof/implementation tasks; no full x86 translator or game behavior is inferred.

Current holds supersede generic ranking: Run259 proves that the actual raw
005925d0 caller sign-extends AL while the original returns a zero-extended DWORD.
Do not issue an alias until the caller is recovered. The 005a4c05 canonical lock
prefix still covers 26 slots versus original IDs through 47; no bounds workaround
is approved. The ten-consumer 00531f90 binding and existing Win32 provider contracts
are the next bounded connected packet. Synthetic VM/CPU misses are not game misses.

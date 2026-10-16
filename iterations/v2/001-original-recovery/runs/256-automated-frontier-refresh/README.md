# 245 — automated original frontier queue

Input: `iterations/v2/001-original-recovery/runs/249-canonical-and-storage-union/summary.json`; actual archive SHA `46bfafedcd1cd4ea3de665b6a18ed79b53fd63636f81ff4c7f167bf7f85ebb0b`. Summary/validation/archive/link-log provenance and before/after source/registry/index pins passed. Reparsed actual link: **418 unresolved names / 602 diagnostics**; 416 research tasks, 20 resolved raw-frontier rows excluded.

The script reuses validated union symbol/closure snapshots and scans canonical/platform C++ definitions; it reads no decompiler corpus and invokes no compiler/linker/native/Ghidra. WIP/probe/interior/duplicate ownership and ABI mismatch remain separate. Ranking schedules proof work; it approves no implementation, data allocation or alias.

Priority classes: accepted_owner_reuse_review=33, canonical_provider_contract_review=6, WIP_exact_definition_review=2, accepted_partial_owner_trace=2, scalar_storage_proof_required=102, original_body_trace_required=85, shared_data_view_trace_required=51, data_layout_trace_required=128, external_native_contract_review=7. Full exact contracts/reference IDs are in `summary.json`; the original frontier is not copied wholesale.

Top bounded review targets:

- 1. `0059f050`: accepted_owner_reuse_review, fanout24, indexed bytes19.
- 2. `00531f90`: accepted_owner_reuse_review, fanout10, indexed bytes278.
- 3. `005925d0`: accepted_owner_reuse_review, fanout4, indexed bytes57.
- 4. `00568200`: accepted_owner_reuse_review, fanout4, indexed bytes95.
- 5. `005682a0`: accepted_owner_reuse_review, fanout4, indexed bytes236.
- 6. `005a4c05`: accepted_owner_reuse_review, fanout3, indexed bytes21.
- 7. `005a4c05`: canonical_provider_contract_review, fanout3, indexed bytes21.
- 8. `0053c290`: WIP_exact_definition_review, fanout3, indexed bytes77.

Executed:

```powershell
py -3 scripts/research/plan-v2-link-frontier-245.py --union-summary iterations/v2/001-original-recovery/runs/249-canonical-and-storage-union/summary.json --run iterations/v2/001-original-recovery/runs/256-automated-frontier-refresh --output local/experiments/v2-frontier-queue-256
```

Six meaningful parser/owner guards passed (runtime known/unknown/dedup and wrongSHA, duplicate owner VA, unmapped refs, compiled ABI frontier, comments/strings). Optional `--runtime-misses` accepts an identity-pinned entry list, retaining unknown VAs as index gaps. It is only an input parser; game-native execution/miss capture is **not implemented** until an EXE exists. Future batches remain manual proof/implementation tasks; no full x86 translator or game behavior is inferred.

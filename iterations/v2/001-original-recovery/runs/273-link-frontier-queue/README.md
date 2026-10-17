# 245 — automated original frontier queue

Input: `iterations/v2/001-original-recovery/runs/269-native-provider-union/summary.json`; actual archive SHA `5a23b789a8962f524dd48558c28a487bba182c940ad8cca89c1168a43c6cab85`. Summary/validation/archive/link-log provenance and before/after source/registry/index pins passed. Reparsed actual link: **416 unresolved names / 569 diagnostics**; 414 research tasks, 23 resolved raw-frontier rows excluded.

The script reuses validated union symbol/closure snapshots and scans canonical/platform C++ definitions; it reads no decompiler corpus and invokes no compiler/linker/native/Ghidra. WIP/probe/interior/duplicate ownership and ABI mismatch remain separate. Ranking schedules proof work; it approves no implementation, data allocation or alias.

Priority classes: accepted_owner_reuse_review=30, canonical_provider_contract_review=7, WIP_exact_definition_review=2, accepted_partial_owner_trace=2, scalar_storage_proof_required=102, original_body_trace_required=85, shared_data_view_trace_required=51, data_layout_trace_required=128, external_native_contract_review=7. Full exact contracts/reference IDs are in `summary.json`; the original frontier is not copied wholesale.

Top bounded review targets:

- 1. `005925d0`: accepted_owner_reuse_review, fanout4, indexed bytes57.
- 2. `00568200`: accepted_owner_reuse_review, fanout4, indexed bytes95.
- 3. `005682a0`: accepted_owner_reuse_review, fanout4, indexed bytes236.
- 4. `005a4c05`: accepted_owner_reuse_review, fanout3, indexed bytes21.
- 5. `005a4c05`: canonical_provider_contract_review, fanout3, indexed bytes21.
- 6. `0053c290`: WIP_exact_definition_review, fanout3, indexed bytes77.
- 7. `005a4ba4`: accepted_owner_reuse_review, fanout3, indexed bytes97.
- 8. `005a4ba4`: canonical_provider_contract_review, fanout3, indexed bytes97.

Executed:

```powershell
py -3 scripts/research/plan-v2-link-frontier-245.py --union-summary iterations/v2/001-original-recovery/runs/269-native-provider-union/summary.json --run iterations/v2/001-original-recovery/runs/273-link-frontier-queue --output local/experiments/v2-link-frontier-queue-273
```

Six meaningful parser/owner guards passed (runtime known/unknown/dedup and wrongSHA, duplicate owner VA, unmapped refs, compiled ABI frontier, comments/strings). Optional `--runtime-misses` accepts an identity-pinned entry list, retaining unknown VAs as index gaps. It is only an input parser; game-native execution/miss capture is **not implemented** until an EXE exists. Future batches remain manual proof/implementation tasks; no full x86 translator or game behavior is inferred.

Current holds:005925d0 cannot be aliased because Run259 proves actual MOVSX AL
versus original zero-extended EAX.005a4c05 still has a26-slot canonical prefix
versus original lock IDs through47. Generic ranking approves neither change.
Run267/270/271 separate proven64B heap-storage evidence from unproved auxiliary
function entry/liveness; Run272 reviews data-only shared-base composition.
Old corpus/manual index and game algorithms remain unchanged.

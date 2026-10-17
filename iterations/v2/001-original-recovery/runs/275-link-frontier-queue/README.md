# Run275 — automated frontier queue (Run245 planner)

Input: `iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json`; actual archive SHA `6f1969657832218baba120c1adc8009395f30403ac91ce73c4252de362e6eaa8`. Summary/validation/archive/link-log provenance and before/after source/registry/index pins passed. Reparsed actual link: **414 unresolved names / 566 diagnostics**; 412 research tasks, 24 resolved raw-frontier rows excluded.

The script reuses validated union symbol/closure snapshots and scans canonical/platform C++ definitions; it reads no decompiler corpus and invokes no compiler/linker/native/Ghidra. WIP/probe/interior/duplicate ownership and ABI mismatch remain separate. Ranking schedules proof work; it approves no implementation, data allocation or alias.

Priority classes: accepted_owner_reuse_review=30, canonical_provider_contract_review=6, WIP_exact_definition_review=2, accepted_partial_owner_trace=2, scalar_storage_proof_required=101, original_body_trace_required=85, shared_data_view_trace_required=51, data_layout_trace_required=128, external_native_contract_review=7. Full exact contracts/reference IDs are in `summary.json`; the original frontier is not copied wholesale.

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
py -3 scripts/research/plan-v2-link-frontier-245.py --union-summary iterations/v2/001-original-recovery/runs/274-shared-heap-union/summary.json --run iterations/v2/001-original-recovery/runs/275-link-frontier-queue --output local/experiments/v2-link-frontier-queue-275
```

Six meaningful parser/owner guards passed (runtime known/unknown/dedup and wrongSHA, duplicate owner VA, unmapped refs, compiled ABI frontier, comments/strings). Optional `--runtime-misses` accepts an identity-pinned entry list, retaining unknown VAs as index gaps. It is only an input parser; game-native execution/miss capture is **not implemented** until an EXE exists. Future batches remain manual proof/implementation tasks; no full x86 translator or game behavior is inferred.

Explicit holds remain: Run259 proves unsafe595d0 MOVSX AL atactualconsumers;
5a4c05 canonical26slotprefix doesnotcoveroriginalIDs through47.
272/274 provide oneboundedheap-table owner forcurrent maskedindexedconsumers,
not the preceding006b4b20..006b4f1f layout orfour candidatefunction entries.
Nextconnectedreview: files.cpp00568200/005682a0 plus sharedcallers' fullEAXcontract.

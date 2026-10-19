# Run321 — original SIMD fill and complete dispatcher chain

Two production sources were added to the Run318 game graph:
[MMX005b0a40](../319-mmx-fill-backend/README.md),176 indexed bytes, and
[SSE005b0b00](../320-sse-fill-backend/README.md),214 indexed bytes. Both recover
the original DWORD-pattern fill, updated-address alignment peeling, bulk/tail
stores and advanced-pointer EAX result. Their void aliases serve the existing
Run312 dispatcher and do not count as additional recovered original functions.
No writable game-data providers, original-byte oracles or fixture code were
added to production. Provenance is `Porsche.exe`, SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`;
the index query, owner check, REA316 evidence and original callers are in319/320.

Standalone original-PE comparisons passed1440 MMX cases/12963 checks and3456
SSE cases/34563 checks. MMX leaves MM0 and the x87 tag state dirty; only the
dispatcher executes EMMS. SSE preserves original MOVNTPS/MOVLPS/MOVAPS operations
without adding a production fence. The MMX compiler warnings about missing EMMS
are expected and are documented in319. Native coverage is bounded, not a proof
for invalid pointers, enormous counts or all asynchronous memory observations.

The test-only `fill_chain_fixture.cpp` additionally compares the **complete**
original dispatcher plus three original backends with the real C++ dispatcher
and all three real C++ backends. The private RW-to-RX oracle retains each raw
PE span and relocates only the dispatcher's two absolute flag operands and three
CALL displacements. The scalar/SSE gaps remain present for internal branches.
Canonical shared-runtime flag storage is reused; one heap flag has an explicit
fixture-only provider. Nothing from this fixture enters the game graph.

Final chain attempt002 passed **27648 cases/193547 checks**: four flag masks
(including both flags set),32 destination offsets,36 lengths0..4097, three DWORD
patterns, empty/populated x87 state, every guarded buffer byte, ESP/nonvolatiles,
x87 control/status/tag, MXCSR and unchanged dispatch flags. A fixture-only SFENCE
after both calls makes memory observation comparable; it does not claim to test
the entire hardware memory model. Attempt001 had an inline-assembly fixture
variable-name collision with 16-bit register names; that failed receipt is kept.
This extends composition coverage beyond standalone dispatcher mocks in312.

Fresh game build001 compiled **all166 C++ sources in eight actual projects**.
Exactly two old names closed (`heap_fill_mmx_005b0a40`, `heap_fill_sse_005b0b00`),
with no new dependencies: **266 unresolved names/295 references**, versus
Run318's268/297. Compiler errors and other linker errors are zero. No game EXE
or game execution. Build time5.74s. All418 source/dependency pins stayed unchanged;
the shared389-pin base is reused with29 delta pins.

The shared-cache audit validates both standalone native receipts, complete-chain
inputs/tools/libraries/logs/objects/EXE, original PE spans, fresh compiler events,
COFF definitions, source exclusion and exact frontier difference without rerunning
successful native fixtures:

```powershell
py -3 scripts/research/audit-v2-simd-fill-integration-321.py --chain-attempt 002 --build-attempt 001
```

Fresh attempts use unused IDs:

```powershell
py -3 scripts/research/verify-v2-fill-chain-321.py --attempt 003
py -3 scripts/research/build-v2-game-entry-321.py --phase configure --attempt 002
py -3 scripts/research/build-v2-game-entry-321.py --phase build --attempt 002
```

Next connected dependency: low-level file-open00561ca0/exists00561b80 used by313;
check canonical owners and typed ABI bindings before recovering another body.
Root/arena/context296/301/303, complete-game linking, startup, rendering and
gameplay acceptance remain open. PR20 reviews the separate experimental lowering
tool and is not a substitute for these recovered game functions.

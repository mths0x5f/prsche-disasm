# Run373: snapshot and async startup integration

The six original bodies from371/372 (447B) now enter the actual game graph.
Native proof reuses371/002 and372/003: **15,446 comparisons,16 mutations PASS**.
Shared acceptance PASS: **505 source pins,200 C++ TUs/8 projects compile**.
The fresh build001 leaves **203 unresolved names/211 references**, no EXE.
Three names close (snapshot save/restore and async callback), no new names.

The snapshot pair shares canonical fragmented state and original defaults;
restore copies the second block first and retains its actual input pointer.
The async queue uses explicit typed views of existing incoming/free slots,
original stale-tail behavior and captured callback/completion state.
See371/372 README/evidence for addresses, raw data, ABI and bounded domains.
The audit verifies canonical COFF ownership, compiler events, original bodies,
unchanged proof/source inputs and the actual DINPUT import library in this build.
No fixture or guessed service enters production.

```powershell
py -3 scripts/research/build-v2-game-batch.py --config iterations/v2/001-original-recovery/runs/373-snapshot-async-integration/build-config.json --phase configure --attempt 001
py -3 scripts/research/build-v2-game-batch.py --config iterations/v2/001-original-recovery/runs/373-snapshot-async-integration/build-config.json --phase build --attempt 001
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/373-snapshot-async-integration/acceptance.json
```

Reuse these immutable attempts. Arbitrary/computed snapshot aliases, malformed
queues, real concurrency and scheduler/allocator composition remain HOLD.
Next374 completes the non-null00534480 descriptor path reached by restore;
its existing null-only wrapper is unchanged. Linked game, live startup/display,
menu and gameplay remain unachieved.

# Run351: canonical heap lock bindings

Two typed application lock names now forward to the accepted005322b0/005322c0
providers. The exact original queue and cleanup call sites take the same pointer
and cdecl ABI. No lock storage or original algorithm is duplicated; recovery
count remains zero. Canonical heap_locks.cpp matches its accepted014 source SHA.

Native003 compiles the actual adapter and canonical provider TU, then compares
both12-byte PE bodies against the same recording Win32 endpoints. Nine cases
at /Od and /O2 (18 total) check pointer identity, event order, stack cleanup and
nonvolatile registers; all five mutations are detected. Unused allocation/init
paths have fail-closed fixture boundaries. This does not test real contention.

Fresh build001 compiles184 C++ TUs/8 projects:248 names/263 refs,noEXE/game
execution. Two names/four references close with no new dependency. Shared467-
input audit PASS and actual COFF confirms single canonical lock providers.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/351-heap-lock-bindings/acceptance.json
```

Next353 restores the bounded mono display/format subsystem from REA347/350 and
index352. Original fixed display address and enabled-path OS access remain HOLD.
Startup report's original-VA/variadic mismatch still needs separate proof.

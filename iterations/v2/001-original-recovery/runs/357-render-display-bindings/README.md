# Run357: display and procedure-address bindings

Nine display facades and two explicit-procedure loader helpers now use the
original THRASH interfaces. Getstate/about preserve consumed EAX values. Quad
and readrect preserve pointer/word order; loader helpers call their supplied
procedure address, which is not an extra DLL argument. No state or renderer is
created. Selected void facades discard only results ignored by original callers.

Native002 passes13 cases at /Od and /O2 (26 total), seven mutations detected.
Eleven SHA-pinned CALL instructions are exercised with explicitly synthetic
argument pushes/RET; these are transport excerpts, not original whole functions.
The fixture compares argument order, returned values, supplied-versus-table proc
selection, stack cleanup and nonvolatile registers. Canonical loader078 source/
header hashes remain unchanged.

Fresh build001 compiles188 C++ TUs/8 projects:224 names/232 refs,noEXE/game
execution. Eleven names/17 refs close with no new dependency; shared477-input
audit PASS. Equal source basenames require full COFF owner paths; the auditor
now verifies those paths. A wrong equal-basename owner is rejected.

The shared native runner also accepts optional SDK libraries, needed immediately
by358. Older receipts retain their original runner hash, verified against the
immutable committed Git blob; only that exact historical tool input is eligible.
All production/fixture inputs remain strict, with a mismatched-source negative
control rejected. No successful native comparison is rerun for tool metadata.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/357-render-display-bindings/acceptance.json
```

Actual THRASH/DLL/OS/visual behavior stays open. Next358 binds six original
KERNEL32 loader boundaries; settings/alias/unlock cases remain separate scope.

# Run363: early startup bindings

Six typed adapters connect mutex creation, immediate last-error retrieval, module
filename, the original drive-letter classifier, thread startup and lock creation
to exact Win32 imports or existing canonical providers. No duplicate state or
replacement algorithms are introduced. Original callsites and reused proof are
recorded in evidence.json; the actual game COFF identities are in import-proof.json.

Native002 passes nine cases at /Od and /O2 (18 total), with seven mutations
detected. The fixture compares SHA-pinned original CALL excerpts with compiled
adapters, including arguments, used returns, output bytes, call order, ESP and
nonvolatile registers. These excerpts use synthetic argument setup and RETs.
Actual filename/error platform TUs are compiled; controlled own-EXE IAT endpoints
are restored before exit. Existing algorithm proof is reused unchanged.

Fresh build001 compiles191 C++ TUs across eight projects. All six targeted names
close, with no new dependencies:207 names/214 references remain; no EXE or game
execution. The shared483-input audit passes, including single canonical providers.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/363-startup-bindings/acceptance.json
```

Duplicate-instance window handling, CD relaunch, partial pool005679f0, real OS
lifecycle/contention and full startup remain unaccepted. Run361 device/pool proof
is separate and not in this build. Next: finish its GUID/return/initial-state review,
then recover the original mouse-state children identified in Run362.

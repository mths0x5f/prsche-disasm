# Run356: original renderer export-table bindings

Nine game_setup/splash_progress names now call the current canonical43-entry
THRASH export table through five original slots: window40,clear3,flush24,pageflip14,
sync26. Selected original callers use matching stdcall arity and ignore returns.
No table, renderer behavior, null guard or recovered original function is added.

Native003 passes11 cases at /Od and /O2 (22 total), seven differential mutations.
Nine SHA-pinned callsite blocks plus two ordered call sequences compare slot,
argument, stack and nonvolatile state against the C++ facades. These are snippets,
not whole original functions: the harness remaps the slot operand and appends
RET/RET4, supplying EDI=0 for game sync. A separate bad-cleanup experiment002
crashed on its synthetic return as expected and is not counted as a clean control.

Fresh build001 compiles187 C++ TUs/8 projects:235 names/249 refs,noEXE/game
execution. Nine names/ten references close with no new dependency. Shared475-
input audit PASS; COFF retains one canonical table owner. Loader source/header
match accepted078 proof; stale028 hashes are not used for reuse claims.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/356-render-bindings/acceptance.json
```

Actual THRASH DLL/OS/game execution remains unproved. Next357 separately checks
nine display facades and two explicit-procedure helpers, preserving used returns.
Settings/unlock/alias-slot interfaces stay outside this batch.

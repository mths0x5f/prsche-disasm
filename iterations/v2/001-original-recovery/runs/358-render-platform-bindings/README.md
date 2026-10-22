# Run358: original loader Win32 bindings

Six cdecl loader boundaries now call the exact original KERNEL32 interfaces.
Four reuse compiled formatter/window/core providers; FreeLibrary and
DisableThreadLibraryCalls use thin direct imports. Raw32 handles, procedure
pointers and immediate GetLastError results are retained without caching or
invented error values. No new loader policy or renderer state is introduced.

Native008 compiles actual provider TUs and passes8 cases at /Od and /O2 (16
total), six mutations detected. Original IAT CALL/MOV ESI excerpts use explicit
synthetic arguments/RET. The test redirects its own six IAT entries to recording
stdcall endpoints, then restores them before exit. The SDK user32/gdi32 libraries
are hash-pinned through shared runner extra_libraries. Unused fatal paths fail
closed in the fixture. Real DLL loading is outside this controlled comparison.

Fresh build001 compiles189 C++ TUs/8 projects:218 names/226 refs,noEXE/game
execution. Six names close,none appear; shared479-input audit PASS. Actual game
COFF direct imports match original FreeLibrary/DisableThreadLibraryCalls.
Initial audit/acceptance001 are retained; final intake additionally checks the
four canonical provider owners and pins import-proof.json. Native proof unchanged.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/358-render-platform-bindings/acceptance.json
```

Live THRASH, OS display and full-game/visual acceptance remain open.359 separately
binds settings returns and live alias cells; startup blockers are mapped in360.

# Run370: input startup integration

Integrates367 original DirectInput/Win32 bindings,368 original wheel/exit callbacks
and369 original sorter with its two helpers. Six new original VAs/551 bytes and
four additional typed platform facades enter the game graph; no test endpoint
or fixture source is linked. Existing361/364 source and ABI declarations remain
unchanged. Typed window dispatch is proved through the address-only legacy alias.

Shared native proofs total923322 comparisons and14 detected mutations:216 input
transports,917732 callback/exit cases and5374 sort/helper cases. Wheel cases exhaust
signed16-bit input and wrapping seeds; sorter cases compare exact callback order
and all bytes, not only sorted keys. Controlled OS/COM boundaries remain explicit.
The canonical module provider, existing startup/cleanup source and unchanged
original proof are reused rather than counted as new functions.

CMake uses lib.exe and the exact dinput.def to create the real named import missing
from current SDKs. The generated x86 library carries DINPUT.dll!DirectInputCreateA;
only its pointer-cell symbol is aliased to the compiled stdcall reference. The .def
is included in the build source pins; the generated library and both loader-only
PE probes are pinned by acceptance. No lazy loading or DirectInput8 substitution.
These probes prove loader/import identity, not live input-device behavior.

Fresh build002 compiles198 C++ TUs/8 projects:206 unresolved names/213 references,
no EXE or game execution. Eight names close with no new dependency. Shared500-input
audit PASS. Attempt001 stopped in sandboxed MSBuild before any compile events and
is retained as failed; its parsed zero names are not a valid link frontier.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/370-input-startup-integration/acceptance.json
```

Next371: original renderer snapshot save/restore00570ed0/00570f00, including the
existing fragmented state aliases. Async callback/list service follows. Real OS/
COM, opaque cursor failure state, allocator/concurrency, complete startup/display
and gameplay remain unaccepted; see recovery-validation-backlog.md.

# Run367: original input platform bindings

Bounded native proof PASS: one new original 6-byte thunk0056e940 and four typed
bindings close the mouse/keyboard platform transports. Production integration
and shared acceptance are owned by the coordinator. Original module is
`Porsche.exe`, SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Index queries for DirectInputCreateA, GetCursorPos, ScreenToClient and
GetModuleHandleA resolve to the four raw PE named imports at005b202c,005b2280,
005b228c and005b2138. Indexed mouse00536e95/9c and keyboard0055fd49/50 callsites
use the same DirectInput thunk. The registry has no prior0056e940 owner.
`platform-evidence.json` records the original bytes/callers, registry check,
POINT layout, exact ABI and boundaries. Cursor/module/keyboard facades do not
add recovered original-body counts. No existing header/source is changed.

`startup_input_platform.cpp` preserves four-argument stdcall and all HRESULT
bits for DirectInputCreateA. The keyboard binding reuses that canonical thunk;
the module binding calls the existing canonical window_module_handle(NULL).
POINT size/alignment/field offsets are statically checked against Windows POINT.
Cursor wrappers pass the caller's actual storage directly to USER32, preserving
failure and partial-write behavior.

Native attempt001 passes108 original/C++ comparisons on each of /Od and /O2
(216 total), with six detected mutations. The shared fixture SHA-pins the
original thunk and four original call instructions before relocation. Forwarding
pushes/RET are labelled fixture construction. Controlled endpoints check
argument pointer/bit transport, output including no/partial writes, EAX results,
events, ESP and preserved EBX/ESI/EDI/EBP. The DirectInput import pointer cell is
defined only by the fixture; USER32 IAT slots are patched only during testing.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/367-input-platform-bindings/native-config.json --attempt 1
```

Accepted receipt: `local/experiments/v2-input-platform-native-367/001/receipt.json`.
The passed source/config/fixture remain frozen; use a new attempt only after
changed inputs, a failure or an unresolved concern.

The SDK lacks dinput.lib. `dinput.def` creates a real original named-import
library with MSVC lib.exe; the source linker directive aliases only the compiled
stdcall import POINTER cell to the undecorated library cell:
`__imp__DirectInputCreateA@16=__imp__DirectInputCreateA`. The stdcall function
signature and generated call sequence stay intact. No lazy loader or alternate
DirectInput API is introduced.

```powershell
& ./local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/lib.exe /nologo /machine:x86 /def:iterations/v2/001-original-recovery/runs/367-input-platform-bindings/dinput.def /out:<build-directory>/dinput.lib
```

`local/experiments/v2-input-platform-native-367/import-proof-004/receipt.json`
pins the exact commands/tools/library/objects/probe/logs. Both frozen production
objects (/Od and /O2) link against this actual library. Their resulting PE import
tables contain exactly DINPUT.dll!DirectInputCreateA, without @16, plus the exact
USER32 cursor exports. The system x86 DLL export is checked; both loader-only
probes exit0. The local probe module endpoint is outside the game graph and no
DirectInput/device function is executed. Trials001/002 preserve rejected decorated
export spellings;003 preserves the metadata-alias investigation.

Real Windows/COM input startup, actual DirectInput devices, concurrency and
complete game/visual acceptance remain open. In particular,361's opaque coordinate
boundary after failed GetCursorPos/successful ScreenToClient is unchanged.

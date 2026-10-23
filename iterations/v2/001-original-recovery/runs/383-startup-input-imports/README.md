# Run383: exact startup keyboard and joystick imports

Native001 **PASS**: 564 cases / 1692 checks in each `/Od` and `/O2`, with
six detected mutations. Three existing cdecl platform facades are supplied;
no new original function VA, game state or recovery-body count is claimed.
Root owns CMake/shared integration and acceptance.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries: `GetKeyboardType`, `joyGetNumDevs`, `joyGetDevCapsA`, their three
IAT cells, and callers `00564e70`/`00564ab0`. Raw SHA-checked PE import
descriptors and FirstThunk indexing independently prove:

- `USER32.dll!GetKeyboardType`, IAT005b2298.
- `WINMM.dll!joyGetNumDevs`, IAT005b2354.
- `WINMM.dll!joyGetDevCapsA`, IAT005b2358.

Raw keyboard caller loads ESI from005b2298 then calls ESI with kind0/1.
Joystick enumeration directly calls `[005b2354]`, loads EDI from005b2358,
then calls EDI with `(id, stack-buffer, 0x194)`. Indexed references and full
raw caller instructions are retained in `evidence.json`; imported identity is
not inferred solely from a nearby disassembly label.

Installed Windows SDK10.0.26100.0 declares `int WINAPI GetKeyboardType(int)`,
`UINT WINAPI joyGetNumDevs(void)` and
`MMRESULT WINAPI joyGetDevCapsA(UINT_PTR,LPJOYCAPSA,UINT)`. Source uses these
actual declarations and explicit ANSI API. x86 pointer/UINT_PTR sizes and
`sizeof(JOYCAPSA)==0x194` are compile-time checked. The existing public facades
remain cdecl; their arguments and complete32-bit return patterns are preserved
through the stdcall calls. No guard, status normalization, Unicode substitution
or lazy loader is added. Exact `user32.lib` and `winmm.lib` inputs are available
and pinned. Production integration must link both libraries.

The fixture reuses367's own-EXE IAT patch pattern. It requires exact named
USER32/WINMM imports in its PE, patches only those three cells to typed controlled
endpoints, compares the same endpoint through original instruction bytes and
the new actual SDK calls, then restores the cells. Forwarding pushes, saved
registers and final RET are harness code; original load/call opcodes and IAT
operands are asserted before relocation. Live keyboard/joystick APIs do not run.

Cases compare all call arguments, call count, raw EAX, guarded capability bytes,
ESP and EBP/EBX/ESI/EDI preservation. Kind/id/return high bits, zero/one/exact404/
405/all-one byte counts, adjacent backed-pointer offsets, null and synthetic
pointers are covered. Controlled partial writes include failing raw returns;
their behavior is a synthetic transport contract, not a claim about Windows API
failure semantics. Synthetic/null pointers are never dereferenced. Mutations
detect changed keyboard kind, truncated keyboard/count returns, wrong device id,
lost capability pointer and replaced byte count.

`coff-evidence.json` pins both object symbol/disassembly dumps and linked fixture
PE import dumps. Objects reference exactly decorated SDK stdcall import cells
`__imp__GetKeyboardType@4`, `__imp__joyGetNumDevs@0`, and
`__imp__joyGetDevCapsA@12`; their public providers match the old facade names.
SDK headers/libs, sources and compiler dependencies are pinned by native receipt.
No original caller/state/header or accepted proof was changed. Actual device
behavior, composed startup and live game/display acceptance remain open.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/383-startup-input-imports/native-config.json --attempt 1
```

Receipt: `local/experiments/v2-startup-input-imports-native-383/001/receipt.json`.
No new runner, shared-tool changes, resources or commits.

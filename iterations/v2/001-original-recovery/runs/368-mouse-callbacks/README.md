# Run368: original mouse wheel and exit callbacks

Native002 **PASS**: 458866 cases / 1839787 checks in each `/Od` and `/O2`,
with four detected mutations. New bodies are `00537020..00537062` (67B,
including the complete `RET24`) and `005370b0..005370bf` (16B): 2 VAs / 83B.
Production graph intake and shared audit belong to coordinator Run370.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index entrypoints/references were searched before implementation; neither new
body has a canonical registry owner or overlaps the adjacent accepted startup
(`00536e50..00537017`) and cleanup (`00537070..005370ad`) ranges.
The main index omits both function entries. Supplemental navigation is
`research/binary-index/supplemental/mouse-callbacks-368.jsonl`; every instruction
and full body hash was checked against raw PE bytes. `original-evidence.json`
records the bodies, wheel ownership, refs, HIGHLOW operands and zero-fill section.

Wheel dispatch checks the first argument and exact canonical window handle.
Original high-word sign extension, signed magic multiply `0x88888889`, add,
arithmetic shift6 and sign correction implement signed division by120 with
truncation toward zero. The result accumulates modulo2^32. Native cases exhaust
all65536 signed highwords against seven accumulator seeds including both signed
boundaries and wrapping, and exercise lowword independence, inactive/mismatched
dispatch and a matching null handle. EAX is zero, the last pointer remains
untouched, ESP is restored by the callee's RET24 and EBX/ESI/EDI are preserved.
The synthetic invocation wrapper's sentinels/pushes are harness instructions.

`0069e0a8` is a new canonical uint32 owner in `mouse_callbacks.cpp`, initially
PE loader zero-fill. All five indexed refs match exactly five HIGHLOW and raw
operand occurrences: callback read/write, poll005372a0 read/read/clear. At
`005372ac`, EBX is zeroed before the clear at `00537358`. Startup and exit do
not reset this cell; no extra reset was added. Computed aliases/concurrency
remain outside this evidence.

The frozen361 header declares a legacy cdecl callback name, but actual361 startup
only takes its address for registration. New canonical
`startup_mouse_window_handler_00537020` has the exact `WindowHandler` stdcall
signature used by `0053aba0`; there is no cdecl-returning callback implementation.
The source carries an MSVC x86 `/alternatename` binding from the legacy name to
this entry. `coff-evidence.json` pins object/directive/relocation dumps and linker
maps: the frozen361 legacy reference is an undefined DIR32 address operand;
new code defines the stdcall provider. Both map names share address00401020
(`/Od`) or00401010 (`/O2`). These fixture link addresses are evidence, not original
VAs or production function pointers.

The fixture links actual frozen361 startup and364 cleanup/mode sources with
bounded external transports. Actual361 registration runs, asserts legacy,
registered and canonical addresses are identical, and invokes the registered
address through `WindowHandler`. Exit comparison composes the new original exit
body with copied original cleanup versus actual accepted364 cleanup, checking
COM order and intermediate initialized/wheel/pointer state for all four device
presence combinations. The initialized flag is cleared after cleanup; wheel and
exit-registration state are preserved. These reused bodies are not new recovery.
Controlled COM/OS/renderer endpoints do not prove live device or full startup.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/368-mouse-callbacks/native-config.json --attempt 2
```

Receipt: `local/experiments/v2-mouse-callbacks-native-368/002/receipt.json`.
Attempt001 passed both comparisons but stopped because mutation diagnostics were
not flushed before ExitProcess;002 corrects the fixture diagnostic and detects
active-gate, divisor, highword sign and exit-order mutations. Attempts are immutable.
COFF artifacts/maps: `local/experiments/v2-mouse-callbacks-native-368/coff-002`.
No old header/source was edited, no original resource changed, and no live game,
window procedure composition or visual acceptance is claimed.

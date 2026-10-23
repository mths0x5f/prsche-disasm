# Run371: original cursor state snapshot pair

Native002 **PASS**: 1000 cases / 3000 checks in each `/Od` and `/O2`;
five material mutations detected. New bodies: `00570ed0..00570ef5` (38B)
and `00570f00..00570f4e` (79B), 2 VAs / 117B. Coordinator owns production
CMake/registry integration and shared acceptance.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query: both entries, their three callers `005342a0`, `00565530`,
`005727c0`, and `005de620..005de67f` references. Neither new entry has a
canonical registry provider. `evidence.json` records original bodies, full
raw caller bytes/disassembly, raw initial data, complete 221 indexed state
references/consumer names, 240 state HIGHLOW operands and 31 callback-cell
operands. The 37 raw operand sites without a nearby same-target indexed
reference retain byte contexts; no missing function/consumer is invented.

Save executes two forward 12-DWORD copies, first `005de620`, then `005de650`.
Restore executes the second block before the first. After both copies,
nonzero mode **low byte** and zero `005de64c` call `[006bd9b0](mode)`;
otherwise `00534480(snapshot)` receives the actual original pointer.
Both entries are cdecl and every indexed caller discards their EAX. Public
void signatures reuse the already established364 caller contract.

The canonical frozen `window_shutdown.cpp` owns the first48B, its mode/state
aliases, independent bytes `005de65c/65d`, and DWORD `005de67c`. New371 owns
only 12 missing bytes `005de650..65b` and 30 bytes `005de65e..67b`.
An explicit second-block byte view shares the old owners, without assuming
their host adjacency. Original nonzero defaults are preserved:
`005de660=1`, `005de66c=640`, `005de670=480`; other new bytes are raw zeros.
No old field is redefined/reset and no full duplicate production arena exists.
`coff-evidence.json` pins `/Od` and `/O2` symbol dumps:371 defines only its new
storage/functions and references canonical fields; the frozen owner supplies
those fields, and359 supplies the stdcall callback adapter.

The fixture links those actual frozen owner/359 sources. It asserts all96B
production initial state against raw PE bytes **before resets**, checks the
canonical aliases, then installs a controlled callback into THRASH slot40.
Original cell `006bd9b0` is loader-zeroed `.data`; raw restore opcode/cell
metadata is checked before patching. A contiguous96B arena belongs only to
the original-byte oracle. Fixture-only unused shutdown services fail closed.

Cases cover randomized complete state/buffers, guarded96B destinations at
eight alignments, mode0/1/2/127/128/255 with nonzero high24 bits, and zero,
one, sign-bit and all-one gating DWORDs. Both state blocks, untouched guards,
callback kind/argument, complete callback-entry state, callback mutations of
canonical/new bytes and input-pointer effects are compared. ESP and
EBP/EBX/ESI/EDI preservation are checked. Mutations detect lost second-block
save, wrong shared-byte ownership, full-DWORD mode, missing gate and replaced
snapshot argument. Ordered DWORD/block operations match raw assembly; no
concurrency or overlap-order observation is claimed for this disjoint domain.

All three indexed callers allocate independent96B stack snapshots, including
actual accepted364 cursor application. Arbitrary/computed or overlapping
global pointers remain HOLD: fragmented host objects provide no valid contiguous
96B alias, and no alias-remapping API is introduced. The non-null `00534480`
body remains an existing `render_display_texture_bind_00534480` typed external
dependency; the accepted null-only shutdown path does not cover it. Controlled
endpoints do not prove actual renderer, live startup, display or gameplay.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/371-cursor-snapshot/native-config.json --attempt 2
```

Receipt: `local/experiments/v2-cursor-snapshot-native-371/002/receipt.json`.
Attempt001 stopped at link because the intact canonical storage owner also
references unused shutdown services;002 adds fail-closed fixture endpoints.
No new runner, old-source edits, original resource changes or commits.

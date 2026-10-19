# Run 423 — input `_getstate` (00532e10), every mode

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Completes `fe_input_getstate_00532e10` (293 bytes) in the canonical
`source/recovered/Porsche.exe/input_state.cpp`. Previously only mode 6 was recovered; the
other modes and the device-type error were typed boundaries. The original source file is
`\real\patch3\pc\input.c` (string at `005bb2f8`) and the function reports itself as
`[INPUT] _getstate`.

Mode table `00532f38`: 1 returns the device count; 2 fills the `0x21c`-byte caps buffer
`006bde20` through `input_caps_0056fdb0` and returns it, or null on failure; 6 reads the
device state (unchanged); 8 returns `input_property_mode8_0056fff0`; 3, 4, 5, 7 and anything
outside 1..8 report `"[INPUT] - Invalid getstate (%d)\n"` at line `0x219`. An invalid
device type in mode 6 reports `"[INPUT] _getstate, Internal error in devicetype\n"` at line
`0x1fa`. Both reports set the diagnostic file/line cells and call the handler at `005debf0`;
the invalid-mode call is printf-style (format plus mode, 8 bytes popped).

The boundaries `input_unrecovered_mode_00532e10` and `input_invalid_type_00532eae` are
removed. The latter's signature was inaccurate: the original passes no type to the report.
Negative and `>= 32` indices stay boundaries, because the original reads outside the slot
array there. The caps buffer is declared `extern`: it ends 4 bytes before
`input_slots_006be040`, the memory a negative index reads.

`input_probe.cpp` and `input_snapshot_probe.cpp` now provide the new callees; both compile
and link, and an `input_probe` smoke run gives `P,G80s` for a valid type and `D` for an
invalid one. The Unicorn verifiers (`verify-v2-input-state.py`, `verify-v2-input-snapshot.py`)
were **not** re-run: `unicorn` is not installed here.

Validation: 24/24 differential cases on a physical x86 slab holding `00532e10` and its
original `0056fce0`/`0056fd00`/`0056fd30` chain, with both jump tables relocated and the
three original strings copied byte for byte so message content is compared. Negative
control: eight mutations of the canonical source each fail — count + 1 in mode 1, ignoring
the caps result, an off-by-one line, an altered message, an altered file string, mode 8
returning zero, an unmasked device type, and mode 3 treated as mode 1. No independent
audit script yet.

```
python scripts/research/experiment-v2-input-getstate-423.py --finalize --attempt 1
```

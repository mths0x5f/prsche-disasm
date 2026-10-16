# Run 226 audit

`audit.py` independently rechecks all repository input pins, actual COFF symbols/offsets, `.ogw$sc` zero bytes, writable/readable/non-executable flags, and zero object relocations.
It verifies original `.data` zero cells `005e25d0`/`005e25d4`, distinct from readonly `.rdata`, plus fixture PE `.ogw` bytes/permissions/zero cell relocations and recorded native exit 0.
All 12 + 3 HIGHLOW sites are matched to actual indexed instructions and exact MEM4 reads/writes: `005e25d0` 4R/8W, `005e25d4` 1R/2W; no in-cell relocations.
The packet preserves four-byte separation and signed/unsigned views for current consumers only; computed-pointer, whole-data layout, aliases, lifetime and production ownership remain deferred.
No compiler, native, or Ghidra rerun was performed; audit output is `ok=true`.

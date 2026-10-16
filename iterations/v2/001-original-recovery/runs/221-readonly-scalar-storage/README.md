# Run 221 audit

`audit.py` independently rechecks frozen source/include/object/input pins, actual COFF symbols, `.orig$fc` bytes/readonly flags/zero object relocations, and fixture PE `.orig` bytes/readonly flags/zero cell relocations.
It also checks original `.rdata` cells (`005b242c=0000c842`, `005b24a8=0000803f`), section permissions, and recorded fixture exit `0`; run output reports `ok=true`.
Indexed/highlow reference accounting is 55 for `005b242c` and 709 for `005b24a8`; the latter is 683 indexed instruction reads plus 26 unindexed relocation-overlap candidates.
Those 26 candidates come from `unindexed-relocation-candidates.json` and are only overlapping immediate decodes, not instruction-boundary proof; indirect/address-taken uses remain open.
Evidence supports current native consumer `00485100` using exact original readonly cells; future formal byte aliases must bind to the same cells.
No production ownership/allocation, whole-program alias or relative-address conclusion is made; no compiler, native, or Ghidra rerun was performed.

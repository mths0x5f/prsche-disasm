# Run 225 — writable scalar selection

One cached 216 inventory plus the pinned original PE/disassembly were read; only `.data` writable zero-aligned int/uint4 views were considered.
Eligible: `005e25d0` (`?DAT_005e25d0@@3HA`, 12 exact indexed `MOV dword` refs: 8 writes/4 reads) and `005e25d4` (`?DAT_005e25d4@@3IA`, 3 refs: 2 writes/1 read).
Both cells are actual PE zero bytes, have no HIGHLOW relocation in-cell, no partial/address-taking/array/pointer form, no gaps, and no canonical/WIP/native view overlap.
Rejected 20 same-filter cells: 7 had no indexed direct reference; 13 had immediate-overlap or other unproven decode candidates, so they fail the no-gaps rule.
This is navigation evidence only; no storage owner, allocation, production declaration, or original behavior is inferred.
No compiler, native, or Ghidra run was performed.

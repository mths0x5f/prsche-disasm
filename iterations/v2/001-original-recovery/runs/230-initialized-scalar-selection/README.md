# Run 230 — initialized scalar selection

Read-only selection over all 228 frontier data entries: 54 aligned writable `.data` int/uint4 candidates remained after excluding 221/226 cells.
Eligible: `005ccb34` int `80000000` (2R), `005d0608` int `01000000` (2R/1W), and `005e5f4c` int `0a000000` (2R); every HIGHLOW ref is an indexed direct MEM4 instruction and each cell has zero in-cell relocations.
All three have no pointer/array/address-taking/partial/gap evidence and no canonical/WIP/native data owner; native mangles are `?DAT_...@@3HA`.
Rejected: 12 no direct indexed refs, 34 immediate-overlap/unproven gaps, and 5 direct-ref cells rejected for adjacent native views/array-like relationships.
This is current-view navigation only; global ownership, computed pointers, aliases, lifetime, and whole-game production behavior remain open.
No storage allocation, compiler, native, or Ghidra run was performed.

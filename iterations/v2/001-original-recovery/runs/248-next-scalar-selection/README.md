# Run 248 ? next scalar storage selection

- 125 cached frontier scalar tasks were checked against pinned PE bytes/section, relocation set, and indexed disassembly.
- Selected top 8 by exact direct MEM4 fanout: `0065b928`, `00690848`, `00656864`, `00656ac0`, `006a6450`, `00699c84`, `00699fe0`, `006c0508`; all are writable `.data` virtual-zero-tail cells.
- Every selected operand has an exact HIGHLOW relocation; no in-cell relocation, indexed/array/address-taking reference, cross-VA overlap, same-VA alias, or prior owner was found.
- All consumer PCs/bytes/accesses and rejection counts are in `summary.json`; readonly pool is empty. Navigation only; no type, array, owner, allocation, compiler, native, or Ghidra claim.

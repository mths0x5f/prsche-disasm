# Run 235 — callback initialization inventory

- Pinned Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`; indexed source/disassembly and PE bytes were checked read-only.
- Full PE HIGHLOW relocation scan covers 9 sites for `006b49a2` (one `00565720` byte write, eight reads) and 4 sites for `006b49e0` (all `MOV EDI,imm` address-taking in `00566ea0/005907b0/00590a80/00590b50`); no direct `49e0` read/write.
- Exact PE bytes match indexed records; `006b49a2` reset/write is not evidence of a `006b49e0` writer.
- `00565720` calls `00565680`, `005656d0`, and `0058fdb0`; concrete nearby `006b48c0` write/read records are retained as provider evidence only.
- `0058ff50` uses computed base `006b49c8` and count `006b49a1`, not proven `006b49e0`. Callback targets, ABI, ownership, and semantics remain unresolved; navigation only.

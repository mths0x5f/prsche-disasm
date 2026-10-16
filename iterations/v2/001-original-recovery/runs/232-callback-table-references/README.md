# Run 232 — callback-table references

Indexed range `006b49c0..006b4a04` has 74 direct absolute data refs: `006b49f0` 2, `006b49f4` 1, `006b49f8` 1, `006b49fc` 3, `006b4a00` 54, `006b4a04` 13; exact `006b49e0` has no direct memory read/write.
Exact `006b49e0` is address-taken as immediate `MOV EDI,0x6b49e0` at 00566f27 (FUN_00566ea0), 0059095b (FUN_005907b0), 00590b0e (FUN_00590a80), and 00590bd6 (FUN_00590b50).
Concrete direct writers include 00565798/005657b1 (006b4a00/4), 00565b7b (006b49f0), 00567520/005676de (006b49fc), plus computed table write `[EAX*4+006b49c8]` at 0058ff5b.
All listed absolute writer bytes and relocation sites were checked against the original PE; computed table targets remain unresolved and are reported separately in `summary.json`.
No callable prototype, algorithm, owner, or current `006b49a2` reset semantics is inferred; no compiler, Ghidra, native, or source edits.

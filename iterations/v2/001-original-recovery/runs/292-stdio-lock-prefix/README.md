# Run292: expand the existing CRT lock prefix for stdio

The canonical header and storage owner declared26 pointers at original005e57a8.
The original FILE selectors require IDs28..47; stdout uses29. The same owner is
now expanded to48 pointers. This is a proved192-byte prefix, not a claim about
the total original table extent. No second table or bounds workaround is added.

PE bytes prove four initial pointer cells (indices1/9/13/17); all other cells in
the prefix are zero. The independent293 audit verifies the four HIGHLOW sites
005e57ac/57cc/57dc/57ec. Header-alias and source scans found one canonical owner
and no sizeof/range consumers whose algorithm would change. The only two game
source edits are `[26]`→`[48]`; algorithms and initialization order are unchanged.
`preflight.json` records parent Git identities and exact before/after hashes.

Verification reuses the157 probe and original-PE oracle, mechanically changing
three loop limits from26 to48 in each private fixture. One two-TU `/MP6` batch
compiled the actual canonical owner and derived probe. All48 initial cells match
the PE.112 native/original comparisons cover IDs28..47 (existing/lazy locks,
scripted allocation races and unlock), five earlier IDs, initialization and
allocation failure. Full arena, static bytes, table, return/error state and
ordered endpoints are compared. The old4152 stdio cases were not repeated.

The first link failed because its VC library path omitted MSVCRT.lib. Its receipt
is preserved. Corrected link002 reused the same compiled objects; one native
execution passed. `producer-used.py` preserves the original driver version.

This closes the insufficient-storage hold. Real OS concurrency, lifetime and
original CRT/bootstrap initialization remain separate open work. Older frozen
reports pin the historical26-entry source; their bytes remain in Git and are
not silently rewritten. Run293 freshly recompiles the game against the new owner.

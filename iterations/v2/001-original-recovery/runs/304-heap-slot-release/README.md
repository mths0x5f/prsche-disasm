# Run304 — bounded heap-slot release

Original `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, indexed`005699f0..00569a37`,72 bytes. The registry has no accepted exact or overlapping owner and the actual274 union has no game object for this VA. `005699f0.cpp` implements the original cdecl one-DWORD input and EAX0/1 return through`porsche::heap_slot_release_005699f0(uint32_t)`.

The function masks the full DWORD ID with`0xf`, loads one of the16 original heap pointers, and returns0 for a null slot. Otherwise it caches that heap and its slot address. A nonzero lock field`heap+0x38` calls the existing accepted`heap_lock_destroy_005322d0(void*)` contract; then`heap_fill_0053c290(heap,0,0x40)` runs, the selected table slot is cleared, and the result is1. The heap pointer stays cached across callbacks even when a callback replaces the table entry. The final slot clear overrides callback writes to that selected slot.

The game object references the existing canonical`heaps_006b4f20[16]` allocation proved in272. It defines no table, storage view or substitute provider. The two callee declarations come directly from canonical`porsche/heap_locks.hpp` and`porsche/heap.hpp`. Their actual original CALLs remove4 and12 bytes respectively; returns are ignored. No guessed raw-to-canonical alias is introduced. The existing accepted lock implementation is reused by symbol; fill remains an external canonical boundary.

One `/MP6` batch compiled the body and its private fixture. The fixture linked the **unchanged actual272 storage COFF**, rather than defining another table. It compares960 bounded states against all72 original bytes:16 selected slots, four high-bit patterns, null slots/non-null heaps with null or high-bit lock values, and five callback mutation modes. Each case checks the entire4096-byte arena, all16 actual shared slots, callback order/arguments, EAX0/1, cdecl stack balance, nonvolatiles and DF=0. Controlled callbacks can replace/clear the selected slot, change the cached heap's lock field, change another table slot, and mutate memory during fill. Lock destruction and fill algorithm semantics themselves are not reaccepted by this controlled-provider fixture.

The original oracle is isolated in`fixture.cpp`/`original-body.inc`. Its two table DIR32 operands and two CALL REL32 operands are patched only in fixture memory, with original operands/targets independently checked against the PE. The game COFF has exactly one function definition and three unresolved canonical dependencies: table, lock destroy and fill. Summary and receipts pin both new objects, reused owner, source dependencies and compiler/tool identities through the common immutable manifest reader. No original machine code or fixture callback definition enters the game object.

```powershell
py -3 scripts/research/experiment-v2-heap-slot-304.py --attempt 001 # completed, do not repeat
py -3 scripts/research/audit-v2-heap-slot-304.py
```

Both compilation and native execution passed on the first attempt, without warnings. This packet performs no shared game build and does not resolve Run303's unmasked parent arena/context state HOLD. Arbitrary invalid heap pointers, callback faults and whole-game shutdown remain outside the finite verification.

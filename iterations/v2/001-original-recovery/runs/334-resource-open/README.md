# Run334 — original resource open wrapper and callback

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Recovered `00561ca0..00561cde` (63B) and `00561ce0..00561df3` (276B),339B
total. Native attempt002 passes30240 comparisons at `/Od /Oy- /GS-` and30240
at `/O2 /GS`:60480 comparisons/302400 checks. Six optimized source mutations
are detected. Root owns game integration335; this packet defines no production
storage cell or backend provider.

## Source and original contracts

Index-first evidence is Run327 `evidence.json` and
`research/binary-index/resource-open-callback-327.json`, supported by the
unchanged original PE and fresh REA325/001. The callback's missing function
entry is distinct from its complete indexed instructions; all276 original
bytes and three returns were verified in327/325. These receipts are reused,
not rerun for metadata. Existing registry/all-run ownership checks found no
accepted implementation of either target. Run313's pointer-return wrapper
declaration is included unchanged to check the existing caller contract.

`resource_open_334.cpp` supplies the exact wrapper and one callback body. The
callback keeps the existing `ResourceLeafAtomicCallback` int32 cdecl signature.
Four-byte copies transport pointer bits through that result and back to the
wrapper's `void*` return; no incompatible callback-function-pointer call is
introduced. This preserves high-bit pointer results without booleanization.

The wrapper snapshots group005df770 before routing, as shown by the original
MOV/PUSH preceding device CALL00561cc8. Its16B context sets path+00,flags+08,
diagnostic1 at+0c; +04 remains uninitialized and unread. The callback saves
the path before opening, opens mode1 at the incoming group, sizes at
`group-1` modulo32, then reloads flags+08 for allocation. The original handle
output reuses its incoming group slot; the C++ local starts with the same raw
group bits, including the value visible to the open boundary before writing.

After successful allocation, read uses offset0 and the raw reported size.
The read result is ignored. Close occurs before the single transform-cell
reload. Transform arguments are `(buffer,saved_path,saved_flags)`; a null
transform result frees the original buffer, while a nonnull result is returned
without a local free. Allocation failure reloads diagnostic flag+0c, optionally
reports line210, closes and returns0. Open failure optionally reports line218
and returns0 without close. Diagnostic file/format literal bytes are pinned
directly from005bcd00/005bcd38/005bcd5c.

The shared diagnostic cell retains its canonical declaration and owner. A
narrow x86 adapter pushes path and format, calls the cell and cleans8 bytes,
matching the original two-argument consumer. It does not invoke that address
through an incompatible C++ function-pointer type. Canonical shared runtime
globals/setters and initialized group owner are linked directly into the
fixture; no copies of their algorithms or production storage definitions are
added here.

Canonical open00533b90 is declared `bool`. Its original full-EAX return is
normalized0/1 (status normalization00533bc1..00533bc6, MOV EAX,ESI at00533bd5,
and zeroed failure return). That89B canonical-callee contract is separately
recorded alongside the selected bodies in the native receipt. It is not an
additional recovered body and is excluded from the339-byte selected count.
The fixture's naked bool entry forwards controlled full-EAX0/1 only; arbitrary
noncanonical return words are not used to claim bool/full-word equivalence.

## Extern-only transform boundary

`resource_open_334.hpp` declares a4B cell006ad750 with consumer type
`void* (__cdecl*)(void*,const char*,uint32_t)`. Neither production TU defines
the cell. Both actual COFF objects leave exactly one reference to its native
name, `?resource_open_transform_006ad750@porsche@@3P6APAXPAXPBDI@ZA`.
All other undefined contracts already belong to canonical route, dispatcher,
file/heap and diagnostic owners. `/O2` additionally emits three read-only
diagnostic string COMDATs; these are not transform storage or new game state.

Run336 independently retains setter/layout/computed-alias coverage holds.
Those unresolved provider questions do not prevent this bounded consumer
recovery. No guessed zero initializer, global state block or no-op transform
is installed in production. Full OS/heap/dispatcher/transform composition,
storage ownership and game/visual acceptance remain separate work.

## Native proof and reproduction

```powershell
py -3 scripts/research/verify-v2-resource-open-334.py --attempt 2 --negative-controls
```

Attempt002 is immutable; use an unused positive ID for another run. Receipt:
`local/experiments/v2-resource-open-334/002/receipt.json`, pinned by
`summary.json`. Production filenames are `resource_open_334.cpp/.hpp`;
the tracked fixture template is `resource_open_fixture_334.cpp.in`.

The original wrapper calls the actual relocated original callback through a
controlled dispatcher. Standalone callback calls are checked too. Each run
compares raw EAX, ESP/EBP/EBX/ESI/EDI, ordered boundary arguments, final defined
context/global state, arena bytes and canaries. Fixture code never reads
context+04. Pointer identities are compared for paths, handles and buffers;
diagnostic literal addresses are normalized by exact text because native C++
literals and relocated PE literals occupy different host addresses.

Cases combine groups0/1/100/80000000/ffffffff, raw flags, zero/positive/negative/
large sizes, open/allocation failures, absent/null/identity/replacement transforms
and mutable context/global phases. They include route mutation of the global
group, changes to flags after size, transform changes during open/size/allocation/
read/close, diagnostic mutation of the handle output, and ignored read failures.
High-bit replacement pointers verify complete32-bit return transport. The
controlled allocator may return a buffer for unusual size words to test this
consumer's transport; this does not claim the real allocator accepts them.

All six `/O2 /GS` mutations fail: late group snapshot, early flags snapshot,
transform loaded before close, new read-result guard, omitted free, and
booleanized pointer return. Attempt001 stopped after successful compilation
because the first COFF assertion permitted only function symbols and rejected
the three optimized string COMDATs. The bounded assertion was corrected before
the first native execution; attempt002 passed both variants in that first batch.

Receipts pin the original PE/body/literal bytes, source/header/template,
canonical globals,193 actual transitive inputs, compiler/DLLs/linker, SDK/CRT
libraries, commands, dependency records, logs, actual COFF and executables.
Dependency probes precede authoritative compilation, with input guards before
and after compilation/link/execution. All current input/output pins were
rechecked after completion. No successful native proof was rerun for metadata.

The fixture owns controlled file/heap/dispatcher/diagnostic/transform effects.
It proves this consumer against those observed ABI/state contracts; it does
not claim a real filesystem, allocation backend or complete running game.

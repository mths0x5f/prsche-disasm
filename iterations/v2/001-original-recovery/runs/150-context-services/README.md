# Run150: context string and vector services

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Binary-index query `004d3420` establishes an 8589-byte body with 408
indexed call sites and 134 distinct direct callees. This packet recovers
eleven coherent helpers reached there: `00423610`, `00505810`,
`004d55c0`, `004d64a0`, `004298a0`, `00429bf0`, `00429840`,
`004d6510`, `004d6520`, `004d6530`, and `004d67b0`.
Each complete ASM body, its caller argument setup, and direct callees
were inspected. Inclusive body ranges/SHA pins are in verification.json.
The large `004d3420` consumer itself remains unrecovered.

Confirmed contracts:

- `00423610` returns ECX unchanged. `00505810` clears exactly three
  DWORDs, returns ECX, and discards one ignored stack argument.
- `004d55c0` reproduces the source's bounded REPNE SCASB counting:
  initial ECX=0xffffffff, stop on NUL or exhaustion, return ~ECX-1.
- `004d64a0` clears the destination before scanning its source string,
  captures length/end, initializes capacity length+1 if unsigned capacity
  is at most 0xfffffffe, copies length bytes, then stores end and writes
  the NUL byte. It returns the original destination and pops eight bytes;
  its second stack argument is unused.
- `004298a0` initializes from a pointer range without first clearing the
  destination. It uses the same unsigned capacity test. It returns the
  final character pointer, not the object, and pops eight bytes.
- `00429bf0` clears destination fields before loading source end then
  source begin. Source/destination aliasing therefore changes the input
  before it is read. It returns the destination and pops four bytes.
- `00429840` releases a non-null nonempty storage span through the
  original pool or manager callback. It captures bounds before locks and
  reloads the lock slot before leave. No fields are synthetically reset.
- `004d6510` subtracts pointers modulo 32 bits then performs signed SAR2.
  `004d6520` computes begin+index*4 modulo 32 bits. `004d6530` decrements
  end by four without an empty guard. `004d67b0` compares two DWORDs and
  returns exactly zero or one.

The private native MSVC Win32 Release probe compares 64 cases with
original x86. Every case compares the complete 20480-byte poisoned arena,
defined EAX results, ordered boundary effects, original stack cleanup and
nonvolatile registers. Cases cover empty/long/unaligned strings,
source/object/allocation aliases, overlapping copy ranges, callback
mutation of source bounds and destination fields, bypassed allocation
for unsigned capacity 0xffffffff, null/empty/small/large/reversed release
spans, negative/unaligned pointer differences, wrapping indexes and empty
pop, identical/overlapping comparison inputs, and two composed sequences.

`005a1a40` remains an explicitly typed copy boundary. Its body is pinned
for navigation, not accepted here. The fixture records every call and
uses controlled copy effects. In reversed-range case20 it records length
0xfffffffe and intentionally copies no bytes, allowing the original
consumer's unsigned allocation guard and final pointer arithmetic to be
compared without claiming that huge-range copy semantics are recovered.
This behavior exists only in the private fixture. Canonical pool allocator,
manager release, locks and storage accessor remain existing boundaries.
No guessed global owner or production stub is introduced.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/150-context-services -B local/builds/v2/context-services-150 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/context-services-150 --config Release
py -3 scripts/research/verify-v2-context-services.py --probe local/builds/v2/context-services-150/bin/Release/context_services_probe.exe --report-dir iterations/v2/001-original-recovery/runs/150-context-services
```

Result: eleven full functions; all 64 comparisons passed. The report
records source closure and verifier SHA, compiler/PE architecture, original
body/global pins, fixture hashes, probe SHA and per-call ABI checks.
Shared integration, full context consumer, game launch and visual
acceptance remain coordinator-owned and open.

# Run158 — original CRT text and locale consumers

Source: Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Eleven full bodies: `005a2248` (111 bytes), `005a22b7` (203),
`005a262c` (111), `005a269b` (204), `005a2eae` (117),
`005a2c24` (46), `005a2c52` (40), `005a2c7a` (40),
`005a2210` (56), `005a2e70` (62), `005a2870` (39).

Queries: these VAs, callees and incoming callers in the original binary index
functions/calls/references; `InterlockedIncrement/Decrement` in static imports;
full ASM bodies. Examples of callers: `0045fb80 -> 005a2248`,
`0047d6b0 -> 005a262c`, `0052ffa0 -> 005a2eae`,
`004a5c30 -> 005a2c24`, `004a5f90 -> 005a2c52`,
`005a81a6 -> 005a2c7a`, `0045adf0 -> 005a2210`,
unpromoted callsite `0052bfc0 -> 005a2e70`, `004876e0 -> 005a2870`.

Confirmed behavior:

- Case conversion bypasses locale machinery when `006afd80 == 0` and changes
  only signed-int ASCII letter ranges. Locale entry increments DWORD reader
  counter `006c02e8` via IAT `005b2258` (Kernel32 InterlockedIncrement).
  A writer flag at `006c02e4` causes decrement through captured IAT `005b2254`
  (InterlockedDecrement), then CRT lock19. Without a writer, captured decrement
  executes after the inner conversion. Result survives unlock/atomic calls.
- Inner conversion reloads locale; values below256 first test the original
  upper/lower classification mask. Width>1 uses classifier; width<=1 reads
  the original table directly, including negative indices. High input byte's
  `0x8000` class bit selects one/two input bytes. The typed map receives
  flags100/200, capacity3, codepage0, strict1. Failure returns the original
  integer; return1 yields output byte0, all other nonzero returns combine
  output1:output0. No invented locale table or host case conversion.
- Classifier accepts the unsigned `(c+1)<=256` table domain (including EOF=-1).
  Other values construct a one/two-byte terminated buffer and call the
  typed classification engine with type1/codepage0/locale0/strict1.
  Failure yields0; success masks the output WORD. Alpha/digit/space wrappers
  preserve direct table reads or classifier dispatch according to width.
- Bounded compare first scans the entire bounded first string through its
  terminator, then compares unsigned bytes (first/second order in the x86
  oracle) and rereads the final pair in second/first order; return is exactly
  -1/0/+1. Zero count reads nothing.
- Reject-span builds the original eight-DWORD membership bitmap and scans
  until NUL/member. Reverse-find scans forward through NUL, then backward
  including NUL, rereads the result byte and returns the final match or null.
  Original STD/CLD leaves DF clear.

The source reuses canonical ctype pointer/width declarations and CRT lock
boundaries. New locale DWORDs have original BSS zero initialization. Typed
atomic callback cells preserve the captured decrement pointer across callbacks;
native OS adapters and unrecovered locale engines are explicit dependencies.

Private MSVC Win32 probe reads the original 514 table bytes (EOF +256 entries)
from the SHA-verified PE. Differential cases compare full poisoned arena,
ordered source/table reads, EAX, all boundary arguments, mutable locale state,
pointer capture, original stack cleanup/nonvolatile registers and DF. Synthetic
lead bits, locale changes during atomic/map/lock calls, map success/failure and
multibyte classifier failure are declared fixture inputs. Private read logging
follows volatile loads; no logging/observer is compiled in production.

Build and verify:

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/158-formatter-text -B local/builds/v2/formatter-text-158 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-text-158 --config Release
py -3 scripts/research/verify-v2-formatter-text.py
```

The report pins every full instruction span, original globals/table/import
identities, native PE32/toolchain, complete fixtures, and quoted include closure
including this verifier. Passing typed-boundary consumers does not recover
the locale mapping/classification engines or prove full game startup.

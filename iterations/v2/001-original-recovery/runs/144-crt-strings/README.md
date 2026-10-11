# Run144 — CRT strings and lazy dialog closure

Original Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Four full indexed functions: `005aa4e0`, `005aa4f0`, `005a28a0`, `005acfb9`.
The production symbols implement the exact typed string/dialog boundaries
declared by Run140; that packet remains unchanged.

Index queries: the four VAs in `research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl`,
their Run140 caller `005a976f` in `calls.jsonl`, and shared-jump/global cells
`005aa4e5→005aa551`, `006b001c/006b0020/006b0024` in `references.jsonl`.
Bodies were recovered from `research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm`.
The verifier pins original SHA, indexed bodies and caller edges, and separately
hashes shared suffix `005aa551..005aa5cf`. The seven-byte `005aa4e0` index
record alone does not describe a full copy implementation: its JMP uses that
suffix inside the concat record.

Confirmed implementation:

- Copy and concat preserve byte alignment scans, original `0x7efefeff`/
  `0x81010100` predicate, repeated DWORD reads, and terminator-dependent
  byte/word/DWORD stores. Concat scans the destination before entering the
  common source-copy suffix. Both return the original destination pointer.
- Copy-n preserves source alignment, remaining-count branches, DWORD snapshots,
  masking after the first zero, destination alignment during early zero padding,
  DWORD padding and final byte padding. A zero count returns without accessing
  source or destination. No host strcpy/strcat/strncpy implementation is used.
- Dialog lazily loads `user32.dll`, resolves `MessageBoxA`, `GetActiveWindow`,
  `GetLastActivePopup`, and stores all three mutable pointer cells. Load failure
  or missing MessageBox returns zero. Optional owner callbacks are consulted
  in original order; popup and message cells are reread after earlier callbacks.
  The final MessageBox return is propagated unchanged. There is no invented
  cache lock, fallback owner, error dialog or library unload.

The private MSVC Win32 probe instruments source memory primitives only under
`PORSCHE_FORMATTER_MEMORY_TRACE`; production has no observer. For each string
input, the verifier compares the entire1024-byte memory arena, return pointer,
and exact ordered `(read/write,offset,width,value)` tuples with original x86
Unicorn execution. Cases cover all source/destination alignments, NUL positions,
short/exact/truncated counts, padding, high-byte predicate inputs, self copy,
downward overlap and bounded forward-overlap word propagation. Nonempty concat
self-overlap and unterminated/unmapped strings are not claimed valid.
All3121 string and170 lazy-dialog cases pass:18005 ordered reads and17047
ordered writes match exactly. A second probe compiles the same source without
instrumentation and repeats all3291 cases, checking identical final memory,
returns and dialog events. This prevents a proof that depends on the observer.

Lazy-dialog cases compare two consecutive calls, callback state, returns and
ordered API/callback arguments. They cover all resolution masks, preseeded
caches, null/non-null owners, load failure, absent optional callbacks, and
mutation of popup/message cells by owner callbacks. OS functions and resolved
window/dialog callbacks are recording boundaries, not live Windows acceptance.

Reproduce:

```powershell
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' -S iterations/v2/001-original-recovery/runs/144-crt-strings -B local/builds/v2/formatter-strings-144 -A Win32
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' --build local/builds/v2/formatter-strings-144 --config Release
py -3 scripts/research/verify-v2-formatter-strings.py --probe local/builds/v2/formatter-strings-144/Release/formatter_strings_probe.exe --production-probe local/builds/v2/formatter-strings-144/Release/formatter_strings_production_probe.exe --report-dir iterations/v2/001-original-recovery/runs/144-crt-strings
```

Next: integrate the four bodies and two OS import bindings into the common
game target; compose with Run140 fatal path, then continue the float/lowio
closure. No registry, common build, existing packet or game data is edited.

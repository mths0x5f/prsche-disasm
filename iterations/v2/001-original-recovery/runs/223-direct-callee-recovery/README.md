# Run223 — original direct callee00565ea0

One isolated real i386 C++ COFF now defines Run211's exact required symbol
`?FUN_00565ea0@@YAIPAXI@Z`: uint cdecl(void*,uint). Original Porsche SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Frozen180 getC source and179 declarations are pinned. No Ghidra, production,
union, registry, game data, completed-run or shared-plan changes.

Index query00565ea0/00565e70 then direct callees00590070/00590170/005907b0.
All38 instructions/93B of the target match original PE. Canonical exact/interior,
recovered WIP definitions and current222 compiled packet contain no target owner.
Original211 caller pushes0 then inputpointer and cleans8. Callee consumes only
stack+4 data pointer, never reads stack+8, returns EAX32 through two RET0 paths.
Opaque void* establishes no invented object/class/pointee layout.

Original565ea6 reads one signed BYTE at input+4, not printed DWORD[1].
Original565ed5 PUSH EDI is retained across590170: ADD ESP,8 pops only its two
arguments. That retained pointer is the third argument of5907b0, whose first
argument reloads the table through DAT006b4a04 after590170. Printed getC assigns
the third argument to the wrong call. The recovered body keeps signed index
comparisons, zeroextended WORD+6 limit, modulo32 signedbyte*12 address arithmetic,
original load order, repeated global/table read and raw32 return representations.

One /MP6 batch with one gameTU and one fixtureTU: exit0,1.497861s, no warnings;
exit/time written before parsing. One measured native consumer RET0, two original
RET0 paths. Raw-copy intrinsics compile to actual DWORD/WORD loads and preserve
unaligned storage without CRT memcpy dependency. Byte input remains a BYTE load.
Native symbols and complete disassembly are pinned; ordinary204 schema includes
only the game object, not controlled fixture definitions.

Actual corrected body passed229376 original/native comparisons in0.431399s.
The original reference is exactly93B after masking five proven COFF relocations:
all opcodes/branch distances match original PE, and every CALL/global relocation
names the corresponding controlled boundary. Comparisons cover all256 signedbyte
inputs,7 signed index patterns,4 unsignedWORD limits,4 guard return bitpatterns,
table reload changed/unchanged, four input alignments and distinct unused slots.
Raw EAX, complete direct-call traces and final table-global bits match.
These controlled boundaries are not implementations of nested game/provider callees.

Independent audit PASS:38 pins before/after,307 bounded original PE instructions,
actual i386 symbols, five reference relocations and source/native receipts.
`proof-before-compile.json` contains original caller/callee/consumer instructions,
lost-dataflow witnesses and contracts. `summary.json` is the reusable one-object
packet; `validation.json` freezes the independent checks.

Remaining dependencies:00590070 and005907b0 implementations;00590170 already has
the exact compiled native symbol `?FUN_00590170@@YAHHH@Z` and is reused without edits.
DAT006b4a04 needs its canonical owner/initializer. Nested providers, lifetime,
concurrency/atomicity, faults, incidental registers and whole-game fidelity remain
open. This bounded callee result is not acceptance of those dependencies.

```powershell
py -3 scripts/research/audit-v2-direct-callee-223.py
```

The experiment driver requires fresh output and cannot recompile a completed run.

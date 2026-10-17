# Run267 — canonical heap table evidence, HOLD

Do not allocate or coalesce the table yet. A full original PE HIGHLOW scan finds
four operand sites missing from the ASM instruction index. The coordinator
accepted this HOLD. This packet changes no source, provider, index, registry,
union or production artifact and runs no compiler, native code or Ghidra.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Query: `006b4f20..006b4f5f`, including the one-past boundary `006b4f60`, in the
PE relocation directory, versioned disassembly/catalog, canonical sources,
Run179 storage export, registry and actual Run264 native dependency objects.

The 64-byte candidate span is writable, non-executable `.data` virtual tail.
Its original loader-initial bits are 64 zero bytes; they are not file-backed
zeros. No HIGHLOW relocation site overlaps those cells. The original slot scan
at `00569a70..00569a8b` starts at `006b4f2c` (slot3), reads DWORDs, advances by4,
and compares against `006b4f60` (one past slot15). This supplies extent evidence
beyond the flags&15 selectors. Original metadata describes cells at base, base+4
and base+12, not an exported 16-element array type. The next cell at `006b4f60`
has separate low-I/O consumers and is outside the candidate span. The preceding
`006b4b20..006b4f1f` loops use `006b4f20` only as an exclusive end address.

Confirmed indexed writes:

- `005698f9` in accepted heap_init `005697f0`: stores `memory+16` at
  `006b4f20+4*(index&15)`. The pointer computation and store windows are pinned.
- `00569a02` forms that indexed cell's address; `00569a2a` writes zero through
  it in `005699f0`, after clearing its heap object.
- `005aefb3` in accepted primary initialization `005aef80` copies slot0 to slot1
  after heap_init(0). Canonical `application_heap_init.cpp` uses the same extern
  table, the same alias, and the same bounded slot scan.

All 56,746 PE HIGHLOW entries were checked. There are 30 references to the span
or its one-past boundary; 26 have exact PE-matching ASM instructions, four do
not. The four missing sites all contain base `006b4f20`:

- Operand `005697d5`: candidate PUSH at `005697d4`.
- Operand `00569a4b`: candidate indexed DWORD load at `00569a48`.
- Operand `00569b1e`: candidate indexed DWORD load at `00569b1b`.
- Operand `0056a222`: candidate CMP at `0056a221`, apparently an exclusive
  endpoint of a preceding-object loop.

The listed instructions `00569ada` and `005aef2d` also lack containing function
catalog ranges. No owner or function entry is invented for these gaps.

`gap-windows.json` preserves four exact PE windows / 166 bytes, candidate
instructions and nearest indexed boundaries. No indexed direct CALL to the
four candidate window starts was found; this is not whole-program absence
proof. Starts and nearby boundaries are:

- `005697d0` /23B: previous `00569640..005697c2`, next
  `005697f0..005699eb`. Raw bytes
  `6a406a0068204f6b00e8b22afdff83c40cb801000000c3` pass `(006b4f20,0,64)` to
  `0053c290`, then return1. The latter is a multi-path fill-dispatch boundary;
  complete filler semantics and reachability are unproved here.
- `00569a40` /43B: previous `005699f0..00569a37`, next
  `00569a70..00569a8b`; indexed heap-cell read followed by block traversal/free.
- `00569b10` /44B: previous `00569a90..00569aca`, next
  `0056a490..0056a4b8`; indexed heap-cell read and block-size accumulation.
- `0056a1f0` /56B prefix: the same nearest catalog boundaries; preceding-object
  DWORD loop ending at base. Its full function extent is not claimed.

These raw decodes are navigation only. Alignment, NOP padding and successful
Capstone decoding do not establish executable function entries.

Canonical storage already exists at `source/recovered/Porsche.exe/heap.cpp:7`:
`OriginalHeap* heaps_006b4f20[16]`, declared in `source/include/porsche/heap.hpp`.
Those current files match the accepted Run078 source SHA records. Fourteen
accepted heap/application-init entries are recorded; this is a data VA, not a
new function. The only other source definition is the private
`application_heap_init_probe.cpp` fixture, which must not be treated as a second
production owner.

Actual cached native owner:
`local/builds/v2/001-original-recovery/porsche_original.dir/Release/heap.obj`,
SHA256 `ebeba962dcfe53edd81ce86cf84f0cf0f6a40e2adb917fac09fccd6220e0ba7a`.
It defines exact symbol `?heaps_006b4f20@porsche@@3PAPAUOriginalHeap@1@A` at
offset0 of writable, non-code `.bss`; the next external symbol starts at64,
and that section has no relocations. The cached application_heap_init object
references this same symbol; the private probe object defines its fixture copy.
These actual objects/symbols are pinned. The whole heap TU contains accepted
algorithm definitions and other data, so it cannot be added wholesale to the
union as a table provider. No fresh/source-equivalent cached code proof is
claimed beyond the actual storage/symbol inventory and accepted source hashes.

Current Run264 also needs raw `?DAT_006b4f20@@3IA` from two actual candidate
objects (`00531c60`, `00556620`), while canonical free `00531f90` needs the typed
array symbol. These are views of the same original base. No current support
storage overlaps the span. A future provider/coalescing packet must preserve
one physical owner; this evidence does not authorize a second scalar or any
linker alias. Original relative layout with neighboring globals is unclaimed.

Commands from the repository root (both refuse completed output):

```powershell
py -3 scripts/research/audit-v2-heap-table-evidence-267.py
py -3 scripts/research/trace-v2-heap-gap-windows-267.py
```

The primary report has 40 before/after pins and actual native/PE/storage checks.
The supplementary windows independently pin the primary summary and exact PE.
Next: prove the four missing consumers' entry/control-flow boundaries and fill
dispatch contract, repair index coverage under coordinator ownership, then
review a canonical single-table reuse/provider and the raw-base view separately.

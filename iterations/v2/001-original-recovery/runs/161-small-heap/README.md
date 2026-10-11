# Run161: original CRT small-block heap

Source: Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
Index queries followed allocator 005aad00 and free 005aa9d5 through callers/callees:
`rg -n '005aa96c|005aa9d5|005aad00|005ab009|005ab0ba|005ab1b5|005a8029|005a8161|005a96fa|005a7ad0' research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl`
and `rg -n '005ab009|005ab0ba' research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl`.
Semantics were checked in the matching full `disassembly.asm`, including size
rounding/copy/new-handler branches 005a807e..005a814f and free/commit metadata consumers.
Recovered full bodies: 005aa96c, 005aa9d5, 005aad00, 005ab009, 005ab0ba,
005ab1b5, 005a8029, 005a8161, 005a96fa and copy alias 005a7ad0.
Nine contiguous bodies cover 3277 bytes; indexed copy alias adds 664 bytes.
The 835-byte complete copy span equals recovered154 005a1a40 after original
internal HIGHLOW relocation rebases, validated against both PE relocation sites.

The implementation preserves the original 20-byte header table, 0x41c4-byte
metadata, 32 groups per 1 MiB reservation, 64 free-size lists, tail allocation,
coalescing, pending empty-group decommit and header compaction. Realloc uses
original size rounding, copy length and new-handler ordering. OS heap and virtual
memory effects remain typed boundaries; production does not substitute host malloc.
Four new BSS globals are 006c01c0/c4/c8/cc. Canonical157 heap/header/lock storage
and original malloc/free/header lookup are reused, together with recovered154 move.

Private MSVC Win32 verification builds actual connected production bodies. The
original-x86 oracle executes all CRT callees and hooks only explicit Win32 imports,
fatal and new-handler boundaries. A private fixed-address fixture makes pointers
identical. Every case compares returns, allocator globals, ordered API effects and
full bytes of allocated metadata/header/OS buffers and committed groups. Inputs
cover all 64 bin transitions, coalescing, resize/realloc, table growth, allocation/commit failure,
pending-group decommit, region release, compaction and copy alignment/overlap.
2315 cases passed. Each recorded return and each external boundary also compares
SHA256 of the seven allocator globals and every tracked memory buffer; this
checks intermediate states in addition to the final exact-byte comparisons.
New-handler fixtures cover failure and one successful retry. Every original
call checks cdecl stack cleanup, nonvolatile registers and cleared DF. Ten native
inline-assembly sentinel cases check ESP/EBP/EBX/ESI/EDI and DF at all ten entries.
The copy alias proof additionally requires package154's current source closure
and its 130440 exact ordered memory-access comparisons.
The decommit fixture preserves readable memory for snapshots and does not assert
live VM protection parity. Raw operations require valid allocator metadata and
allocated pointers. No game launch or visual acceptance is claimed.

Commands (repository root):

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/161-small-heap -B local/builds/v2/formatter-small-heap-161 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-small-heap-161 --config Release
py -3 scripts/research/verify-v2-formatter-small-heap.py --probe local/builds/v2/formatter-small-heap-161/Release/formatter_small_heap_probe.exe --report-dir iterations/v2/001-original-recovery/runs/161-small-heap
```

Verification metadata pins function bytes, original module SHA, copy alias proof,
case results and full compiled source/header/verifier closure. Files use UTF-8 LF.
Ready for coordinator integration; no shared registry, platform binding or common
CMake change is part of this packet. OS imports require canonical native bindings
at integration; this private fixture does not prove their live VM semantics.

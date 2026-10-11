# Run154: exact context move access ordering

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Binary-index query `005a1a40` resolves one complete body: 664 indexed
instruction bytes in 21 discontiguous ranges within `005a1a40..005a1d74`.
There are eight return exits and 118 indexed call sites. Callers include
context range/string consumers `004298a0`, `00429bf0`, and `004d64a0`.
Every instruction and the six alignment/count/tail tables were inspected.
Body ranges and jump-table bytes/SHA are pinned in verification.json.

The source preserves the unsigned original direction predicate:
backward only when `destination > source && destination < source+bytes`,
where addition wraps modulo 32 bits. Forward copying first emits byte
accesses needed to align destination when length is at least four, then
ascending DWORD read/write pairs, then ascending byte tails. Backward
copying aligns the exclusive destination end with descending byte
accesses, emits descending DWORD read/write pairs, then descending byte
tails. Length below four bypasses alignment and uses only byte accesses.

The original short jump-table path and REP MOVSD path have identical
observable ordered DWORD access sequences; the recovered C++ expresses
them using loops. Every individual read precedes its corresponding write.
Volatile byte/DWORD accesses retain the source widths and self-copy
effects. This implementation does not call host memcpy/memmove, skip
self-copies, or replace DWORD accesses with byte loops. All exits return
the original destination. Win32 x86 ABI requires DF clear on entry; the
original restores it after backward REP MOVSD and all tested exits leave
it clear.

The private MSVC Win32 Release probe observes actual native reads/writes
using PAGE_GUARD and a vectored exception handler. After each guarded
access, a single-step exception restores the guard. The observer decodes
the native MOV/MOVZX access width, captures read values before execution
and write values from the fault context, and records ordered address,
width and payload. It does not alter the recovered body. The verifier
compares this trace with original x86 Unicorn memory hooks, alongside the
complete 12288-byte poisoned arena, EAX, original cdecl stack cleanup,
nonvolatile registers and DF. Native instruction opcodes are independently
validated and summarized in the report.

3215 cases cover every source/destination alignment for lengths 0..40
and 63/64/65/127/128/129/255/256/257/511; destination above/below a
disjoint source; exact self-copies; forward/backward overlaps with offsets
1/2/3/4/7/8/15/31 where overlap exists; and three null-pointer zero-length
contracts. This includes the short/REP boundary at eight DWORDs and all
byte tails. The fixture places all copied ranges within one guarded page
so an access cannot escape observation. Outer arena canaries are compared
without omissions. Arbitrary invalid pointers and enormous ranges are
not converted into supported inputs.

The canonical symbol is `context_move_005a1a40`, declared by Run150's
context services header. The new header reuses that declaration. There
are no unresolved dependencies or production substitutes in this body.
Run150's historical boundary proof remains unchanged; common integration
and any connected string-consumer revalidation belong to the coordinator.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/154-context-move -B local/builds/v2/context-move-154 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/context-move-154 --config Release
py -3 scripts/research/verify-v2-context-move.py --probe local/builds/v2/context-move-154/bin/Release/context_move_probe.exe --report-dir iterations/v2/001-original-recovery/runs/154-context-move
```

Result: one full function, 3215 exact native/original comparisons passed.
Verification records source closure, verifier/compiler/probe SHA,
architecture, original body/table pins, per-case fixture/access hashes,
native access-opcode counts and ABI checks. Game launch and visual
acceptance remain open and coordinator-owned.

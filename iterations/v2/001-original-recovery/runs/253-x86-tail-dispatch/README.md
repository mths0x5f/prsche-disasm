# Run253 — isolated x86 tail dispatch

Three original wrappers now lower to C++ VM statements and an explicit direct
tail transfer. The dispatcher records the original target PC and `MissingEntry`
when that target has no generated VM entry. No original callee, typed native
binding, production change, union packet or newly accepted function is supplied.

Source: `Porsche.exe`, SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query: `00468100`, `004d8230`, `004d8240` in the versioned Porsche catalog
and disassembly, checked against the PE bytes before generation.

- `00468100`, 8 bytes: `MOV ECX,[ECX+0x74]; JMP 00536050`.
- `004d8230`, 11 bytes: `MOV ECX,[ECX+0x264]; JMP 004c7e10`.
- `004d8240`, 11 bytes: `MOV ECX,[ECX+0x264]; JMP 004c7df0`.

The offsets are hexadecimal (116 and 612 decimal). Registry exact/interior and
canonical WIP definition preflight found no selected owner. The frozen Run246
finite-width lowering is inherited mechanically; direct immediate JMP is added
generically, with instruction-boundary checks for internal targets. Indirect JMP,
CALL, x87, malformed instructions and open fallthrough remain rejected. Selected
generated bodies contain a DWORD read and a dispatcher transfer; they synthesize
no guest RET or stack adjustment. Original machine code executes only in the
comparison fixture.

One actual 5-TU `/MP6` compile passed in 1.7115481999935582 seconds, exit 0, with
zero warnings. `/showIncludes` is absent. Source/include closure is the five
recorded C++ roots and the single pinned `machine253.h`; the roots include no
other headers. Compile/link/native commands, measured exits and durations were
written to durable receipts before assertions or output attribution. No retries
or recompilation were needed. The actual five Win32 COFFs and linked fixture
are pinned in `summary.json`.

The native fixture passed 18,432 cases in 0.6593246000120416 seconds:
3 wrappers × 8 receiver alignments × 6 DWORD values × 16 CF/ZF/SF/OF patterns ×
8 register seeds. Values include zero, one, `7fffffff`, `80000000`, `80000001`
and `ffffffff`. All eight GPRs, unchanged raw ESP, the four observed flags,
unchanged VM flags, and the unchanged 768-byte controlled memory arena agree.
Each original wrapper COFF contains its exact original MOV prefix and terminal
JMP; **only the JMP REL32 operand** is normalized to a controlled capture hook.
The hook records state before fixture effects and jumps to the host continuation;
it has no RET and supplies no callee behavior. The harness's eventual RET is
fixture transport. Hook globals/private stack traffic after the cutpoint are
outside the original memory comparison.

The actual generated dispatcher observed 18,432 missing-entry events and wrote
`local/experiments/v2-x86-tail-dispatch-253/runtime-misses.json`, with the original
module/SHA, the three original callee PCs, `provenance: isolatedVMpilot`, and
`native_game_execution: false`. This report is SHA-pinned. The frozen Run245
runtime-input parser was called only as an identity test, including wrong-SHA
rejection. Its result is wrapped in `runtime-parser-identity.json` to preserve
the provenance the parser itself does not retain. No planner CLI or queue update
ran; the existing Run245 queue was pinned before and after. These VM dispatch
misses do not assert missing native bodies or execution of a game EXE.

Commands from the repository root:

```powershell
py -3 scripts/research/experiment-v2-x86-tail-dispatch-253.py
py -3 scripts/research/audit-v2-x86-tail-dispatch-253.py
```

The first command requires fresh output and refuses a completed summary. The
second performs only a read-only independent audit and writes validation: 49
input pins, actual PE/COFF/oracle/hook bytes, generated sources and symbols,
8 lowering guards, measured receipts, runtime identity/provenance and queue
exclusion all pass. It runs no compiler, linker, native fixture or Ghidra.

Limits: controlled native32 memory only; no guest memory loader, CALL/imports,
x87, original-callee/provider fidelity, complete CPU equivalence or game launch.
The earlier lost-receiver native ABI contracts remain deferred. Stop scope is
exactly these three wrappers; accepted function count remains zero.

Versioned `runtime-misses.json` is an exact copy of the SHA-pinned native fixture output; it retains isolatedVMpilot provenance and is not fed into the native-game queue.

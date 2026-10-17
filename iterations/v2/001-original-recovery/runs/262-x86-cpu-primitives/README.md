# Run262 — synthetic CPU primitives

The frozen Run257 backend passed 15,744 native comparisons for previously
unexecuted arithmetic, register views, stack aliasing and indirect transfers.
These are **synthetic CPU infrastructure tests**, not original Porsche functions.
No accepted function, provider, native FUN binding, production change or union
packet is added. Backend257 is unchanged, SHA256
`fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc`.

The coordinator approved the 19 fragments / 70 bytes and case counts before
native execution. `proof-before-compile.json` records every byte, synthetic PC,
ASM reference and generated statement. All 19 actual native oracle COFF bodies
match those bytes exactly, with **zero oracle relocations or byte normalization**.
The synthetic entry range is `10001000..10002200`; these are not game VAs.

- ADD/SUB/SBB AH,CL; AX,CX; EAX,ECX and NEG AH/AX/EAX: 9,600 cases.
- MOV AH,CL followed by MOV DX,AX, preserving other register bits: 1,024 cases.
- PUSH ESP/POP EAX, POP ESP, and POP DWORD[ESP]: 3,072 cases.
- CALL DWORD[ESP] and tail JMP DWORD[ESP+4], into an actual synthetic
  NEG EAX/RET leaf: 2,048 cases.

Arithmetic uses the eight width-specific values zero, one, max unsigned,
max signed, min signed, min signed+1, max unsigned−1 and two. Binary operations
cover every pair and all 16 CF/ZF/SF/OF input patterns, including both carry
states. NEG covers every value and pattern. AH/word preservation is compared in
the complete GPR state. Stack/indirect cases cover eight unaligned stack offsets,
eight register seeds and all 16 input flag patterns. Defined CF/ZF/SF/OF are
compared with actual hardware; PF/AF and undefined flags are outside scope.

The fixture uses a valid 256-byte native32 guest stack arena and compares every
byte after execution, plus all eight GPRs, flags, final PC/stop and expected ESP.
The native capture hook saves registers and restores host ESP before PUSHFD,
leaving guest stack residue intact. PUSH ESP must store the old ESP. POP ESP must
read old [ESP], increment, then assign the popped pointer. POP[ESP] must compute
its destination after incrementing ESP. All three order-sensitive cases agree
with native hardware.

CALL[ESP] reads its target before CALL decrements ESP and pushes the synthetic
return PC. The generated source explicitly evaluates that read before call257;
the actual native CALL uses the old top-of-stack target. It returns through the
real synthetic leaf and resumes after CALL. Tail JMP[ESP+4] reaches the same leaf
without a return push. Only declared synthetic codepointer/return slots are
mapped between native addresses and synthetic guest PCs. Each native slot is
checked before mapping; no register values or arbitrary pointers are normalized.
The full stack comparison passes with 19,840 exact slot mappings in total.

One 2-TU `/MP6` compile passed, exit 0, in 1.2773309999611229 seconds, with zero
warnings. One linked fixture passed in 0.4405999999726191 seconds. The generated
root and fixture include only the pinned machine257.h. MSVC Win32 emits the
`__aullshr` CRT dependency for add257's U64 shift; the actual object symbol and
pinned linked CRT libraries are recorded. The first audit expectation omitted
that helper; it was corrected to the actual exact undefined symbol set. No
compiler, linker, native code, generated source or frozen backend was rerun or
changed for that audit correction.

Unique `compile-001`, `link-001` and `native-001` receipts/logs preserve the actual
commands, cwd, exit and timing before assertions. Existing attempt names cannot
be overwritten. No retries occurred. The actual `fixture-result.json` records
15,744 cases, zero failures, all group counts and exact slot count, with
`provenance: syntheticCPUfixture` and `native_game_execution: false`.

Commands from the repository root:

```powershell
py -3 scripts/research/experiment-v2-x86-cpu-primitives-262.py
py -3 scripts/research/audit-v2-x86-cpu-primitives-262.py
```

The experiment requires fresh output and refuses a completed summary. The second
command only reads artifacts and writes validation; it does not compile, link or
execute native code. Independent audit passes 28 input pins, actual COFF oracle
bytes, deterministic generated source, target/stack ordering, native capture
hook, symbols, result counts and unique measured receipts.

Limits: finite selected register combinations and edge sets, valid memory only,
no fault/segment/exception/concurrency claims, no full ISA or complete CPU proof.
Only the selected indirect CALL/JMP forms are covered. This test neither repairs
lost-receiver native ABI contracts nor executes the game or feeds a frontier queue.

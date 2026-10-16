# Run258 — three closed original CALL chains

The frozen Run257 backend translated six original bodies into C++ VM functions.
An actual native fixture passed 36,864 end-to-end comparisons of the three closed
chains, including all eight GPRs, defined CF/ZF/SF/OF, memory effects, guest return
slots, ESP and callee cleanup. This is an isolated backend pilot: **zero newly
accepted functions, no union packet, no game EXE execution or native FUN alias**.

Original: `Porsche.exe`, SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Backend: `scripts/research/x86-cpp-backend-257.py`, frozen SHA256
`fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc`.

- `00515ca0` (18B) → `004bc610` (5B): PUSH/POP ESI, direct CALL, byte stores,
  AL XOR, RET0. The native CALL return address maps to original PC `00515ca8`.
- `00466e60` (29B) → `00466e80` (9B): stack argument, DWORD memory effects,
  ADD ECX, callee RET4 and caller RET4. Return PC is `00466e7a`.
- `004cecc0` (20B) → `004e0dc0` (23B): nullable receiver, TEST/JE, two PUSH0,
  callee RET8 and caller RET0. Return PC is `004cecd3`.

The indexed selection scanned only single-span bodies ≤96 bytes and call-free
callees ≤64 bytes, with the stated instruction/operand subset. It found 13 closed
candidates among 2,949 bounded bodies; `selection.json` preserves their bytes and
navigation. The approved three chains contain 104 bytes / 34 instructions, no
absolute global operands and no unknown/indirect edges. Each indexed body was
checked against the actual PE before generation. Selection was reported to the
coordinator and approved before native execution.

Exact registry owners, registry interior overlaps and canonical WIP definitions
are absent for all six VAs. Existing `00466e80` references in
`application_context_core_candidate.cpp` / `render_display.cpp` are boundary
calls, not definitions. Three callees already have ordinary candidate COFFs in
Run249 (`004bc610`, `00466e80`, `004e0dc0`); their source/object identities are
pinned as existing candidates. This fixture compares generated VM code against
original native oracle instructions; it does not execute or certify those cached
candidate COFFs and does not replace their ownership.

One 8-TU `/MP6` batch passed, exit 0, in 2.2426681000506505 seconds, with no
warnings. The generated roots include only the pinned `machine257.h`; the fixture
also declares its explicit memcpy/Win32 test boundaries. `/showIncludes` is absent.
Actual compiler/linker/native commands, cwd, exits and timings were written to
durable receipts **before** assertions or diagnostic attribution. No retry or
recompilation occurred. The native fixture passed in 2.063936599995941 seconds.

Cases: 3 chains × 8 unaligned receiver addresses × 6 high-bit/zero/one DWORD
values × 16 CF/ZF/SF/OF patterns × 8 GPR seed sets × 2 receiver-presence cases.
The final factor exercises both JE paths for the nullable chain; the other chains
repeat with that factor unchanged. Both the 1,024-byte object arena and the full
256-byte guest stack agree byte for byte. Callee entry ESP and the guest CALL
return slot are checked at VM dispatch. Final ESP is entry+4 for RET0 callers,
and entry+8 for the RET4 caller, after the callee consumed its own arguments.

All six native oracle COFF bodies match the original PE exactly after normalizing
**only three direct CALL REL32 operands** to the corresponding oracle callees.
Internal branches, RET immediates, stack operations and memory operands are
unchanged. Native execution uses a dedicated guest stack arena; original RET
reaches a test capture hook. The hook saves all GPRs, then restores host ESP
before PUSHFD, so capture cannot overwrite guest stack residue. Its eventual
jump/host continuation belongs only to fixture transport.

Two precise slot mappings reconcile native and guest PCs: the initial native
capture return address maps to guest sentinel `0badf00d`, and an executed CALL's
native oracle address plus verified offset maps to its original return PC. Each
native slot is checked before replacement. The conditional chain's unused CALL
slot is not normalized on its no-CALL path. No arbitrary pointer or whole-stack
normalization occurs.

Four explicit negative checks pass: unknown dispatcher target → MissingEntry;
unknown CALL target preserves MissingEntry after pushing its original return PC;
an actual generated callee followed by test-only returned-PC corruption →
BadReturn with no caller continuation; zero instruction budget → BudgetExhausted.
DIV, truncated CALL, x87 and INT3 inputs are rejected before compilation.
`local/experiments/v2-x86-call-chain-258/fixture-result.json` records the actual
case count, zero failures and two **synthetic** missing-entry events. Its module,
SHA, `provenance: isolatedVMpilot`, scope and `native_game_execution: false` are
pinned. No main frontier queue is fed and no original callee is missing here.

Commands from the repository root:

```powershell
py -3 scripts/research/select-v2-x86-call-chain-258.py
py -3 scripts/research/experiment-v2-x86-call-chain-258.py
py -3 scripts/research/audit-v2-x86-call-chain-258.py
```

The experiment requires fresh output and refuses a completed summary. The audit
does not compile, link, execute native code or invoke Ghidra. Independent audit
passes 59 input pins, actual PE/COFF/oracle/hook bytes, deterministic generated
sources, symbols, return-slot mappings, observed native result and durable
receipts. Its result is `validation.json`.

Limits: only the selected six original bodies receive native proof here. Other
Run257 capabilities, including SUB/SBB widths, POP[ESP], high-byte/word views and
indirect transfers, remain outside this fixture's native proof. Flags coverage
uses the actual valid native addresses/operands; it does not cover every possible
arithmetic input. There is no full guest memory loader, complete CPU claim,
Win32/TLS/allocator substitution, typed lost-receiver ABI repair or game launch.

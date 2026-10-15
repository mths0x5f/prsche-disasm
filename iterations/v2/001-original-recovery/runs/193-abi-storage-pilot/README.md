# Run193 вЂ” restore lost call inputs from original x86 storage

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query: Run186's counterexample callers00483290/00489370, their callees
00482f70/00489530, original disassembly and Run179 inferred parameter storage.

Four functions are decompiled before and after two callee-only CUSTOM_STORAGE
corrections in an independent copy of the analyzed project. All receiver/stack
slots are raw undefined4; semantic types and object lifetimes remain unknown.
No analysis is rerun, and -readOnly discards the in-memory changes afterward.
The original project's78 files/572766909 bytes have identical before/after hashes.

-00489370 CALL00489386в†’00489530: original ECX=entry ECX, stack+4=ESI loop index,
 stack+8=entry stack+4. RET8 and both callee stack reads establish two slots.
 Before: high IR/getC had only index and stack argument. After: ECX/index/argument.
-00483290 CALL004832a1в†’00482f70: original ECX=DWORD[entry ECX], three pushed
 stack slots. Both RET12 consume all three; slot+c is unused locally.
 Before: three printed arguments were assigned to an incomplete prototype and
 the caller's incoming ECX vanished. After: receiver load plus all three slots;
 Ghidra also reinfers the caller's incoming ECX without manually overriding it.

The audit checks373 indexed instructions against immutable PE bytes, all local
RET sites, exact custom parameter storage, and high-IR CALL input producers.
It passes. This supplies a bounded correction mechanism; it does not authorize
blind changes to all42 Run186 mismatches, arbitrary thiscall rewriting or native
ABI/class acceptance.00489530's inferred void return is retained in this pilot;
its complete return/hidden-register contract and22 further calls remain open.
No game source or function registry is changed; accepted/candidate counts stay
at476full+6partial/1054distinct COFF VAs. No EXE is produced by this run.

Reproduce the Ghidra capture using a fresh attempt number (requires existing
analyzed project and local Ghidra/MSVC environment):

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/experiment-v2-abi-193.ps1 -Attempt 3
~~~

Validate the frozen successful capture without recompilation/Ghidra:

~~~powershell
py -3 scripts/research/audit-v2-abi-193.py
~~~

Successful capture: export/attempt-002. The earlier failed Windows project-path
attempt is preserved locally; it changed only its disposable copy, before any
ABI correction. Original project remained unchanged. Full high IR/Clang token
captures are retained to avoid repeating exports for alias investigations.

Next: select other RET mismatches with independently proven receiver/storage,
then repeat callee correction and verify every affected original CALL consumer
before applying native method lowering. Native compile/full-body behavior,
indirect calls, side effects and production integration remain in the backlog.

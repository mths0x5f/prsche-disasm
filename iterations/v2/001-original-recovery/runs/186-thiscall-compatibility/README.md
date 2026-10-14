# Run186 — native MSVC x86 thiscall pilot

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first inputs:179 inferred ABI records, the original address/range corpus,
disassembly and indexed caller graph. Accepted owners are excluded from the
12-body selection; no original resource, corpus or production source changes.

A nonvirtual C++ method preserves native ECX this and stack arguments. The
original explicit ECX parameter becomes a typed local view of `this`; only
the method declaration and that binding are introduced into the original
body. Every parameter/return width is asserted against179 metadata. Ordinary
stack parameters must occupy contiguous original stack slots; hidden returns,
varargs, unknown register values, unsupported float10 returns and nonstandard
storage are rejected. No cdecl or dummy-EDX fastcall replacement is used.

This matches the documented [MSVC x86 thiscall convention](https://learn.microsoft.com/en-us/cpp/cpp/thiscall).
The documentation supplies the compiler contract; local native tests and
original instructions supply the actual experiment evidence.

Two standalone native fixtures pass with MSVC19.44 `/Od` and `/O2`:
165 method invocations/403 checked conditions in each. They cover compiler
generated direct callers and raw assembly callers into real compiler generated
methods; ECX, stack argument order/cleanup, EAX, low AL/AX and x87 ST0 double
returns are checked. Raw observers preserve an EDX sentinel without supplying
a dummy argument. EDX is otherwise volatile; unknown original incoming EDX
remains unresolved. One-word method-pointer extraction is restricted to the
empty nonvirtual fixture class and is not a production address-lowering rule.

All12 selected original bodies compile into real COFF, and their original
RET immediates match the native stack parameter extent. Five relocation-free
COFF text sections exactly match the original body bytes:00466e80,00537a30,
0045fb00,00460c70,00537a40. This is bounded compile evidence, not an increment
to accepted function counts or a claim that unknown classes/lifetimes are proven.

The corpus-wide thiscall census does not compile the1301 functions. It checks
original catalog ranges/RET instructions against inferred parameter extents:
1258 match,42 disagree,1 has no local RET. The same1258 have Ghidra extra_pop
equal to stack extent plus the4-byte return address. A local RET match does
not prove tail-call paths, complete inferred types or all caller contracts.

Printed getC callers can omit the ECX receiver entirely. One bounded caller
is repaired from its original instructions:00466e60→00466e80. Instructions
00466e6c/6f establish `ECX_call = DWORD[ECX_entry+0x0c]+0xb8`;00466e6a stores
the original stack argument. The emitted call uses that receiver and preserves
param_2. Both bodies compile together; MSVC emits the same receiver loads/add,
then a tail jump to the callee, whose RET4 consumes the existing argument slot.
This explicitly traced binding is not generalized to other printed arguments.

Counterexamples prohibit a blanket rewrite.00489370 pushes two arguments
with ECX=EDI before CALL00489530;179 models only one stack argument and getC
prints two arguments without the receiver.00483290 loads ECX=[ECX] and pushes
three arguments to00482f70;179 omits the caller's incoming ECX and models only
two callee stack arguments. Treating printed argument zero as this would
silently change the original machine contract.

Unresolved: actual class/object lifetime/layout, missing call receivers/args,
evaluation order, qualified/literal-this identifiers, indirect/virtual calls,
function-address representation, hidden register/return contracts, and extended
x87 storage. No original machine bytes are executed and no interpreter is used.
No full1301 compilation or production integration was attempted.

```powershell
py -3 scripts/research/experiment-v2-thiscall-186.py --pilot 12
```

`summary.json` pins source/tool inputs, captures both native fixtures, every
pilot contract/COFF byte comparison, all1301 RET census rows and the traced
caller instructions. Generated C++, executables, COFF/symbol/disassembly files
and compiler logs remain in `local/experiments/v2-thiscall-186`.
Next: restore call receivers/stack contracts from original consumers before
extending method lowering; combine only proven ABI-compatible declarations
with184 body-scoped globals. Syntax success cannot waive a contract mismatch.

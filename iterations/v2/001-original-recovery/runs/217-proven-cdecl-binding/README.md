# Run217 — one proved unused-argument cdecl link binding

Frozen support packet; **zero new game functions**. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Only the211 consumer symbol`?FUN_00590290@@YAIII@Z` is weakly bound to the
existing216 candidate`?FUN_00590290@@YAIXZ`. The source contains one directive:

```cpp
#pragma comment(linker,"/alternatename:?FUN_00590290@@YAIII@Z=?FUN_00590290@@YAIXZ")
```

The actual i386 support COFF contains exactly that .drectve option, no .text
bytes and no external definitions/undefined symbols. It supplies no algorithm,
body, storage, wrapper or generic alias. Canonical exact/interior ownership and
WIP implementation checks remain clear; the already compiled candidate is
reused without replacing an implementation owner. The support object counts
as physical linker input, never as another recovered/compiled function VA.

Original00590290 is`33c0c3`: XOR EAX,EAX;RET0.211 proves the concrete caller
passes two locally unused raw32 slots and performs ADD ESP,8. The actual cached
COFF is independently checked: its sole code body is`558bec33c05dc3`, with
PUSH EBP/MOV EBP,ESP/XOR EAX,EAX/POP EBP/RET0, zero relocations, no argument
read or undefined symbols. EBP is restored; EBX/ESI/EDI are untouched. The exact
target object/source/include hashes are pinned. Historical compiler identity
is not needed to infer this body's ABI: its actual bytes and native execution
are checked directly. The alias is limited to this single proved edge.

The private native fixture links the **actual cached181 zero-argument COFF**,
the directive object and a typed two-slot consumer. It also references the
zero-slot symbol and verifies both function addresses are equal.1088 argument
pairs cover64 boundary combinations and1024 deterministic full32-bit pairs.
Each pair performs one ordinary typed C++ call, one raw call to that actual
cached function and one raw call to the exact original`33c0c3` assembly test
reference.18497 checks verify EAX0, ESP before/after caller cleanup, preserved
EBX/ESI/EDI/EBP, matching results and target address identity. Raw probes seed
all four nonvolatile registers; absolute snapshots allow restoring the test
frame even if a check fails. The original assembly exists only in the fixture.

One2-TU MSVC batch builds the support and fixture, followed by one private
fixture link and one native run. Compile/link/native exits are all0; each
exit/time/log record is persisted before parsing/assertion. No compiler repeat,
whole-archive union or production link is performed. All18 source/tool/object/
proof/include/library input pins pass before/after. New text is LF before SHA.
The initial preparation stopped before any native command on an external SDK
path formatting error; its files remain at the experiment root. The accepted
capture is under`local/experiments/v2-proven-cdecl-binding-217/final`.

The fixture compiler emits two C4731 warnings because its raw probe deliberately
seeds EBP. Both warnings remain in the capture; absolute global snapshots restore
the saved frame before C++ local/frame use resumes. The1088 native probes verify
that restoration and the callee's EBP preservation. These are fixture-only
warnings; the directive-only support source has none. No warnings are suppressed.

```powershell
py -3 scripts/research/experiment-v2-proven-cdecl-binding-217.py
py -3 iterations/v2/001-original-recovery/runs/217-proven-cdecl-binding/audit.py
```

Summary kind is`proven-link-contract`; its support_objects entry uses id
`cdecl-binding-00590290`. Each aliases row contains the exact from/to/VA,
support_object_id,directive and pinned proof. The collector can reread actual
COFF .drectve/symbols and count support objects separately. Full caller flags,
nested/provider behavior and game fidelity remain open. No other signature
or address inherits this binding, and no source implementation is added.

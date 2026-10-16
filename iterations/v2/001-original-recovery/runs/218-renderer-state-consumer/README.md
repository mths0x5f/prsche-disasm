# Run218 — original renderer-state consumer00537b40

One real native i386 C++ COFF, isolated from production/union. Frozen184 source
SHA `ed787305373b627f4fd7d20264fd4f0e63703d0cef9a02366d4579f0e35dffb1`;
original Porsche SHA `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries:00537b40 CALL/RET/stack producers/global widths,006bd934/954
loader exports, Run207006bd97c/984 contracts. Canonical exact/interior and recovered
WIP ownership preflight found0. No Ghidra, game-data, completed-run or shared edits.

119 original instructions/416B match PE bytes. The consumer's two RET0 paths
become one measured native RET0; three incoming stackDWORDs remain caller-cleaned.
Original537b81 saves the old indexed tableDWORD;537bfe reloads it for setstate12.
Printed `uVar9=10` lost that value. Original537c13/1b resolve to incoming param3
then param2 after one PUSH, replacing the printed uninitialized uStack variables.
Original entryS/frameS-0x414 and LEA537c83 put the buffer atS-0x400..S-1:
1024B, with savedtable atS-0x404. The header fixes only observed byte/WORD/DWORD
views; indexed span1024 is a minimum consumer view, not an allocation/owner claim.

Run207 getstate/setstate raw32stdcall4/8 match this caller's actual pushes.
GetProcAddress names and all three renderer implementations establish
about@0 EAX address32/RET0 and settexture@4 one rawDWORD/RET4. Voodoo's misleading
inferred about fastcall argument is PUSH ECX local allocation, discarded at exit;
the incoming ECX contents are not used. About's nested DWORD loads at+30/+18 and
the signedWORD reads at input+4/+6 retain original widths and bits.

One /MP6 batch compiled one changed gameTU and one controlled fixtureTU:
exit0,1.798446s. Saved exit/time before parsing. Game warning C4146 is the
original defined unsignedNEG index0/255; fixture warning C4244 deliberately
supplies char0x80. No warnings were suppressed. Initial postcompile zero-warning
assertion stopped; captured driver is preserved locally. Explicit
`--resume-existing-compile` validated identical source/proof/command and reused
the successful immutable objects/log, without recompilation. Native consumer
disassembly and actual COFF external symbols are recorded in summary204 schema.

Actual corrected body passed28 native call-boundary traces in0.031601s:
16 fast and12 fallback paths, table indices0/255, oldtable distinct from10,
highbit incoming arguments, signedWORD extrema, existing/new texture, about6/7,
all three fallback gates, output metadata, table restore and1024B buffer-end write.
These controlled callees verify boundary/dataflow, not renderer/game providers.

`proof-before-compile.json` holds original/callee/provider bytes, loader strings,
stack map, edit witnesses and unresolved contracts. `summary.json` is the
ordinary204-compatible one-game-object packet; the fixture object is excluded.
`validation.json` is the independent read-only SHA/PE/COFF/source/exit audit.

Remaining:00571630's original first argument is a data address (callee loads
DWORD through it), despite frozen code* declaration. Scoped int raw32 declaration
therefore introduces explicit native symbol `?FUN_00571630@@YAXHHHPAI@Z` versus
the prior code* spelling; canonical binding is still required, no bridge supplied.
Scalar/indexed/overlapping globals and address-only537ce0 require canonical owners
and aliases. Full callees/provider, lifetime/concurrency, fault/register and
whole-game fidelity are deferred. The candidate is not game/union integration.

Reproduce audit only:

```powershell
py -3 scripts/research/audit-v2-renderer-state-218.py
```

The experiment driver requires fresh output; its explicit resume mode is only
for the preserved pre-summary successful compilation. Completed summary is immutable.

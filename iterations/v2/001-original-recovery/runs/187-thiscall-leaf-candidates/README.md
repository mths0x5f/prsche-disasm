# Run187 — call-free native thiscall candidates

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first inputs: original catalog ranges/instructions,179 ABI declarations,
frozen186 native method proof and183 per-TU generated source/header provenance.
No accepted owner, caller adapter, registry, corpus or production file is changed.

Conservative filtering selects159 of1301 inferred thiscall functions. Each
has matching original RET/stack extent, contiguous parameter storage, one ECX
receiver, and no machine CALL or external/indirect branch. Source scans reject
unknown register values, unproven helper/callback/function-pointer calls and
unsupported hidden/variadic/extended-return contracts. Every native parameter
and return sizeof is asserted against179 metadata. The explicit original ECX
parameter becomes the same typed local view of native class `this`; source
body tokens retain183's already pinned integer-helper transformations.
No argument/receiver corrections or callable fallback implementations are added.

Exclusions are explicit:975 original machine calls,86 conservative possible
indirect-call syntax matches,39 RET disagreements/missing RET,28 canonical
accepted owners,8 extended x87 returns,1 qualified/decorated name,1 ROUND,
3 NAN and1 unrecovered incoming-register body. The86 syntax exclusions are
conservative exclusions, not proof of86 actual machine calls. All skipped VAs
and reasons remain in `summary.json`.

One full batch run uses actual MSVC `/MP6`, three compiler invocations, and
39.579 seconds including selection/generation/reporting.159 real code-generation
attempts produce127 x86 COFF objects and32 compiler failures. These bodies
all failed183's free-thiscall syntax phase, so this is a new isolated method
candidate subset. Native method symbols still require original caller/address
binding before integration. No second syntax census or new deep ABI suite ran;
the frozen186 `/Od`/`/O2` native proof is reused with complete input hashes.

27 relocation-free COFF text bodies exactly equal the original instruction
bytes. The independent audit verifies all159 bodies/9980 bytes directly from
the SHA-pinned PE, original leaf/RET gates, baseline/body preservation,
headers/source/object pins, native symbols and emitted sections. Accepted
function counts remain unchanged; raw matches and compile candidates are
separate from whole-graph or behavioral acceptance.

The127-object subset has one unresolved name, `__fltused`, referenced by8
objects. Dependencies stay unresolved. The32 failed TUs retain missing global
declarations and incompatible/partial scalar or extended-float expressions;
batch diagnostics are pinned and per-VA failures appear in `validation.json`.
No invented types, globals, casts, storage or stubs were supplied to pass them.
Existing compiler warnings about narrowing/precedence/unsigned negation also
remain recorded.184 global headers were not needed for this first bounded run;
adding relevant proven declarations is a separate incremental opportunity.

```powershell
py -3 scripts/research/experiment-v2-thiscall-leaves-187.py --jobs 6
py -3 iterations/v2/001-original-recovery/runs/187-thiscall-leaf-candidates/audit.py
```

`summary.json` contains all eligibility results, per-VA baseline/generated
source/header pins, original ranges/bytes/RET and method contracts, COFF
sections/symbols and compiler batch response/log hashes. `validation.json`
pins that summary and the independent audit. Generated C++, COFF and batch
logs remain under `local/experiments/v2-thiscall-leaves-187`.

Next: apply only relevant184 declarations to failed leaf TUs as a measured
delta. Original thiscall callers remain blocked on missing receiver/argument
contracts documented186; this packet supplies no blanket caller rewrite.

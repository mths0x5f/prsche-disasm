# Run198 — reusable native candidate union and diagnostic link

Frozen compilation-free union. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Inputs:924 ordinary Run192 COFF objects plus146 thiscall Run196 objects,
**1070 distinct VAs**, zero overlap and zero new compilations. Source,
quoted include closure, object, compiler/tool and original-data provenance
remain explicit. No prior packet, production binding, resource or registry
is modified; no aliases, storage definitions or function stubs are supplied.

The reusable builder accepts explicit `--ordinary-summary`,
repeatable `--thiscall-summary`, `--output`, `--run` and optional
`--baseline-union-summary` (default195). Output must be a fresh local
experiment directory and the run must have no completed summary. It validates
the recorded closures with batched SHA/mutation guards.1054 exact native
symbol snapshots are reused after source/object/include identity checks;
the16 new object symbol tables are reread. All531 platform-library identities
are reused from195 and their bytes guarded before/after; none are newly
inventoried.6516 unique final input pins pass. Omitted summaries default to
ordinary192/thiscall196. Multiple thiscall packets must have disjoint compiled
VAs; overlap with one another or the ordinary set is rejected explicitly.
Uncompiled rows do not claim ownership.197 is not included in this snapshot.

An actual `lib.exe /MACHINE:X86` archive contains all1070 objects:
1,209,804 bytes, SHA256
`70a07ea4dd5f762234187b27b159d1bf762b24dd524617d3af9b46a3b1c4a0e1`.
An actual `link.exe /DLL /NOENTRY /WHOLEARCHIVE` diagnostic uses the same
explicit VC14.44/SDK10.0.26100.0 x86 libraries and `/VERBOSE:LIB` as195.
The accepted archive command takes0.501 seconds and link command0.048 seconds.
No DLL or EXE is produced.

Compared with195, raw unresolved COFF names rise387→403 and distinct
referring-object references763→780. After CRT/platform extraction,
LNK1120 reports377→393 unresolved names; LNK2001/2019 occurrences rise
564→581. No old unresolved name is removed. The16 added names are11 table
address symbols,4 integer globals and1 string symbol, all exact179 names.
The005b54f0 integer is referenced by two new objects, hence17 new references.
Ten CRT machine helper names still resolve and no additional unresolved
names come from the extracted platform closure.

The exact frontier has145 function names,241 data names and17 other names.
All145 function VAs remain outside the compiled union:36 have canonical
recovered owners and109 have neither a compiled union body nor a canonical
owner. Seven other printed/runtime source contracts remain unresolved;
the remaining10 names resolve through platform libraries. All241 data
names have exact179 HighSymbol-name matches;5 retain observed conflicting
type/storage variants.25 data addresses lie in nonwritable PE sections.
These facts do not authorize allocating globals or coalescing consumer views.
Every frontier row retains exact symbols, consumers, inferred declarations,
canonical owners and original section/initial-byte evidence.

The first capture at the experiment root stopped on localized LNK1120
count extraction and is retained separately. The accepted fresh capture
is under `local/experiments/v2-native-union-198/final`. Its source and
summary are preserved as `captured-builder.py` and `captured-summary.json`;
the subsequent interface revision uses the corresponding `-001` snapshots.
Parser-only finalization corrects the new PTR_FUN data categorization and
performs zero lib/link commands: native archive, response and raw log hashes
are unchanged.195 had no PTR_FUN frontier names and its counts are unchanged.
Finalization checks the localized LNK1120 count against all parsed decorated
names; the final category counts are145/241/17. All new text uses LF before SHA.

Commands used:

```powershell
py -3 scripts/research/audit-v2-native-union-198.py --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json --output local/experiments/v2-native-union-198/final --run iterations/v2/001-original-recovery/runs/198-native-union
py -3 scripts/research/audit-v2-native-union-198.py --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json --output local/experiments/v2-native-union-198/final --run iterations/v2/001-original-recovery/runs/198-native-union --finalize-existing
py -3 iterations/v2/001-original-recovery/runs/198-native-union/audit.py
```

Fresh captures use the current finalized builder directly. Parser/report-only
finalization preserves an ordered capture chain and requires retaining the
exact captured builder bytes before an edit; it rejects changed native inputs
or tool logs. The repeatable packet interface is finalized without another
archive/link invocation. A controlled overlapping-packet CLI pilot confirms
rejection before any archive/link tool runs.
Completed-output guards preserve this snapshot. The final audit repeats no
compiler, archive, linker, original execution or native ABI oracle.

Next frontier: bind existing canonical owners under proved ABI contracts,
recover the remaining109 function bodies, and prove native ownership,
initialization and overlapping views for241 data names.193/194/197 evidence
belongs to their independent packets; this union does not wait for or ingest
their unfinished deltas. This is a dependency diagnostic, not a game launch
or original-behavior acceptance claim.

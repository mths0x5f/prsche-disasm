# Run206 — combined declaration and float-bit candidates

Original: `Porsche.exe`, SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Evidence: frozen192/196/197 objects, original179 declarations consumed by203,
and original00485100 instructions/HighIR/raw-bit fixture202. Index entry point:
`research/binary-index/README.md`; consumers and addresses are in each packet.

Actual union: **1094 distinct VA objects** =945 ordinary (924+21) +149 leaf
(146+2+1), zero overlaps, +22 objects relative to199. Native archive has1094members,
1238938bytes, SHA256 `ac8505d84248f5a59ccaeb32d3d1fb5923d374796e9f61ea7f3214e9fef8420b`.
One library command succeeded; one diagnostic `/DLL /NOENTRY /WHOLEARCHIVE` link
returned1120: **413 unresolved names /600 diagnostics**, no DLL or game EXE.

Raw union:423names/800objectrefs. Function names145→133:21removed,9new dependencies;
36canonical owners remain outside this union and97 lack a compiled/canonical body.
Data names241→273;7printed CRT contracts remain. Ten actual machine CRT helper names
resolve through platform libraries. Full dependency closure of the game is not proven.

Cache:1072symbol snapshots and531platform-library pins reused;22new objects read.
6672unique exact input pins checked before/after. **Zero compilations**;
elapsed7.828s includes the collector, archive and diagnostic link.
Run203's missing observed compiler exit/timing remain null; selection uses its
explicit actual-COFF evidence and independent object checks, not a fabricated exit0.
Run200's unsafe float-conversion object is excluded and replaced by202's candidate.

Exact command executed from the repository root:

```powershell
py -3 scripts/research/audit-v2-native-union-204.py `
  --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/203-consumer-declaration-pilot/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/197-call-free-abi/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/202-float-bit-stores/summary.json `
  --baseline-union-summary iterations/v2/001-original-recovery/runs/199-native-abi-union/summary.json `
  --output local/experiments/v2-native-union-206 `
  --run iterations/v2/001-original-recovery/runs/206-frontier-and-float-union
```

Use fresh output/run paths for a new execution. Local artifacts and logs are under
`local/experiments/v2-native-union-206/`; report/output hashes are in `validation.json`.
No stubs, guessed storage, accepted function additions or production changes.
Run173 remains476full+6partial and game-link267symbols/303refs.
Full body/ABI/x87/global lifetime and actual-game checks remain in the validation backlog.

# Run215 — consumer contracts and byte views union

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index/query: original THRASH callback slots, DirectSound Release, signed FILD32,
ECX/stack vcall, two direct callee contracts and byte+1 reads. Evidence/addresses
are recorded in207/208/210/211/212; each accepted here only as a compile candidate.

**1107 distinct function VA objects** =958ordinary +149leaf, +13 from206.
Actual archive1107members/1254572bytes, SHA256
`1d8a505518459f03e7bb01b8cfed75ad3ce8c88f6a40e3799f1e3d3f0e3c1112`.
Actual diagnostic DLL /NOENTRY /WHOLEARCHIVE link returned1120:
**426unresolved names /618diagnostics; no EXE/DLL**.
Raw437names/821objectrefs;127function names (90missing,36canonical outside union,
1compiled-VA contract mismatch),292data and7printed CRT contracts.
Eleven actual CRT helper names resolved, including rangecheckfailure.

Compared with206:13function names removed,7introduced; netfunction names133→127.
Missing bodies97→90. Data273→292 reflects newly exposed storage dependencies.
00590290 already defines `?FUN_00590290@@YAIXZ`;211's proven caller pushes two
unused slots and refers to `?FUN_00590290@@YAIII@Z`. This is explicitly a compiled
VA contract mismatch, not a missing function or permission to insert a guessed alias.

1094cached symbol snapshots and531platform pins reused,13new objects read;
6780exact input pins checked before/after. **Zero compilations**, one archive and
one link; collector elapsed16.140s. Partial-failure batch208 and unknown exits203
retain their original evidence; no fabricated per-object exit values.
Run212's sole C4146 unsigned-negation warning is recorded, not suppressed.

Executed arguments (PowerShell continuation formatting):

```powershell
py -3 scripts/research/audit-v2-native-union-204.py `
  --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/203-consumer-declaration-pilot/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/207-pointer-call-consumers/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/208-frontier-dependencies/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/210-consumer-views/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/211-direct-call-contracts/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/212-byte-consumers/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/197-call-free-abi/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/202-float-bit-stores/summary.json `
  --baseline-union-summary iterations/v2/001-original-recovery/runs/206-frontier-and-float-union/summary.json `
  --output local/experiments/v2-native-union-215 `
  --run iterations/v2/001-original-recovery/runs/215-consumer-contract-union
```

Use fresh output/run paths to execute again. Logs/artifacts:
`local/experiments/v2-native-union-215/`. Summary and validation pin the actual
archive, source/include/object closure and link diagnostics.
Production173 remains476full+6partial and game-link267symbols/303refs.
No storage allocations, stubs, production changes or faithful full-game acceptance.
Run214 sound output-value recovery is a separate subsequent packet, excluded here.

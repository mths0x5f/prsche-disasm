# Run222 — native function, scalar storage and proven call binding

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navigation: binary-index,211/217 cdecl CALL/RET,213/218 renderer state consumer,
194/202/219/221 exact float4 reads. No original game data is modified.

**1109 distinct function VAs**, plus2support objects; actual archive has1111members
and1260938bytes, SHA256
`e7ec41263bd950c2dd781ab6ecee2d01640880e7aab23b9d17d470a55844d314`.
Support objects are not counted as recovered functions. One object contains only
an exact linker directive; the other defines two original readonly float cells.

Actual link:445unresolved names/639diagnostics, exit1120, no DLL/EXE.
Compared with216, four edges close:00537b40,00590290's proven caller binding and
two float cells. The new consumer exposes17 further dependencies, so the count
432→445 is graph expansion. Linked frontier:93missing function names,
36canonical owners outside union,309data views and7printed CRT contracts.
00590290 is actually resolved through its exact validated directive;11CRT
helpers resolve through platform libraries and are reported separately.

218 fixes three decompiler dataflow losses: state12 receives savedtableDWORD,
FUN00572b40 receives incoming arguments, and the local buffer is1024bytes.
1341original PE instructions checked across consumer/callees/providers;28actual
native controlled call-boundary traces pass. Full providers/wholegame are deferred.
217's1088case/18497check actual-cached-body ABI fixture passes.221 verifies738
indexed direct float4 reads and readonly bits/permissions;26additional original
HIGHLOW sites lack indexed instruction boundaries and remain explicit in the index.

Cache:1108symbol snapshots reused,3new objects read,6840pins before/after PASS.
Zero compilations in this collector; one archive/link, elapsed10.714s.
Production173 unchanged476full+6partial and267game-linknames/303refs.

Executed command:

```powershell
py -3 scripts/research/audit-v2-native-union-220.py `
  --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/203-consumer-declaration-pilot/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/207-pointer-call-consumers/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/208-frontier-dependencies/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/210-consumer-views/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/211-direct-call-contracts/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/212-byte-consumers/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/214-sound-output-consumer/summary.json `
  --ordinary-summary iterations/v2/001-original-recovery/runs/218-renderer-state-consumer/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/197-call-free-abi/summary.json `
  --thiscall-summary iterations/v2/001-original-recovery/runs/202-float-bit-stores/summary.json `
  --support-summary iterations/v2/001-original-recovery/runs/217-proven-cdecl-binding/summary.json `
  --support-summary iterations/v2/001-original-recovery/runs/221-readonly-scalar-storage/summary.json `
  --baseline-union-summary iterations/v2/001-original-recovery/runs/216-sound-consumer-union/summary.json `
  --output local/experiments/v2-native-union-222 `
  --run iterations/v2/001-original-recovery/runs/222-native-support-union
```

Use fresh output/run paths to repeat. Local artifacts/logs/early native execution
receipts: `local/experiments/v2-native-union-222/`. Report validation pins actual
archive/input closures and COFF support directives. No guessed aliases or stubs.

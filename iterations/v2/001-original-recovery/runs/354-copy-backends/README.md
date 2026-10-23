# Run354: original optimized copy backends

Three original backends (1015 indexed instruction bytes;1072 raw bytes including
padding) restore x87 FILD/FISTP, MMX MOVQ and SSE MOVUPS/MOVNTPS copying. C++ owns
control flow and scalar tails; isolated hardware helpers preserve original
register effects and grouped load/store order. Forward overlap behavior is kept;
there is no memcpy/memmove replacement, duplicate state or imported copy provider.

Native008 passes41472 cases at each of /Od and /O2 (82944 total;9455616 checks)
and six mutation controls. Coverage includes32 alignments,36 threshold sizes up
to257, both overlap directions/exact alias, full8192-byte arenas, advanced EAX,
ABI and selected FXSAVE fields. Native and actual game objects have matching
instruction shape:42 FILD/42 FISTP,84 MOVQ,2 MOVNTPS, no EMMS/SFENCE and no
undefined symbols. The existing dispatcher retains its MMX cleanup.

Fresh build001 compiles186 C++ TUs/8 projects:244 names/259 refs,noEXE/game
execution. Three names close with no new dependency; shared473-input audit PASS.
REA355 supplies five original dossiers. Prior proofs and failed attempts remain
historical;008 includes all required mutation controls and final LF inputs.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/354-copy-backends/acceptance.json
```

CPU comparison starts after EMMS/FNINIT and zero XMM0/1; it covers control/status/
abridged tags, x87/MMX slots0..6, MXCSR and XMM0/1. Arbitrary ambient CPU state,
FIP/FDP equality, invalid spans and concurrent streaming visibility remain open.
A fixture-only SFENCE precedes memory observation; no fence is added to production.
Next: original render export-table binding/ABI triage and full integration holds.

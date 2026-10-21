# Run345: original diagnostic setup and fill binding

Five original device/channel setup bodies (334 PE bytes) now share their
original physical tables, initialization guard and readonly string spans.
The device image includes the name prefix at005e1c88, callback view at005e1c8c
and adjacent tail DWORD at005e1ce8. Channel names retain interior string aliases.
No guessed callback or parser implementation is provided.

Final native diagnostic attempt005 compares18 cases at /Od and /O2 (36 total),
with four detected mutations. It checks the actual100B/512B PE initializers,
both readonly spans, initial BSS guard, callback identities, lazy initialization,
field boundaries and original ABI. Review caught a misplaced tail DWORD that
earlier function-only cases missed; those earlier attempts remain preserved.

The application_fill ABI view forwards to the accepted Run312/321 dispatcher.
Its128 transport cases and three mutations pass; the unchanged27,648-case full
scalar/MMX/SSE chain receipt, inputs, tools and raw PE spans are rechecked and
reused, without rerunning those native tests. No new fill algorithm is counted.

Fresh build001 compiles179 C++ TUs/8 projects. Six names close and eight original
child/callback boundaries surface:256 unresolved names/273 refs,noEXE. The
457-input audit accepts both proofs and checks actual COFF/graph/compiler events.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/345-diagnostic-devices/acceptance.json
```

Next346: original device/channel setters and three device output callbacks,
then parsers/environment. Invalid indices, arbitrary aliases, complete output/OS
composition, formatter/locale domains and full-game/visual acceptance remain HOLD.
The SHA-pinned342 raw evidence/index files are preserved without Git newline
conversion; their native tests are unchanged.

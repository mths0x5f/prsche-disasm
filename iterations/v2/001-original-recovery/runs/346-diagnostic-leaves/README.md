# Run346: diagnostic setters and output callbacks

Five original bodies (212 PE bytes) restore device/channel flag setters and
three output callback wrappers. Setters preserve unrelated flag bits, zero/one
channel selection and unmasked direct indexing. Output wrappers forward the
second argument and preserve the original calling conventions. The existing
formatter_stdio printf owner is reused; mono formatting remains an extern.

Native attempt001 passes50 cases at /Od and /O2 (100 total), with four detected
mutations. The fixture supplies canonical-layout data and controlled output
targets. The supplemental index repairs the omitted00586cc0 callback entry with
its relocated pointer, raw PE body, RET and original IAT consumer.

The modern OutputDebugStringA binding uses the exact original KERNEL32 import.
The auditor checks that its real x86 COFF code is only a six-byte JMP through
that import, with one DIR32 relocation and no other undefined target. This is
platform plumbing; it is not another recovered game algorithm or visual test.

Fresh build001 compiles181 C++ TUs/8 projects:252 unresolved names/269 refs,
noEXE. Five names close, one mono-formatting boundary appears. Shared460-input
audit PASS; no native fixtures or duplicate state providers enter the graph.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/346-diagnostic-leaves/acceptance.json
```

Next347 traces device/channel parsers, environment lookup and mono formatting
with REA. Invalid indices, formatter/locale domains, complete output/OS effects
and full game/visual acceptance remain open. Same-VA ABI triage found no safe
additional aliases; its excluded cases remain in the local346 triage artifact.

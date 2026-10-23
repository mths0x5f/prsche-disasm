# Run350: tokenizer and diagnostic formatting evidence

One manifest-driven REA session002 provides six dossiers: original tokenizer
005a30ee, vsprintf005a299e, mono writer00592b60 and helpers00592d00/00592d70/
00592e00. Attempt001 spawnEPERM is retained; shared session audit002 PASS.
The tokenizer uses canonical CRT thread state+0x18 and is recovered in349.

Mono formatting remains a separate original display subsystem. Its writer uses
cursor/attribute/tab state and the original monochrome display address; those
cells and the unpromoted00592ac0 region need ownership/lifecycle proof. The
format wrapper uses original FILE-style state with a0x7fffffff count, not the
caller's256-byte local bound. No host printf or fake display provider is accepted.
Evidence here navigates implementation and does not constitute native acceptance.

```powershell
py -3 scripts/research/audit-v2-rea-session.py --config iterations/v2/001-original-recovery/runs/350-diagnostic-formatter-evidence/rea-queries.json --attempt 002
```

# Run348: diagnostic parsers and environment wrapper

Seven original functions (661 PE bytes) restore ASCII lowercase copy, common-
prefix scoring, device/channel lookup and parsing, and locked environment lookup.
Canonical diagnostic tables and CRT lock providers are reused. Tokenizer and
inner environment lookup remain named original boundaries, with no host substitutes.

Lookup selects the first strictly longest common prefix. Copy deliberately
retains the original inclusive bound, extra terminator and repeated source scans.
Native003 passes82 original-versus-C++ cases at both /Od and /O2 (164 total),
with eight detected mutations. Cases cover overlap, high bytes, exact delimiters,
disable markers, first-tie lookup, channel63, 254-byte input and lock/inner/unlock
ordering with a cached return pointer. Capacity zero and parser input>=255 remain
unvalidated original overflow domains; fixture tokenizer is only a caller oracle.

REA347/002 supplies six original dossiers; shared463-input integration audit PASS.
Fresh build002 compiles182 C++ TUs/8 projects:251 unresolved names/268 references,
noEXE/game execution. Three old names close; tokenizer and inner lookup appear.
Build001 stopped before source compilation in the sandbox and is retained.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/348-diagnostic-parsers/acceptance.json
```

Next349 restores tokenizer005a30ee through the existing canonical CRT thread
provider; REA350 traces its formatting siblings. Environment vector lifecycle,
formatter/display effects, malformed input and full game/visual acceptance stay open.

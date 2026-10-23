# Run353: original mono formatting and display logic

Seven original bodies (909 indexed PE code bytes) restore mono/XY formatting,
text/control-byte output, scroll, clear, attribute and the vsprintf bridge.
The exact14-byte original data image and two distinct BSS cells are owned once;
006af144 and adjacent padding remain unowned. Original0xb0000 pointer is retained.
Canonical heap and formatter entry/core/cleanup providers are reused.

Native003 passes44 cases at /Od and /O2 (88 total), nine mutations detected.
It compares initial PE data/BSS before reset, controlled framebuffer and cursor,
ABI/returns, raw varargs, nested lock/copy/fill/core/cleanup order and formatter
cleanup. Review corrected signed IDIV cursor math and signed length gate;
safe tab/newline tests include negative cursor states through INT_MIN. Earlier
attempts remain historical:001 had tautological initial checks;002 preceded the
signed-math correction. Only003 is current proof.

Fresh build001 compiles185 C++ TUs/8 projects:247 names/262 refs,noEXE/game
execution. One name closes with no new dependency; shared470-input audit PASS.
REA347/350 and supplemental352 retain exact original provenance. Canonical
formatter_entry.cpp matches its accepted136 proof; opaque tail is not zeroed.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/353-diagnostic-mono/acceptance.json
```

Actual enabled-path0xb0000 mapping, negative glyph writes, row>24, format output
>=256 and arbitrary descriptor-tail behavior remain HOLD. Default original
dispatch disables mono, but PRINT_DEVICE may enable it; no forced-off policy or
host screen is introduced. Next354: three original optimized copy backends.

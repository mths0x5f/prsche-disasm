# Run380: original pixel address and conversion helpers

Native001 **PASS**: 517894 comparisons / 1553682 checks in each `/Od` and
`/O2`; seven mutations detected. New entries are `00574050..00574076`
(39B) and `00574b70..00574c49` (218B): 2 VAs / 257B. Root owns production
intake and the next shared build/audit; frozen377 is not enlarged.

Source is `Porsche.exe` SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index searches cover both helpers, `00556910`, palette `006b4b20..006b4f20`
and extent consumers `00537e30`/`0053cbc0`. `evidence.json` retains original
instruction bytes, callers/references, raw jump targets/map, section metadata,
palette aliases and all40 palette-range HIGHLOW operands. Neither entry nor
body overlaps an accepted registry provider/interior entry:546 entries and584
indexed accepted ranges were checked. Indexed navigation alone is not treated
as semantic proof.

`00574050` reads the existing canonical config: pitchDWORD+36, storage-bits
byte+14 and pixel-baseDWORD+44. Both products wrap to32 bits; the horizontal
product then uses **arithmetic** right shift3 before the wrapping address sum.
The returned pointer transports that exact32-bit result. Synthetic addresses
are compared as words and never dereferenced.

`00574b70` dispatches by canonical depth byte+13. Depth15 expands1555, with
alpha255 only when bit15 is set. Depth16 plus format byte+12 equal0x6d expands
4444; other depth16 formats expand565 and set alpha255 when the **whole input
DWORD** is nonzero. Expansion preserves the original zero low channel bits;
there is no replicated-bit scaling. Depth24/32 return the unchanged input.
All other depth bytes index the palette directly, without a new mask/guard.

Only new state is the256-DWORD palette `006b4b20..006b4f1f`. The raw consumer
`00537e30` walks256 entries with stride4; `0053cbc0` independently compares
the exclusive end006b4f20. That end belongs to unrelated original state and is
not included. The palette span is beyond `.data` raw end005e7000 and inside
its virtual extent, so loader initialization is all zero. Original005de2f8
contains another pointer to006b4b20; no unused host pointer owner is invented.
No existing palette owner was found. The old48B config and all mode/base
aliases remain in frozen `window_shutdown.cpp`; no field is redefined/reset.

The fixture checks production config against raw48B initial data and all256
production palette words before resets. It validates raw jump-table VAs/map
before relocation and links actual canonical config,359 THRASH adapter and
frozen378 pixel-write caller. The copied original378 caller calls copied
original380 bodies, while actual378 calls new C++ helpers. Controlled typed
draw/word endpoints isolate independent381 work; they do not claim381 behavior.
Unused shutdown services fail closed.

Direct comparisons exhaust all256 depth bytes with every valid palette index,
all65536 packed values for1555/4444/565, every format byte with high input bits,
and address calculations over every storage-bits byte, signed/wrapping coordinate
edges, pitch/base extremes. State and palette must remain unchanged; EAX, ESP
and EBP/EBX/ESI/EDI are checked. Additional real378 comparisons cover valid
software writes, palette/config destination aliases, hardware conversion,
signed FLOAT32 coordinate transport and callback state effects. Seven mutations
detect logical SAR replacement, widening the horizontal multiply, wrong pitch,
wrong1555 alpha bit, wrong4444 format, truncated565 alpha test and palette masking.

Palette lookup comparison is bounded to indices0..255 because the original has
no check. Invalid indices/addresses, arbitrary computed aliases, concurrency,
future palette setters and ambient floating-point environment changes remain
HOLD. Software dereferences use backed valid spans. This proves original integer
helpers and bounded caller composition, not live renderer/startup/gameplay.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/380-pixel-helpers/native-config.json --attempt 1
```

Receipt: `local/experiments/v2-pixel-helpers-native-380/001/receipt.json`.
`coff-evidence.json` pins eight `/Od`/`/O2` object symbol dumps, showing only
new380 helper/palette definitions and references to canonical config ownership.
No new runner, shared-tool changes, old-source edits, resources or commits.

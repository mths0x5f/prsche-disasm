# Run382: original clipped rectangle geometry

Original0056daf0..0056dd7f (656 bytes) supplies the raw five-DWORD geometry
contract introduced by381. C++ owns clipping order and vertex construction;
small x87 primitives preserve extended intermediates and original FSTP32 stores.
No whole-function assembly rewrite, numerical approximation or new framework is
used. Root owns integration.

Source is Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index/registry queries confirm no prior body owner. All indexed instructions
equal the raw656-byte body. `evidence.json` records complete assembly, exact state
layout, initialization, scalar ownership, relocation coverage and native receipt.

Two explicit20-byte blocks receive new ownership:006a6404..6417 is loader-zeroed;
005dfa08..fa1b contains FLOAT32 words1,1,1,640,480. The BSS block ends before the
canonical file-page cell006a6418. A separately pinned readonly zero005b23f8 is
defined; canonical221 one005b24a8 and357 quad transport remain their existing
owners. Initial production bytes/scalars are checked before fixture overrides.

The original validates positive width/height, clips left/right/top/bottom in that
order, then validates resulting extents. Clipping changes UV endpoints with live
80-bit ratios and explicitly rounds extent/UV writes to FLOAT32. Four32-byte
vertices follow TL/TR/BR/BL order with words{x,y,z,rhw,color,0,u,v}. Canonical357
dispatches their addresses through THRASH slot38. The fixture checks exact vertex
bytes and pointer offsets0/32/64/96 before controlled callback effects.

Shared native attempt001 PASS:31296 comparisons at each of /Od and /O2,62592
total; all eight mutations detected. Cases cover clipping edges/corners,
degenerate/inverted viewports, signed/zero/fractional extents, reversed/nonbinary
UV ranges and4096 seeded finite rectangles.320 cases per variant compare actual
frozen381 wrapper→new C++ geometry against raw381 wrapper→raw656-byte geometry.
ESP/EBP/EBX/ESI/EDI, persistent state, complete vertices, call order and x87
control/status/MXCSR match. Rounding the live ratio to FLOAT32 is detected by
vertex bytes at case240.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/382-rectangle/native-config.json --attempt 1
```

Receipt: `local/experiments/v2-rectangle-native-382/001/receipt.json`.
The compiler emits C4405 for helper parameter`add` used in inline assembly;
both variants and mutation controls pass. Source/header/config/fixture remain
frozen; no cosmetic source edit or proof rerun followed acceptance.

The full PE HIGHLOW audit records28 references into the new BSS block,25 into
the initialized block and845 to readonly zero. Unindexed users near0056de50..
0056e24b remain navigation gaps. Known setters0052a7f0 and005740a0 are unaccepted
original bodies, not additional providers in this batch. Full audit artifact:
`local/experiments/v2-rectangle-native-382/state-audit/relocations.json`.

Acceptance covers the tested bounded finite domain with masked exceptions,
default x87 precision/rounding and default MXCSR. Nonfinite/denormal/extreme
overflow and ambient FP modes, computed aliases, concurrency/reentrancy, actual
THRASH effects and full startup/display/game acceptance remain open.

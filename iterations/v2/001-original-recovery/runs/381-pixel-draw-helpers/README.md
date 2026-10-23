# Run381: original draw forwarding and packed-word writer

Two new original entries,89 bytes:0056de20..0056de41 (34B) and
0056e301..0056e337 (55B). Existing378 draw/word contracts are implemented without
editing passed sources or adding production state. Root owns integration.

Source is Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Registry/index queries0056de20,0056e301,0056e2c0 and0056daf0 confirm both new
entries are unowned. Accepted big-endian0056e2c0 ends0056e300;0056e301 is a
separate adjacent entry, with no overlapping bytes. Indexed instructions exactly
match both raw original bodies; `evidence.json` records their complete listings.

The draw wrapper copies raw FLOAT32 representations of x/y and passes them with
two original1.0f words and the pixel to an explicit five-DWORD geometry boundary.
The original wrapper uses only MOV/PUSH, so memcpy-to-DWORD transport preserves
signaling NaNs without an accidental FPU load. The656-byte geometry/clipping body
0056daf0 remains external as render_draw_rectangle_bits_0056daf0; no substitute
quad, clipping or THRASH behavior is introduced.

The word writer uses signed count branches: nonpositive writes nothing;1 writes
one byte;2 writes a word;above3 writes a DWORD. The original3-byte path stores a
word then overwrites byte0 with bits16..23, leaves byte2 unchanged and returns
pointer+3. For pixel0x12345678 the first two output bytes become34,56. This unusual
behavior is preserved exactly, including the returned pointer.

Shared native attempt001 PASS:8614 comparisons at each of /Od and /O2,17228 total,
with seven detected mutations. Tests cover signed size extremes, null/nonpositive
counts, unaligned destinations, walking bits/complements, complete output buffers,
returned EAX, exact geometry argument/event order and endpoint writes. Draw inputs
include zeros, denormals, infinities, quiet/signaling NaNs and seeded raw DWORDs;
x87 control/status and MXCSR remain unchanged at the controlled geometry boundary.
ESP/EBP/EBX/ESI/EDI are checked for both functions. No persistent initialization
exists; both original embedded1.0 words are pinned before relocation.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/381-pixel-draw-helpers/native-config.json --attempt 1
```

Receipt: `local/experiments/v2-pixel-draw-helpers-native-381/001/receipt.json`.
Source/header/config/fixture remain frozen after PASS. Actual geometry/THRASH
effects, invalid positive write spans, MMIO/concurrent store observation and full
renderer/startup/game composition remain open.

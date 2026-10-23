# Run378: original packed-pixel write/draw path

Original00556910..00556a34 (293 bytes) is recovered as a three-DWORD cdecl core
and the existing render_display_select_buffer_00556910 facade. The arguments are
signed x/y and a packed pixel. The legacy name/header is preserved; the indexed
render_display caller pushes x=i,y=0,pixel=1 and cleans12 bytes. Other indexed
callers confirm the same argument order. Root owns integration in the next batch;
passed377 is not enlarged.

Source is Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Registry/index queries00556910 and its four direct helper addresses find no
accepted provider. All293 indexed instruction bytes match the raw PE. The
adjacent accepted heap_word0056e2c0 ends0056e300; external0056e301 is a separate
nonoverlapping indexed entry. Evidence records all four callsites, raw jump/map
data, exact state aliases, ABI and explicit unresolved helpers.

For mode neither0 nor255 and active state0, the original saves GetState10/1,
sets state10/texture0, converts the pixel, draws signed x/y converted to FLOAT32,
then restores both saved values. This path bypasses clipping. The software path
uses signed half-open clipping, calls the address helper, then reads depth.
Depth4 preserves the original unmasked even-pixel OR;8/15/16/24/32 use their
original write widths. Unsupported depths still call the address helper.

Only canonical window_shutdown state and THRASH table storage are consumed;
no new production globals are defined. Canonical359 GetState/SetState providers
are compiled directly. The four original helpers00574050,00574b70,0056de20 and
0056e301 remain typed externs, with controlled endpoints only in the fixture.

Shared native attempt001 PASS:7115 comparisons at each of /Od and /O2,14230
total, with all seven mutations detected. Tests cover all256 depth bytes,
parity/pixel truncation, helper side effects before the depth read, output aliases,
signed clipping extremes, GPU float precision boundaries, exact call/state
restore order and ESP/EBP/EBX/ESI/EDI. The known facade discards EAX; no return
meaning is invented. Actual canonical state initialization is checked against
raw48 bytes before overrides. Fixture THRASH storage is explicitly labelled;
the real production table owner/zero-fill and accepted359 proof are pinned.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/378-buffer-select/native-config.json --attempt 1
```

Receipt: `local/experiments/v2-buffer-select-native-378/001/receipt.json`.
Source/config/fixture remain frozen after PASS. Four engine helper bodies, live
renderer/device effects, arbitrary computed spans, non-nearest x87/MXCSR rounding,
concurrency and full startup/display/game acceptance remain open.

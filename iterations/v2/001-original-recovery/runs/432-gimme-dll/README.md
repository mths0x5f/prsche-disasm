# Run 432: gimme.dll recovery and the FaceInRace heap over-read

Original `gimme.dll` SHA-256 `3a43b0f6a1608f69adc3a5009c9fe055a24e17197e85c4045c2c43e37eb75f6b`,
preferred base `0x10000000`, one export `ConvertFile`. Called by `Porsche.exe` (`ddd748fd…`) from
`FUN_004dbba0` at `004dbe36`.

## 1. Root cause of the crash

**Summary.** `gimme.dll` links two generations of EA's GIMEX image library header. The six
"shape" format modules (FSH/PSH/VSH/NSH/DSH/SSH, module version 2.07) were compiled with a
`GINFO` image descriptor of `0x2aa4` bytes. FaceInRace's own image code and the other 63 modules
were compiled with the older `0x2890`-byte `GINFO`. Every `GINFO` starts with a tag and its own
size, and the shape writer uses `size == 0x2aa4` as its version test before it touches the newer
fields. FaceInRace copies a descriptor with `galloc(0x2890)` + `memcpy(…, 0x2890)`: the copy keeps
the source's size field `0x2aa4`, so the FSH writer trusts it and reads up to `0x214` bytes past
the end of the `0x2890` block. The record count it loops over comes from heap memory outside the
block, and the loop walks off the heap page.

This is EA misusing its own library inside one build, not a bug in the GIMEX shape module: the
shape reader itself caps the record count at 32 (`1010a6fa`), and the writer's version test is
correct for every descriptor that tells the truth about its size.

### The trigger in Porsche.exe

`FUN_004dbba0` looks for a player photo `<name>.bmp/.jpg/.pcx/.tga/.tif` (table `005d97b0`).
Without one it uses `%sAllDrivr.fsh` (`005d9824`) and the driver index as `ConvertFile`'s third
argument. The destination is `%s%s.fsh` with `pic16` (`005cccc8`, `005ccce0`). So the default
case converts FSH → resample to 0x36×0x40, 16 bpp → FSH, which is exactly the shape-to-shape
path that mixes the two descriptor sizes.

### Evidence chain (addresses are VAs in the original DLL)

| Step | Where | What the bytes do |
|---|---|---|
| Source descriptor | `10109112` (FSH module `info`) | `galloc(0x2aa4)`, tag `'SHPI'`, size `0x2aa4`; fills `+0x2890`, `+0x2894` (`10109781`, `1010978d`) |
| Extension records | `1010a6fa` | `+0x2898` = record count capped at 32; 16-byte records at `+0x289c` |
| Same-size copy (correct) | `10001450` | `galloc(src->size)` + `memcpy(src->size)` |
| Resample copies (defect) | `10001930`, `10001cb0` ×4, `10002160`, `10002340` ×2 | `galloc(0x2890)` + `memcpy(dst, src, 0x2890)` |
| Writer dispatch | `ConvertFile` → `10004f9f` → table `10431a50 + 0x24*1 + 0x1c` = `100f9b24` → `100f9b76` | FSH write, sections gated by bits of `GINFO+0x428` |
| Version-gated reads | `10104ad3` (`10104ce2`), `101054a0` (`101054dc`), `10105606` (`10105641`) | `cmp [info+4], 0x2aa4`, then reads `+0x2890…+0x28a8+16*n` |
| Fault | `101055ac` in `101054a0` | `mov dl, [esi+edx+0x28a0]` with the loop bound `[info+0x2898]` |

`galloc` (`10003170`, EA diagnostic prefix "galloc - …") frames each block as `'GMEM'`, size,
data, `'GEND'` on top of the debug CRT `_nh_malloc_dbg` (`10229f50` → `10229fc0`, 32-byte header,
4-byte `0xFD` no-man's-land). For a `0x2890` descriptor: `+0x2890` reads `'GEND'`, `+0x2894` reads
`0xFDFDFDFD`, `+0x2898` is the first byte after the CRT block.

### Native proof (i3-3220, original DLL bytes)

Harness `harness/gimme_host.cpp` loads the original DLL and calls `ConvertFile` the way
`004dbe36` does. With `--guard` it redirects the DLL's `HeapAlloc/HeapFree/HeapReAlloc/
HeapValidate` imports so every block ends exactly at a `PAGE_NOACCESS` page (8-byte heap
granularity kept).

| Mode | ALLdrivr.fsh images 0–8 | Result |
|---|---|---|
| plain heap | 0, 1 | access violation (game crash) |
| plain heap | 2, 4, 8 | `galloc - INVALID SIZE <negative>`: garbage count reached `galloc(count*8+8)` |
| plain heap | 3, 5, 6, 7 | returned 1 with a garbage-dependent result |
| `--guard` | all 9 | `FAULT eip=101054ec … past heap block (HeapAlloc size 0x28c0) at block offset 0x28c0` |

`0x28c0 = 0x2890 + 12 (galloc frame) + 0x24 (CRT header and no-man's-land)`, and `101054ec` is
`cmp dword ptr [edx+0x2898], 0`: the very first read of the record count is already outside the
block. The plain-heap outcome depends on whatever follows the block, which explains the 3-in-12
crash rate seen in the game. The community shim (EmulateHeap + HeapPadAllocation) only pads the
heap, so the count usually reads as zero; it does not fix the copy.

Reproduce:

```
harness\build-host.cmd <out>
<out>\gimme_host.exe gimme.dll ALLdrivr.fsh out.fsh <index> --guard
```

## 2. Component inventory

`harness/gimme_about.cpp` calls every module's `about()` in the original DLL. The full dump is in
[components.md](components.md).

## 3. Recovered source and builds

Source: `source/recovered/gimme.dll` (`build.cmd <out>` → `gimme-faithful.dll`, `gimme-fixed.dll`,
`gimme_oracle.exe`). The only difference between the variants is `GIMEX_FIX_DESCRIPTOR_COPY` in
`dev/FaceInRace/FaceInRace.cpp`: descriptor copies allocate and copy the source's own `size`, as the
same-size branch of `10001450` already does. `_sem_arquivo/platform.cpp` selects the x87 `sin()` of
the static CRT (the VC6 CRT of the original has no SSE2 path).

Recovered and proven against the original bytes (oracle `gimme_oracle`, same process, `--pad` heaps):

| Part | Evidence |
|---|---|
| FaceInRace, GIMEX core, Nil | ConvertFile on ALLdrivr.fsh frames 0–8 identical; `--guard` faults identically |
| about() of 69 modules, 37 filters, 10 quantizers | 116 records byte-identical; mutation detected |
| is() of 67 modules + GIMEX_detect | 15 504 scores on a 228-file corpus; only PNG differs (libpng pending) |
| FSH module (92 functions) | 554 game files: 7295 frames read, 7293 rewritten identically |
| Crop, Size, Remap filters, Wu quantizer | 1371 generated cases identical; mutations detected |
| BMP, TGA, PCX readers | 541/549 generated + Pillow files identical; 8 corrupt inputs are UB in the original |
| ConvertFile on BMP/TGA/PCX photos | 51 Pillow photos identical; mode-1 TGA: no output on both sides |

Boundaries (explicit stubs in `boundary.h`, reported through `gerror`): readers of the 61 modules
other than Nil, FSH, BMP, TGA, PCX, JPG, TIF and PNG, all writers except FSH, JPG and PNG is() and the JPG/TIF/PNG readers (they need the public
IJG 6a, libpng 1.0.3 and libtiff 3.4 sources), the QuickTime open used by MOV is().

Second original defect, kept in both variants: a 1×1 source photo makes the Size filter read index −1
(`gimme+0x246d3`, address `fffffffc`); the faithful DLL faults at the same address.

## 4. Game test

`PorscheLowered.exe Porsche.exe` with `PORSCHE430_NATIVE=1` in `local/run-430` (original game code;
startup reaches ConvertFile on its own via `004dbe11`), killed after 22 s per run. Without a player photo
the game converts `ALLdrivr.fsh` image 8 ("driv").

| DLL | Runs | Crashes | pic16.fsh written |
|---|---|---|---|
| original | 12 | 3 (`gimme+0x1055ac`) | — |
| gimme-fixed.dll | 20 | 0 | 20, all identical |

The 20 pic16.fsh files (MD5 `61a160ea…`) equal the original DLL's output for the same image.

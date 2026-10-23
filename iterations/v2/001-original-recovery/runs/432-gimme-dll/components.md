# gimme.dll components

Sources of each claim: strings in the original image (VA given), the runtime `about()` dump
([about-dump.txt](about-dump.txt), produced by `harness/gimme_about.cpp` on the original DLL)
and the Ghidra index `research/binary-index/ghidra/gimme.dll-3a43b0f6a160`. Versions marked
"exact" are the library's own version string; "family" means the exact release still has to be
pinned by a differential test against the published source.

## Image layout

| VA range | Content | Evidence |
|---|---|---|
| `10001000`–`10004e95` | FaceInRace (EA): `ConvertFile`, image resample/convert, `galloc/gfree`, file I/O callbacks. Compiled with `/GZ` (`__chkesp`) | PDB `D:\dev\FaceInRace\Debug\FaceInRace.pdb`; "galloc - …" diagnostics |
| `10004e96`–`10005a3f` | GIMEX core dispatch (module table `10431a50`, 69 modules × 9 entry points), format detection | no `__chkesp`: built separately |
| `10005a40`–`1010b8a0` | 69 GIMEX format modules (table below) | `about()` dump |
| `1010b8a0`–`10134000` | GIMEX filters (Gamma, Texture Map, Chroma Key, Clean Edges, Composite Blend, Flip, …) and colour quantizers (Wu, Exact, Low Colours) | property strings, authors F. Barchard, G. Shaw, L. Ancessi, A. Brownsword |
| `10134000`–`10229000` | third-party libraries, below | version strings |
| `10229000`–`1024a000` | MSVC 6 debug CRT (libcmtd, `dbgheap.c`, `i386\chkesp.c`) | assert file names; compiler 12.00.8447 |
| `10401000`–`10409fff` | `CSEG` code section | not yet attributed |
| `1024a000`–`10400fff` | leftover NFS5 object data, never executed | memory note `gimme-dll-debug-objects` |

## Third-party libraries

| Library | Version | Evidence |
|---|---|---|
| libpng | 1.0.3, January 14, 1999 (exact) | `1040e194` "libpng version 1.0.3 - January 14, 1999" |
| zlib | 1.1.3 (exact) | `10412f68` " deflate 1.1.3 …", `1041b858` " inflate 1.1.3 …" |
| IJG libjpeg | 6a, 7-Feb-96 (exact) | `1040f254` "6a  7-Feb-96", `1040f264` "Copyright (C) 1996, Thomas G. Lane" |
| libtiff | 3.4 family (codec registry `TIFFRegisterCODEC`, `LZWDecodeCompat`, fax tags `FaxRecvParams`); no version string linked | relative assert paths `tiff\tif_*.c` |
| MPEG-2 decoder (MSSG) | mpeg2decode V1.2a, 96/07/19 (exact) | `1043f2e0`; wrapped by `mpeg\mpeglib.c` (Sasa Djolic, module 59) |
| Avid OMF Interchange Toolkit | version not yet found | "OMFI_ERR…" strings, `ToolkitVersion` property |
| Apple Bento container library | Apple Computer 1991–1993, by Ira L. Ruben | `104167b0`; used by OMF |
| 3dfx Texus | version not yet found | "Texus: %s", `txMipWrite`, `txMipRead`, NCC "Neural nets" |
| QuickTime for Windows glue | — | `QuickTime.qts`, `_CallComponentFunctionWithStorage` |
| Video for Windows | — | imports `MSVFW32` `ICCompress/ICDecompress…` (AVI module) |

## GIMEX descriptor generations

Every module's `info()` allocates the image descriptor (`GINFO`) and writes its tag and size.
The six shape modules (1, 25, 32, 45, 48, 49; version 2.07) use `0x2aa4` bytes; every other module
and FaceInRace use `0x2890` (allocation sites `10041144`, `10052f22`, `100669b7`, `1008c40f`,
`100c3a62`, `10109112` versus `push 0x2890` in the others). See the [README](README.md) for why this
matters.

## GIMEX format modules

Reached by `Porsche.exe`: detection runs over all 69 modules; readers BMP (2), TGA (5), PCX (16),
JPG (55), TIF (60), FSH (1); writer FSH (1).

| # | Module (about name) | Short | Version | Author | Extensions | about | info | write |
|---|---|---|---|---|---|---|---|---|
| 0 | Nil Gimex | Nil | 1.02 | FrANK G. Barchard |  | `1010b860` | `1010ba3d` | `1010b849` |
| 1 | FSH Shape File | FSH | 2.07 | F Barchard | .fsh | `10106e80` | `10109112` | `100f9b24` |
| 2 | Windows BMP | BMP | 1.24 | FrANK G. Barchard | .bmp .rle | `100f83d0` | `100f8692` | `100f73a6` |
| 3 | Windows Icon | ICO | 1.00 | FrANK G. Barchard | .ico .cur | `100f5ea0` | `100f619e` | `100f52e6` |
| 4 | S3 Texture | S3T | 1.03 | FrANK G. Barchard | .s3t .s3tc | `100f46e0` | `100f49a3` | `100ebb47` |
| 5 | Targa | TGA | 1.37 | FrANK G. Barchard | .tga .vda .icb .vst | `100ea480` | `100ea8ee` | `100e9756` |
| 6 | Amiga ILBM | LBM | 1.20 | Frank Barchard | .lbm .ilbm .bbm .iff | `100e8480` | `100e88df` | `100e7716` |
| 7 | TIM PSX Texture Image | TIM | 1.05 | FrANK G. Barchard | .tim | `100e6b80` | `100e6e0e` | `100e6546` |
| 8 | HSI Raw | HSI | 1.07 | FrANK G. Barchard | .hsi .raw | `100e5d10` | `100e6111` | `100e5a26` |
| 9 | Scitex SCT | SCT | 1.02 | FrANK G. Barchard | .sct .sc | `100e5200` | `100e552a` | `100e4f46` |
| 10 | Adobe Photoshop 4.0 | PSD | 1.13 | Frank & Julian | .psd .pdd | `100e31b0` | `100e3eb9` | `100e1d51` |
| 11 | DPaint ANM | ANM | 1.12 | D. Gyles & F. Barchard | .anm | `100e0dc0` | `100e1233` | `100e0820` |
| 12 | Adobe FilmStrip | FLM | 1.02 | FrANK G. Barchard | .flm | `100df440` | `100df825` | `100df076` |
| 13 | Binary Info File | BIF | 1.04 | FrANK G. Barchard | .bif | `100ddf89` | `100de282` | `100dc9ff` |
| 14 | SGI RGB Image File | SGI | 1.07 | FrANK G. Barchard | .rgb .sgi | `100dbb70` | `100dbeca` | `100db526` |
| 15 | Macintosh Pict | PICT | 1.18 | Frank/Gerry/Laurent | .pict .pic .pct | `100d8750` | `100db465` | `100d8046` |
| 16 | ZSoft PCX | PCX | 1.05 | FrANK G. Barchard | .pcx .dcx .pcc | `100d7060` | `100d743e` | `100d69e9` |
| 17 | Portable Pixel Map | PPM | 1.05 | FrANK G. Barchard | .ppm .pbm .pgm .pnm | `100d5f20` | `100d623c` | `100d5c36` |
| 18 | ACT Photoshop Palette | ACT | 1.02 | FrANK G. Barchard | .act .pal | `100d55d0` | `100d5981` | `100d5506` |
| 19 | WaveFront RLA | RLA | 1.06 | FrANK G. Barchard | .rla .rlb | `100d4860` | `100d4c23` | `100d3f66` |
| 20 | QuickTime Movie | MOV | 1.31 | FrANK Barchard & Kaz Okuda | .mov .qt .moov | `100d2f37` | `100d3bf5` | `100d1297` |
| 21 | Alias Pix | PIX | 1.00 | FrANK G. Barchard | .pix .als | `100d0af0` | `100d0e13` | `100d0876` |
| 22 | FLIC Animation | FLI | 1.06 | Frank Barchard | .fli .flc | `100cfc78` | `100d009a` | `100cf2af` |
| 23 | Gimex Images | GMX | 2.14 | A.Brownsword | .gmx | `100cc850` | `100ccd86` | `100c963a` |
| 24 | PC Font File | FFN | 2.30 | Gerry Shaw | .ffn | `100c7380` | `100c7ddb` | `100c6408` |
| 25 | PSH Shape File | PSH | 2.07 | F Barchard | .psh | `100c17d0` | `100c3a62` | `100b4474` |
| 26 | SoftImage PIC | Sim | 1.08 | FrANK G. Barchard | .pic .sim | `100b3d47` | `100b401c` | `100b2e79` |
| 27 | TGV Movie | TGV | 1.39 | L.Ancessi & F.Barchard | .tgv | `100b0390` | `100b1ba4` | `100aa763` |
| 28 | Compuserve GIF | GIF | 1.15 | FrANK G. Barchard | .gif | `100a8b70` | `100aa2c5` | `100a8758` |
| 29 | ATI VQ Texture | VQT | 1.02 | FrANK G. Barchard | .vqt | `100a6f90` | `100a7263` | `100a6016` |
| 30 | MDEC Movie | MDEC | 1.35 | FrANK G. Barchard | .str .xa .xar .dct | `1009e99c` | `100a1edf` | `10092217` |
| 31 | PSX Font File | PFN | 2.30 | Gerry Shaw | .pfn | `1008fdb0` | `10090945` | `1008edb8` |
| 32 | VSH Shape File | VSH | 2.07 | F Barchard | .vsh | `1008a120` | `1008c40f` | `1007cdc4` |
| 33 | Sony2 Font File | SFN | 2.30 | Gerry Shaw | .sfn | `1007aa30` | `1007b5ab` | `10079a48` |
| 34 | Nitendo64 Font File | nfn | 2.30 | Gerry Shaw | .nfn | `10077610` | `10078058` | `10076788` |
| 35 | MVI Movie | MVI | 1.14 | F Barchard & A Brownsword | .mvi .cmv | `10075e29` | `100761ec` | `10072242` |
| 36 | Latenight Text Palette | TXP | 1.03 | FrANK G. Barchard | .txt .txp | `10071fa0` | `100721ac` | `10071b9f` |
| 37 | Ninja 3 CharMap | CMP | 1.04 | FrANK G. Barchard | .cmp .chr .pal | `10070d90` | `100710c1` | `1010b849` |
| 38 | Encapsulated Postscript | EPS | 1.05 | FrANK G. Barchard | .eps .epsf .ps | `10070ae0` | `10070d66` | `10070386` |
| 39 | Erik Kiss RAW | Raw | 1.04 | FrANK G. Barchard | .raw | `1006fdb0` | `1007009b` | `1006fc6c` |
| 40 | Raw Grey Scale | GS | 1.03 | FrANK G. Barchard | .gs .rgs | `1006f710` | `1006f9c8` | `1006f566` |
| 41 | Inverse Table | INV | 1.02 | FrANK G. Barchard | .inv | `1006efc3` | `1006f270` | `1006eb1a` |
| 42 | Stareo 3D | S3D | 1.04 | FrANK G. Barchard | .s3d .tga | `1006e6d0` | `1006e8ee` | `1006c5a6` |
| 43 | PSX VRAM Viewer | VRM | 1.01 | FrANK G. Barchard | .vrm .vram | `1006b580` | `1006b79d` | `1006af1c` |
| 44 | Font Shape | FSHP | 1.11 | Gerry Shaw | .sfs .pfs | `10069100` | `100693bf` | `100690e9` |
| 45 | NSH Nintendo 64 Shape File | NSH | 2.07 | F Barchard | .nsh | `10064740` | `100669b7` | `100573e4` |
| 46 | Bank Mask | BAM | 1.04 | FrANK G. Barchard | .bam | `10057110` | `10057304` | `10056c7f` |
| 47 | ACOM YUV | YUV | 1.06 | FrANK G. Barchard | .yuv | `100562cf` | `1005661b` | `1005569c` |
| 48 | DSH Shape File | DSH | 2.07 | F Barchard | .dsh | `10050c90` | `10052f22` | `10043934` |
| 49 | SSH Sony Shape File | SSH | 2.07 | F Barchard | .ssh | `1003eed0` | `10041144` | `10031b74` |
| 50 | QuickTime3 Movie | QT3 | 1.00 | Kaz Okuda | .mov .qt | `100310b0` | `10031742` | `10031099` |
| 51 | TQI Texture Quantized Image | TQI | 1.01 | Martin Griffiths | .tqi .444 | `10030a20` | `10030dea` | `1003092c` |
| 52 | ClipBoard Gimex | CLP | 1.03 | Kaz Okuda | .clp | `100304e0` | `10030784` | `1002eb50` |
| 53 | Abobe Illustrator | AI | 1.01 | Kaz Okuda | .ai | `1002bbdc` | `1002cfa8` | `10023729` |
| 54 | Open Media Framework | OMF | 1.01 | Kaz Okuda | .omf | `10022700` | `10022e51` | `100226e9` |
| 55 | JPeg | JPG | 1.10 | FrANK G. Barchard | .jpg .jpeg .jfif | `100219d2` | `10021d3c` | `100214b8` |
| 56 | Audio Visual Interleave | AVI | 1.10 | Kaz Okuda | .avi | `1001f1d0` | `10020b38` | `1001e723` |
| 57 | Portable Network Graphics | PNG | 1.06 | Kaz Okuda | .png | `1001c830` | `1001cc34` | `1001bfc6` |
| 58 | 3DO Cel | CEL | 1.11 | L Ancessi & F Barchard | .cel .anim .sanim .ani .san | `10019c3d` | `1001a843` | `1010b849` |
| 59 | MPEG | MPG | 1.01 | Sasa Djolic | .mpg .mpeg | `10018d00` | `1001903b` | `10018ce9` |
| 60 | Tiff | TIF | 1.04 | FrANK G. Barchard | .tif .tiff | `100185b0` | `100188c7` | `100182ab` |
| 61 | Layout | LAY | 1.09 | Gerry Shaw | .lay | `10016ff2` | `1001760c` | `100168d5` |
| 62 | VAN DOS/PC | VAN | 1.00 | Sam Deasy | .van | `10015310` | `1001592c` | `10013a30` |
| 63 | Quake Model Texture Gimex | QMT | 1.00 | Julian Fong | .mdl | `10013440` | `1001379e` | `10013429` |
| 64 | Madcow Movie | Mad | 1.09 | Kaz Okuda | .mad | `100125d0` | `10012b2f` | `10012224` |
| 65 | Material | MAT | 1.02 | Kaz Okuda | .mat | `1001165c` | `10011bfc` | `10010cd7` |
| 66 | 3Dfx Texture | FX | 1.05 | FrANK G. Barchard | .3df .txs | `10010020` | `100104f3` | `1000f70b` |
| 67 | PowerVR Texture | PVR | 1.01 | Kaz Okuda | .pvr | `1000dd6f` | `1000e162` | `1000c9e4` |
| 68 | Movie Gimex | uV | 1.05 | Kaz Okuda | .uv .tgq | `100089c0` | `10009026` | `10005c4e` |

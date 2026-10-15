# Run 213 — callable contract inventory

Read-only navigation from cached 201/207/208 inputs; original PE/corpus and report SHA pins are in `summary.json`.
Candidate for contract reuse: `00537b40` (416 bytes), uses `DAT_006bd97c`/`DAT_006bd984`; C2065=17, C2664=4, C2440=2.
Its 179 source SHA is `ed787305373b627f4fd7d20264fd4f0e63703d0cef9a02366d4579f0e35dffb1`; smallest remaining cached body after exclusions.
`00562680` (368 bytes) was excluded as canonical/WIP recovered source; all 206/207/208/210/212 and pending 211 scopes were excluded.
Reuse boundary: 006bd97c/006bd918 = stdcall raw32/raw32 RET8; 006bd984 = stdcall raw32 RET4; identity does not prove caller prototypes or data ownership.
No source lowering, compiler, native, Ghidra, or semantic allocation was performed; this is navigation only.

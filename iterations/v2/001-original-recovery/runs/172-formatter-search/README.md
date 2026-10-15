# Run172 - original CRT search and case comparison

Source: Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Index-first queries: 005ae3c0, 005a1e10, 005a2780, their incoming calls,
original ASM and disjoint ranges. The 169 actual game-link frontier has unresolved
compare_005ae3c0 (FE text) and render_settings_read_config_005a1e10 (substring test).
Root owns their binding aliases; this packet provides canonical typed bodies.

Three full indexed bodies: compare208 B, substring133 B, character188 B (529 total).
The index assigns shared return tail005a2770..2774 to substring, but character
branches there. Both functions require it. Substring's one-byte needle tail jumps
to the interior character entry005a2786 with AL=character, original stack intact.

Character search aligns by byte, then uses original 7efefeff/81010100 DWORD
candidate and zero detection. Candidate words are reread before byte selection.
Substring preserves original pair comparisons, overlapping restart, and byte reads.
Compare reads right then left. ASCII path folds only A-Z. Locale path uses inline
LOCK INC/DEC, signed writer>0, lock19, and canonical158 inner lowercase. Upper24
bits of EAX/EBX survive subsequent AL/BL loads and are passed to inner lowercase.
No host str*/ctype replacements. Existing locale state and lock owners are reused.

Private MSVC Win32 and original Unicorn compare returns/pointers, poisoned arena,
ordered byte/DWORD reads, canonical lower table accesses, map/lock arguments and
mutable state. Native inline-assembly checks ESP/EBX/ESI/EDI/DF on every call;
Unicorn also checks EBP. Native compiles the real158 lower body; map/classification
and lock are explicit controlled fixture boundaries. Production has no observer.

Build/check:
```
local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/172-formatter-search -B local/builds/v2/formatter-search-172 -A Win32
local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-search-172 --config Release
py -3 scripts/research/verify-v2-formatter-search.py
```

First complete instrumented comparison:9374 cases,126092 ordered reads. Final reports
also count original interior005a2786 and shared005a2770 reachability. Boundary
snapshots capture readers/writer/locale before every lock/map/classify call.
Signed writer values0,1,7fffffff,80000000,ffffffff, counter wraparound,
all byte characters, pointer alignments0..3, overlaps, empty inputs, random text,
map failure/success and mutation of locale during mapping are explicit cases.

An additional private build with PORSCHE_SEARCH_READ_TRACE=OFF runs the same batch
and writes production-verification.json; it compares every return/state/arena and
boundary event while excluding only the absent private read-event field.

This packet closes two typed CRT consumers, not game startup or visual acceptance.

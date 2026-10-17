# Run 279 — physical-file storage preflight

- `006af080` is a signed 32-bit count and `006af084` is a `PhysicalFile*` declaration in the current WIP `files.cpp`/`files.hpp`; Run224 records the corresponding canonical mangles.
- Both addresses are adjacent 4-byte virtual-zero cells in writable `.data`; no HIGHLOW relocation lies inside either cell.
- Exact indexed direct MEM4 references, raw-byte occurrences and unindexed gaps are recorded per cell in `summary.json`; pointer-record width and possible adjacent 8-byte base are kept separate.
- This is navigation evidence only. WIP/canonical status, raw symbol consumers, whole-program address-taking and storage allocation remain blocked pending the listed gaps.

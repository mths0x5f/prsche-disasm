# Run264 — connected heap functions in the actual native union

Run261 plus Run263: **1125 distinct function VAs + 15 support objects**,
1140 archive members / 1,295,200 bytes. Archive SHA-256:
`2fd9f221a696431ef25839d9c1292967c12353eda80c96c1562e6e9d21577502`.

The actual link reports **419 names / 581 diagnostics**, no EXE/DLL. The canonical
free dependency is resolved; its real heap table and two platform critical-section
providers are now exposed. This is +2 names versus Run261 (one closed, three added).
The ten-consumer raw `FUN_00531f90(unsigned return, int argument)` name remains an
explicit ABI binding task; no alias is inferred merely from its compiled VA.

7493 pins pass before/after; 1137 symbol snapshots reused, three new COFFs read,
zero compiler commands, one archive/link, collector 9.579 seconds. No overlap or
unexpected duplicate definitions. The linked frontier comprises 87 missing
bodies, 32 canonical owners outside the union, one compiled-VA ABI mismatch,
283 data names and 16 other contracts. These counts do not measure the remaining
work of the complete game. Verified Run173 remains 476 full + 6 partial functions.

Exact invocation: [command.json](command.json). Actual artifacts/receipts:
`local/experiments/v2-native-union-264/`. Summary identity, native directive,
closure and actual linker checks: [validation.json](validation.json).
Use fresh output/run paths when replaying the command.

The refreshed automatic research queue is [Run265](../265-link-frontier-queue/README.md).
Next: prove the raw free ABI binding, connect existing Win32 platform providers,
then trace the real heap table and initialization. Gameplay/fault/concurrency
acceptance and the full-game launch remain open.

# Run 364: DirectInput mouse startup children

Status: three bounded original bodies integrated after Run361. Fresh build001
compiles194 TUs/8 projects:215 unresolved names/222 refs,no EXE. Two names close
and two renderer-snapshot dependencies are exposed. Shared audit: validation.json. `00572690` frame initialization is
deferred because its callback targets `00572640/70/80` are unrecognized by the
binary index and supplemental REA365 failed on the first target. Do not bind
new callback cells or zero `006a644c` without consumer and ownership proof.

Source is `Porsche.exe` SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries used `query-binary-index.py --binary Porsche.exe --address`
`0x537070`, `0x5370c0`, `0x5727c0` with `--disassemble`, plus their references
and callees in `research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d`.
REA362/001 covers `005370c0` and `00572690`; REA365/001 produced partial
cleanup and cursor dossiers but its session failed on callback recognition and
is not audited PASS. The original bodies are `00537070..005370ad` (62 bytes),
`005370c0..0053727d` (446 bytes), and `005727c0..005728a4` (229 bytes).

The cleanup body calls mouse Unacquire then Release, clears its pointer, then
releases and clears the DirectInput pointer. Mode selection writes the existing
361 slots; access mode 7 preserves the original Unacquire, cooperative-level
retry and Acquire order and uses original flags 5 or 6. Raw original
`005de758/5c/60` initializes to `4,2,1`, not zero. Cursor application clamps
signed x/y against canonical renderer bounds, writes limits, calls the existing
cursor helper, then restores the original lock/snapshot path. The state-copy
helpers `00570ed0/00570f00` remain typed externs, as do unresolved live
renderer/window dependencies. No callback implementation or DirectInput8
transport was invented.

Run the shared native comparison:

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/364-mouse-startup-children/native-config.json --attempt 3
```

Native attempt 003: **PASS**, 31 original/C++ cases and 33,883 byte/return
checks at both `/Od` and `/O2`; three mutations detected. Fixture validates
raw PE mode and cursor data before scenario overrides, pins original body and
jump-table hashes, compares COM call order, diagnostics, state and cursor
clamping. Receipt:
`local/experiments/v2-mouse-startup-children-native-364/003/receipt.json`.
Earlier attempts 001/002 are retained; 002 passed both comparison variants but
stopped at a duplicate mutation anchor. This run does not establish a linked
EXE, live DirectInput operation, or frame callback acceptance.

Root review also checks all three raw PE diagnostic strings in constant-proof.json.

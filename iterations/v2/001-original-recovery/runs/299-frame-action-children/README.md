# Run299 — original frame-action children

Original `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, indexed `00476710..00476797`,136 bytes. Index query `00476710` identifies calls from `0047619b` and `00476851`; the accepted registry has no exact or covering owner. Run274 has a prototype input pin for this address, without a compiled game-object owner. The existing297 declaration is preserved unchanged.

`00476710.cpp` implements `FrameActionBoundary_297::update_00476710(uint32_t)` with original ECX/self, one DWORD stack argument and RET4. It caches the group at `read(self+0xc)+index*0x38` across callbacks. Each iteration reloads the child table at cached `group+0x34`, uses child stride`0x18`, reads object flag byte`+4` before any null test, and either invokes virtual destructor slot0 with argument1 or virtual update slot`+0x1c`. After destruction it reloads the child table, clears exactly six DWORDs in that record, then reloads the cached group's count at`+0x14`. It finally clears that count, including the initially empty path. Changes to self's table pointer do not change cached group identity.

One `/MP6` batch compiled two translation units in1.045s. Game COFF contains exactly one definition and zero unresolved, weak, or common symbols. Original machine-code bytes occur only in the separate fixture oracle, whose virtual callbacks are test providers. No original bytes or test providers are linked into the game object. Summary and actual receipts identify the source, COFF SHA, compiler, dependencies, tool pins and common shared input manifest.

The native fixture compared648 bounded valid-memory states against all136 original bytes, requiring no original CALL relocation. Cases vary group index0/1/2, count0..3, zero/nonzero field`+0x10`, object flags0/1/255, mixed child paths, and callback mutations of the child table, self table, cached count and next object. Every case compares the entire4096-byte arena, callback arguments/order, stack cleanup, preserved nonvolatiles and DF=0. Null object faults, arbitrary invalid pointers, huge counts/indexes and whole-game behavior remain outside this finite verification. Initialization and Run296's buffer/layout HOLD remain open.

```powershell
py -3 scripts/research/experiment-v2-frame-children-299.py --attempt 001 # completed; do not repeat
py -3 scripts/research/audit-v2-frame-children-299.py
```

The first producer invocation stopped before compilation because its private output-directory constant was wrong; this was corrected before capture. There was exactly one actual compiler batch, link and native execution. The audit rechecks preserved receipts and pins without rerunning them. The game target has not been rebuilt in this packet.

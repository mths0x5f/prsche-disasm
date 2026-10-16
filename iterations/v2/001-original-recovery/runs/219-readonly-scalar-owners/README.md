# Run 219 — read-only scalar owner evidence

`005b242c` is `.rdata`, bytes `0000c842` (100.0f); `005b24a8` is `.rdata`, bytes `0000803f` (1.0f); both VA/file alignment is 4 and neither four-byte range has a HIGHLOW relocation.
Original indexed disassembly has 55 direct four-byte x87 reads of `005b242c` and 683 of `005b24a8`; no direct writes, address-taken, or array-width forms were found in the indexed references.
194/179 list both as undefined/1-byte formal aliases; 194 records 00485100 direct width 4, while 202 records only native consumer 00485100 with expected `?_DAT_005b242c@@3MA` / `?_DAT_005b24a8@@3MA`.
At 004851a4/004851bb the original bytes are `d81d2c245b00` (`FCOMP [005b242c]`); at 004851ce the bytes are `d805a8245b00` (`FADD [005b24a8]`).
Evidence supports exact read-only four-byte views as a candidate; it does not prove a native owner, allocation, global coalescing, or behavior outside indexed refs.
No compiler, Ghidra, native execution, storage allocation, or source edits were performed.

# Run212 audit — byte consumers

`audit.py` independently verifies the finalized capture: source/include/object hash closure, actual COFF symbols, 57 original PE instructions, five total byte-slice replacements across two functions, and measured batch exit `0` at `1.437s`.
The private 179 `uint4` views for `DAT_005de62c` and `DAT_006b16a4` are retained; `00598630` additionally uses the exact 179 `int4 DAT_006b17d0` view. These are local consumer views, with no canonical owner or storage allocation claim.
The single `C4146` warning is retained from unchanged unsigned negation/SBB-NOT behavior and is treated as defined modulo-32 arithmetic evidence; it is not suppressed as a semantic fix.
Candidate/global-alias only: signed overflow, full-body byte checks beyond the recorded slices, native execution, caller ABI and global lifetimes remain open. No production/union/registry edit, compiler rerun, or Ghidra action.

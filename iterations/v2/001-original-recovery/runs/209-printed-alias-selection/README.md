# Run209 — printed-alias selection

Read-only selection from Run201 cache + Run206 missing97 frontier; audit189 was not rescanned. Seven VAs have sole cached blocker C2065 printed globals after excluding 203-provided `00540480/005404e0/00554530/0058f1f0`; 202 `00485100` does not intersect.
Preferred order is `004012b0` (three 179 float4 RAM cells) then `0056daf0` (one 179 float4 RAM cell); `_DAT_005b24a8` is only a 16-byte `.rdata` observation with unresolved alias/type and is not an owner.
Selection: `004012b0`, `0056daf0`, `0040af70`, `00537ed0`, `0058f5d0`, `00598630`, `004032d0`; all have no cached pointer/uint/call-argument diagnostics, only C2065.
179 formal type/storage conflicts and missing aliases are recorded per VA in `summary.json`; no WIP/canonical owner was found in the searched registry/docs.
Navigation only: no semantic proof, allocation permission, lowering, compiler, native, or Ghidra work.

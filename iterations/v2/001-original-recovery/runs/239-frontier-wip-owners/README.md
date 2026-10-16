# Run 239 — missing-function WIP owner inventory

- Frontier233 has 93 `no_compiled_union_body_or_canonical_owner` functions; 6 have exact WIP definitions in two current source files, 3 have only probe/reference mentions, and 84 have no source owner hit.
- `formatter_stdio.cpp` owns exact `005a177b`, `005a36ea`, `005a3719`, `005a373c`, `005a376b`; `005a3719/005a376b` are already covered by Run240 canonical reuse.
- `application_state.cpp` owns exact `0053c290`; these are reuse candidates, not new implementation permission.
- `004deda0`, `00562680`, `00592490` have declarations/probe or call references only; they are not claimed owners.
- Run224 accepted canonical VAs do not intersect these 93. Remaining 84 need source ownership/call tracing; no compiler/native/Ghidra/commit was used.

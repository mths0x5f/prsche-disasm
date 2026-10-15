# Run205 — float/integer representation inventory

Read-only inventory of pinned audit `local/experiments/v2-scalar-slices-189/full/audit.json` and original `decompiled.c`; source SHA256 is `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, audit SHA256 is `1206eb99f84a2999a948e17b0945b7c5fb5ff5a872b4293d8984ee1eadb2f1db`.
Historical audit189 signals: C4244 `1041` matches/`246` bodies, C4305 `74`/`32`, C2440 `6017`/`1917`; C2440 is a general compiler code, not FP-specific. Strict `(float|double)` regex has `3785` occurrences/`539` bodies; occurrences are not asserted erroneous casts.
Intersections are VA matches against the older compiled sets ordinary192 (`924`) and leaf196+197 (`146+2`), plus the 199 frontier's `109` rows classified `no_compiled_union_body_or_canonical_owner`; they are not latest 202 warnings.
Priority queue for bounded CAST/RAM export: missing109 `0040af70`, `0040bfe0`, `0040b650`, `00406520`, `004edf00`, `0049ae30`, `004f3e40`, `00562680`, then `00518880`, `00532b20`.
These are navigation candidates only; diagnostics and regex occurrences do not prove original consumer semantics or an error. No compiler, Ghidra, native, EXE, or full-input rerun was performed.

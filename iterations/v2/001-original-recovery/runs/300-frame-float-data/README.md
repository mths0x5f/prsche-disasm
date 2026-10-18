# Run300 — exact frame float data

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. The binary-index query for `005b47d8` and `005b2764` yields 9 and 26 references, respectively. The bounded probe decoded the exact original instructions, then checked the PE section table and HIGHLOW table. Both cells are independent 4-byte values in nonwritable `.rdata`: `005b47d8 = 00 00 fa 45` (8000.0f) and `005b2764 = 00 40 1c 46` (10000.0f). All 35 raw address literals are relocated operands of indexed 4-byte reads. None is an observed write or address-taking instruction; no interior address literals, relocation inside either cell, or direct operand crossing its boundary was found. `original-evidence.json` retains every site and operand. Adjacent values are deliberately not claimed as part of either cell.

`frame_floats_300.cpp` defines only the two external `const float` symbols needed by Run295, in separate read-only COFF sections. Its one `/MP6` compiler invocation produced one data-only game object with exact 8 PE data bytes, zero COFF relocations and undefined symbols, and the two expected C++ mangles. The Run295 tail object independently has those two exact unresolved mangles. The producer captured repository input and source-dependency manifests through `v2_shared_manifests`; its immutable compile receipt is under `local/experiments/v2-frame-floats-300/001`. `summary.json` and `validation.json` record the object and checks. Independent `audit.json` rechecks the PE instructions/relocations, native COFF data bits, manifests, receipt and Run295 link-symbol contract without recompiling.

```powershell
py -3 scripts/research/audit-v2-frame-floats-300.py
```

That command was already captured; `audit.json` is immutable. No game target link or executable run was performed. The evidence proves these two direct consumers' scalar bytes and symbols, not original whole-section layout or every possible indirect access. The next integration step is to add `frame_floats_300.cpp` as a game source alongside Run295, then check a fresh game link.

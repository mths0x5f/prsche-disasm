# Run210 audit — bounded consumer views

`audit.py` independently verifies the frozen Run210 capture: both source/include/object hashes, actual COFF symbols, 61 original PE instructions, original bytes at `004012cf` and the `004032d0` caller sequence, plus measured batch exit `0` and `1.073s`.
`004012b0` retains its complete body unchanged; the generated header has seven exact 179 externs and adds `_DAT_005e66ac` as signed `int32`, justified only by original `FILD m32int` at `004012cf`.
`004032d0` uses exact 179 `undefined4 *DAT_005e671c`; its caller evidence supports `ECX=self`, stack argument `1`, callee cleanup `4`, and ignored return. The pointer type is absent from the exported type manager, so the typed vcall remains a bounded lowering.
Candidate-only result: x87 intermediate rounding/overflow and actual callee fidelity remain deferred; no production/union/registry change, compiler rerun, native execution, or Ghidra action.

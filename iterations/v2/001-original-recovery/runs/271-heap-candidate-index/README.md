# Run271 — navigation-only heap consumer index

Published four candidate spans in
`research/binary-index/supplemental/heap-consumers-271.jsonl`, with a separate
supplemental README. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Source: frozen Run270 preflight SHA256
`c53bf19e7713a27a8457b7dc6914e0f49298eaaf23daee0526ff3e3fbf3394f9`.
All 510 bytes /167 instructions were redecoded and checked against the actual PE.

Records use `candidate_entry_va`, `entry_status: unproved` and
`recovery_status: navigation-only`; there is no authoritative `entry_va` key.
They preserve exact instructions, byte/source hashes, boundary evidence, callees,
closed internal branch targets, known raw incoming calls and absence of known
indexed entry/relocated-pointer references. Table operands are explicitly
classified as PUSH address, indexed MEM4 reads or CMP immediate. No function,
implementation, calling convention or storage extent is inferred from them.

Old manual index/corpus and frozen267/270 artifacts remain unchanged. No compiler,
native program, Ghidra, storage allocation, alias/coalescing or union operation
ran. **Run267 HOLD remains; this index is not heap allocation approval.**

Commands from the repository root:

```powershell
py -3 scripts/research/index-v2-heap-candidates-271.py
py -3 scripts/research/index-v2-heap-candidates-271.py --validate
```

Generation refuses existing output. Validation only reads inputs/index and
refreshes validation.json. Fifteen pins and before/after guards pass. Seven
meaningful negative checks reject changed PE bytes, body hashes, original SHA,
an authoritative entry key, status promotion, storage approval and instruction
tampering. Zero authoritative or accepted functions were added.

Next: trace raw incoming CALL candidates `0056a1c1` and `0056a483`, establishing
their entry/instruction/control-flow context. Trace `0053c290` fill-dispatch
consumer behavior as needed. Entry/liveness evidence for the first three spans
remains missing; their aligned RET/NOP/CFG structure alone does not resolve it.

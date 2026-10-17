# Run270 — omitted heap-consumer boundary preflight

Four complete contiguous PE spans were recovered for coordinator review. No
existing index was changed, no supplemental entry was created, and no storage or
implementation was added. Their instruction boundaries are structurally strong;
authoritative external entry references remain unresolved.

Original `Porsche.exe` SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Source query: the four unindexed HIGHLOW operand sites from frozen Run267.
`preflight.json` pins the PE, old indexes, catalog and Run267 evidence, preserves
body/instruction-source SHA256, exact bytes, complete CFG targets, callees,
incoming-reference scans and nearby indexed boundaries.

- Candidate `005697d0..005697e6`: 23B /7 instructions, CALL `0053c290`.
  Starts after indexed RET `005697c2` and 13 NOPs; terminal RET followed by
  nine NOPs. Raw instructions request fill(base006b4f20,zero,64), then return1.
- Candidate `00569a40..00569a6a`: 43B /16 instructions, CALL `00531f90`.
  Starts after indexed RET `00569a37` and eight NOPs; terminal RET followed by
  five NOPs. Its conditional branch and loop target actual instruction starts.
- Candidate `00569b10..00569b3b`: 44B /13 instructions, no CALL.
  Starts after raw RET `00569b09` and six NOPs; nearest prior catalog range ends
  `00569aca`. Terminal RET followed by four NOPs; closed internal CFG.
- Candidate `0056a1f0..0056a37f`: 400B /131 instructions, CALL `00537ed0`.
  Starts after raw RET `0056a1e9` and six NOPs; nearest prior catalog range ends
  `00569aca`. All internal branch targets are instruction boundaries. The
  terminal RET is followed immediately by another apparent prologue at
  `0056a380`; that adjacent body is not promoted here.

The fourth span matches two existing indexed 400B /131-instruction bodies,
`0053cbc0` and `00571f90`, byte for byte except the single CALL REL32 operand.
All three call the same indexed `00537ed0`. That is useful independent boundary
and instruction evidence, without proving runtime liveness or a public ABI.

Full executable-section E8/E9 scanning and full PE HIGHLOW scanning found no
direct incoming candidates or relocated entry pointers for the first three.
The fourth has two raw direct-CALL candidates at `0056a1c1` and `0056a483`; neither
is within an indexed function/instruction range. No indexed direct entry edge
exists for any of the four. Raw opcode matches outside known boundaries remain
navigation only, not established callers. Absence of these forms does not prove
that no runtime-computed entry exists.

The focused `candidate-listing.asm` contains all 510 bytes /167 instructions.
It explicitly labels them candidates. Successful disassembly, RET/NOP padding,
alignment and closed CFG alone do not establish authoritative external function
entries; HOLD remains until coordinator review. The old `manual-functions.jsonl`
bytes are pinned and untouched. Any approved future index material belongs in a
new supplemental file, not that frozen index.

Command from the repository root:

```powershell
py -3 scripts/research/preflight-v2-heap-consumer-index-270.py
```

The script refuses completed output, runs no compiler/native/Ghidra commands and
checks input pins before/after. An early path-normalization error was fixed before
it read the PE or emitted evidence; the successful run produced the current
preflight without index mutation. Next decision: either retain these spans as
candidate navigation only, or obtain independent entry/control-flow evidence
before publishing function entries. Heap allocation/coalescing remains blocked.

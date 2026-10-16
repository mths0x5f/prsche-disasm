# Run 260 — x86 backend coverage

- Frozen 252 frontier: 85 original bodies; backend 257 syntax census: 25 supported, 60 rejected.
- Exact PE body bytes/call graph are pinned in `summary.json`; remaining opcode families and supported instruction counts are recorded there.
- Up to three closed direct-call chains are selected only when syntax-supported and free of indirect calls/global operands; this is navigation, not acceptance.
- No compiler, native execution, gameplay implementation, ABI or fidelity claim.

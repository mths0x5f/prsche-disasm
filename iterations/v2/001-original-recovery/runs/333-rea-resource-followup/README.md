# Run333: allocator, drive and search through a reusable REA session

One persistent REA6.7.0/Ghidra12.1.3 MCP session on a SHA-checked private copy
of Porsche.exe confirms005682a0(236B),005916a0(111B) and005a2780(188B).
Original SHA is ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39;
original and copy hashes before/after agree. ServerPID195444 and server identity
remain unchanged; Ghidra child PID was not measured. No AI API provider is used.

Session140.36s; cold allocator117.94s, repeat59.53ms, drive49.83ms,
search142.74ms. Repeated normalized allocator dossiers agree. Native329/331 and
canonical intake330 cross-review these instructions; analysis itself is not
native or game acceptance. Search's188 indexed bytes do not absorb its shared
return tail into a new original-function count.

The client/runner are now shared tools, driven by versioned queries.json.
Future sessions can change query manifests without copying another client and
runner. Commands, messages, all responses/errors/logs, Node/REA/client/config
hashes and unchanged copied PE are pinned under
`local/experiments/v2-rea-resource-followup-333/001/receipt.json`.
The read-only auditor verifies result ranges against the original index and
records original PE body hashes. Query manifests and outputs are trusted only
as analysis evidence; inferred prototypes still require instruction/consumer review.

```powershell
py -3 scripts/research/audit-v2-rea-session.py --config iterations/v2/001-original-recovery/runs/333-rea-resource-followup/queries.json --attempt 001
```

The completed session is reused. For genuinely new analysis, use a new query
manifest/experiment and an unused attempt with scripts/research/run-v2-rea-session.py.
No original binary, global MCP registration or historical receipt is modified.

Current generic auditor accepts success-only manifests. The client can retain
explicitly allowed error probes, but those require a matching targeted audit
policy before acceptance; none are used by333.

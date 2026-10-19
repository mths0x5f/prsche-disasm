# Run308 — persistent REA MCP stdio session

This is an isolated SDK-protocol test of the published `rea-agents@6.7.0` server and its already installed portable Node 26.12.0/Ghidra 12.1.3 environment from Run302. It does **not** register an MCP server or skill in the IDE. The original `local/game/Porsche.exe` (SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`) is read only. Every attempt uses its own SHA-verified copy under `local/experiments/v2-rea-mcp-session-308`.

`scripts/research/rea-mcp-session-308.mjs` uses the matching `@modelcontextprotocol/client` 2.3.1 and `StdioClientTransport` to start `rea mcp`, initialize, save the actual 207-tool `tools/list` and selected schemas, open the PE with `provider_id: ghidra`, query `analyze_function` twice, inspect `binary_session` between calls, then close. The client records all decoded JSON-RPC messages from server stdout, the server stderr stream, full tool responses, timings, the server PID, and target hashes. `scripts/research/run-v2-rea-mcp-session-308.py` adds immutable attempt receipts and process output. Its commands are:

```powershell
py -3 scripts/research/run-v2-rea-mcp-session-308.py --attempt 003
py -3 scripts/research/audit-v2-rea-mcp-session-308.py
```

Attempt 001 hit sandbox `spawn EPERM` before MCP initialization. Attempt 002 initialized, listed tools, opened the PE and reached the native query, but `analyze_function` rejected `address`; the actual discovered schema requires `procedure`. Attempt 003 used that schema and passed. In one MCP server process (PID 168488) and one `analysis_run.run_id`, the first native query for `00476170` took 86,368 ms; the repeat took 23 ms. Both returned identical normalized function evidence: `00476170..00476218` (169 B), caller `00487e20`, direct callee `00476710`, and two unresolved indirect calls. The second Evidence explicitly says it was loaded from a local REA analysis snapshot and did not rerun the provider. The target SHA was identical before and after. The frozen binary index agrees on those address and call facts. `audit.json` checks all of this and pins repository inputs/sources via `v2_shared_manifests.py`.

To distinguish exact-result caching from another native function query, the follow-up copied the harness into `scripts/research/rea-mcp-session-308-004.mjs` and kept prior attempts/source frozen:

```powershell
py -3 scripts/research/run-v2-rea-mcp-session-308-004.py --attempt 004
py -3 scripts/research/audit-v2-rea-mcp-session-308-004.py
```

Attempt 004 passed in one MCP server process (PID 161708) and one analysis run ID across four `binary_session` observations. `00476170` cold took 86,662 ms; its exact repeat took 24 ms and declared snapshot reuse. A **different** function, `00476710`, then returned in 65 ms with 136 bytes and callers `00476170` and `00476810`, matching the frozen index. Its Evidence has no snapshot-reuse limitation. This supports the inference that the active REA provider/session can serve new Ghidra analysis after the cold import, beyond exact-result caching. The session telemetry reports `analysis_activity: not_observed` and does not expose a live Ghidra PID, so it does not prove Ghidra process identity. `audit-004.json` verifies the protocol sequence, data, timings, same server/run identity, target hash, and separate manifests.

No game build, global configuration, IDE registration, or API key was involved. REA tools were not exposed in the root IDE tool inventory; this result is a standalone local MCP client/server session.

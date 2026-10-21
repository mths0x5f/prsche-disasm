# Run340: canonical heap/context state

The original default/live managers, selector pointer and adjacent arena/guard/
page/object-ID fields now have one physical owner. Initialization publishes the
live manager before clearing its records and reloads it after each lock callback.
Queue allocation retains the original cached pool/selector and per-node callback
reloads. Object creation preserves unmasked selector/arena stores and the locked
argument's low byte. Shutdown restores the default manager with the original
callback ordering and late ID/selector reads. The accepted Run311 JMP wrapper
is reused unchanged; the duplicate definition detected in build001 was removed.

Source: Porsche.exe SHA ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
Index queries:005e4fe8/005e4fec,005e3e18/005e4700 and consumers0059e9d0,
0059edb0,0059ebc0,0059eb20. REA339/340 and callback-map.json record the evidence.
The two original default callbacks and shutdown body are new recovery; three
existing bodies are corrected. Getter aliases and the existing wrapper are not
counted as new original algorithms.

Native attempt025 passes344 cases at each of /Od and /O2 (688 total), including
callback replacement, physical index16 alias, failure paths, static callback
identity and original stack/register ABI. Seven targeted production mutations
are detected. Actual compiler dependency closure and native outputs are pinned.
The 450-input shared audit also checks actual COFF owners and build graph.

Fresh build003 compiles175 C++ TUs/8 projects:259 unresolved names/274 refs,
noEXE or execution. Five names close; six real helper/callback boundaries appear.
Build001 retains the duplicate-wrapper failure;002 is incremental and is not
the fresh compile proof. The shared builder now enforces a complete clean build.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/340-heap-context-state/acceptance.json
```

New runs use the same verify-v2-native-batch.py, run-v2-rea-session.py and
build-v2-game-batch.py with configs and unused attempt IDs. Passed native tests
are not repeated for bookkeeping. Failed local attempts remain preserved.

Controlled child callbacks do not prove their complete implementation. Missing
three live callbacks, queue cleanup, heap destruction and secondary shutdown
remain explicit link boundaries. The modeled adjacent ranges preserve tested
aliases; arbitrary out-of-object addresses, complete allocator/OS composition,
root providers, transform-cell ownership and game/visual acceptance remain HOLD.
Old078 heap/bootstrap receipts are historical, not current-source acceptance.

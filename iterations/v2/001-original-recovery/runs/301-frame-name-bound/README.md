# Run301 — TRACK_NAME has no proven31-character invariant

Original `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. Queries `00657444`, `005d2ac8`, `00439e68`, and neighboring registration records connect the Run296 copy source to **TRACK_NAME**. Original resource `005d5274` is the exact11 bytes `TRACK_NAME\0`. Store sites `004b29a1/004b29ab/004b29b5` create the12-byte registration at`005d2ac4`: identifier`0x10f`, destination pointer`00657444`, label pointer`005d5274`.

The actual consumer `004b4b80..004b4cca` walks12-byte records beginning at`005d1e40`, selects the matching identifier and reads its destination pointer. For identifier`0x10f`, comparisons at`004b4c82/004b4c8a` take the inline-string branch at`004b4ca3`. The loop`004b4cab..004b4cbc` copies bytes untilNUL, without a31-character limit. Calls at`004155da` and`0048f9b8` feed packet records to this consumer; their immediate loops advance through records using`004b4cd0`, without a TRACK_NAME-specific length check in those excerpts. No claim is made about every upstream packet producer.

Four bounded original-byte executions first execute the original registration-store span`004b0ff0..004b4b75`, then the complete consumer with controlled id`0x10f` packets containing31/32/40/63 characters. All four strings survive unchanged into`00657444`. Executing the original initialization-copy cutpoint`00471b70..00471b99` next preserves those exact lengths:31 leaves the root canary intact;32/40/63 overwrite bytes of`00628960`, and40/63 also overwrite the following buffer at`00628964`. This demonstrates a concrete consumer path admitting longer strings and their memory effects. It does not establish that a shipped game resource or full game session supplies those packets. The store span is indexed under`004b0fa0`; its independent function entry/liveness is not promoted by this experiment.

The second writer at`00439e68` passes destination`00657444` to`005a0fbf`, using the format string at`004fbf30`'s returned item`+8`. The60-byte lookup`004fbf30..004fbf6b` searches a pointer vector through`00691d00` for a signed16-bit item identifier, falling back to the first item; it checks no string length. The format resource is dynamic and was not identified as a fixed literal. Original wrapper`005a0fbf..005a1010` initializes a stream with remaining capacity`0x7fffffff` before calling`005a4371`; a separate original cutpoint verifies that exact capacity. The wrapper supplies no destination-size limit of31. Neither an assumed plain-string format nor an upstream resource-size bound is substituted for evidence.

**Storage remains HOLD.** Any shared layout must retain destination`00628940`, root`00628960` at offset32, and the following buffer`00628964` at offset36 whenever crossing writes are admitted. The final extent still needs an upstream allowed-length bound; these bounded examples do not justify allocating an arbitrary large buffer or copying the entire original data section. Original constructor/store and cleanup remain separate unfinished algorithms.

`evidence.json` records original instruction bytes, registration/resource bytes, all four packet/source/destination windows and the formatter stream state. Common shared manifests pin all producer inputs. No storage definition, compiler invocation, native fixture, game build or game execution was added. The audit checks preserved evidence and closure without rerunning the producer.

```powershell
py -3 scripts/research/trace-v2-frame-name-301.py # completed, once only
py -3 scripts/research/audit-v2-frame-name-301.py
```

If a stronger bound is required, inspect payload construction upstream of`004155da/0048f9b8` and the actual resources behind the item vector`00691d00`. The bounded consumer trace is complete; no exhaustive upstream search was attempted.

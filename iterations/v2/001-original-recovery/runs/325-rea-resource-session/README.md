# Run325: persistent REA resource session

One fresh REA6.7.0/Ghidra12.1.3 MCP session analyzed a private SHA-checked copy
of Porsche.exe. No AI API provider or global MCP configuration was used.

The session completed in110.90s. Cold exists analysis took93.26s; repeat took
19.45ms. Subsequent constructor/open/device dossiers took17–30ms. The same
server identity and PID189684 were retained; the Ghidra child PID was not measured.
Original and copy SHA before/after match
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Function dossiers cover00561b80(20B),00533f00(52B),00568260(51B),00561ca0(63B),
00568e90(35B),00591760(27B). Repeated normalized exists evidence is identical.
Ghidra's inferred void return labels for exists/constructor are not ABI evidence:
instructions and callers consume EAX. Runs326/327 use the actual instructions.

REA does not recognize00561ce0 as a function. Its error is retained, alongside
context, decoded entry/last instruction and276 raw bytes checked against the PE.
Run327 records supplemental callback coverage; this session does not accept its
behavior, shared transform state006ad750 or a physical filesystem backend.

Local raw requests/results/logs and receipt:
`local/experiments/v2-rea-resource-325/001/`. Validation pins every output plus
client/runner/Node/REA server inputs. No full-game or native behavior acceptance.

```powershell
py -3 scripts/research/audit-v2-rea-resource-325.py
```

The completed session is reused; do not rerun it merely to refresh metadata.

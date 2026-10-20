# Run 423 — bounded `_getstate` modes

Canonical owner: `source/recovered/Porsche.exe/input_state.cpp`, original
`Porsche.exe` SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
The indexed body is `00532e10..00532f34` (293 bytes), SHA-256
`f8f0b37499524cfa089f53c5d4737bd8e14e6e5e7185a7513011c03d038c3a4a`.
Index query: `query-binary-index.py --binary Porsche.exe --address 0x532e10 --disassemble`.
No new function owner is introduced; this extends the existing partial owner.

The mode table at `00532f38` selects count (1), capabilities (2), state (6),
property (8), and the invalid-mode diagnostic. The type table at `00532f58`
selects state sizes `0x50/0x10/0x100/0x50` from the low byte. The source strings
and diagnostic lines `0x1fa/0x219` come from the original PE. Invalid mode pushes
format and mode, then pops eight bytes; invalid type pushes only format.

`input_caps_buffer_006bde20[0x21c]` is defined once by the canonical source.
The original buffer sits `0x220` bytes before the slots, including a four-byte
gap. The port does not preserve this adjacency. A full original HIGHLOW scan
found only two references into the buffer/gap, at `00532edf` and `00532ef1`, both
targeting its base; this is bounded evidence, not proof against computed aliases.
The original caps helper clears `0x21c` bytes; its success parser remains an
explicit existing boundary. This change does not recover that parser.

Negative indices and indices >=32 admitted by the signed count compare remain
typed boundaries. They are not tested or accepted. Count is captured on entry,
and callback results/state are compared only within the documented valid slots.
The existing fixed-argument diagnostic declaration is called through an x86
cdecl variadic view for the invalid-mode path. The actual game diagnostic body
and complete game execution remain outside this fixture.

Review on 2026-10-20 rebuilt the final PR22 head `1b907749e4b0c8a507d795fc38ebd7cc4e120a84`
in `local/experiments/pr22-review/snapshot`. Original source, headers and generator
were materialized byte-for-byte using `git show`. The retail PE was copied
read-only for this work. The only native-run adaptation was selecting local
MSVC `14.44.35207/bin/Hostx64/x86/cl.exe`; source and generated fixture were not
changed. Fresh summary/validation replace the earlier records that described
the buffer as an undefined external.

Fresh checks:

- Native original-PE slab: **24/24**, compile/link/run exit zero. Both jump tables,
  poll/read chain, original strings, return value, trace and post-state are checked.
- Rebuilt `input_probe`: **1026** Unicorn comparisons pass.
- Rebuilt `input_snapshot_probe`: **13** comparisons pass.
- Rebuilt `input_buffer_probe`: **37** comparisons pass.
- Rebuilt `startup_input_probe`: **8** comparisons pass.
- Corrected audit: fresh source/header/fixture/compiler hashes, prepared input
  hashes, actual COFF object, receipt/log hashes and native record pass. An old
  summary fails rather than producing a stale green result.

Artifacts are under `local/experiments/pr22-review/snapshot/local/experiments/v2-input-getstate-423`
and `snapshot/local/probes/*`. Commands used from the repository root:

```
py -3 local/experiments/pr22-review/review_setup.py
py -3 local/experiments/pr22-review/review_setup.py native
py -3 local/experiments/pr22-review/probes.py
py -3 local/experiments/pr22-review/proposal/audit-v2-input-getstate-423.py --root local/experiments/pr22-review/snapshot --summary local/experiments/pr22-review/proposal/summary.json
```

The historical eight source mutations were not repeated during review and are
not claimed as fresh results. These bounded comparisons do not prove physical
DirectInput behavior, arbitrary callback mutation, nonvolatile/FP ABI state,
negative-index layout, the caps success parser or full-game acceptance.

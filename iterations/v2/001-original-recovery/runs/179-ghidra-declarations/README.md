# Run179 — complete read-only Ghidra declarations

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first input: `research/binary-index/README.md`, the cached analyzed
`local/experiments/binary-index-ghidra/binary-index` project and the frozen
5772-entry Porsche corpus. No analysis, signature commit, game-data write,
accepted-source change or behavioral acceptance is performed.

Ghidra12.1.3/x86/windows exported all5772 functions successfully. Coverage/VA
uniqueness and source/tool hashes passed independent JSON validation. The
program reports changed=false before and after export. Exported359 database
types and79841 listing data records; native DataTypeWriter declaration errors0.
HighFunction globals contain15877 occurrences/6278 identities,837 identities
with incompatible observed type/storage/declaration variants, and5441
unambiguous memory-global extern declarations. Every variant retains its
consumer VAs. Conflicts are excluded from the shared globals header.

Outputs in `export/`:

- `types.h`, `types.jsonl`: native DataTypeWriter output plus database paths,
  widths, alignment, composite members/offsets, enum values and type links.
- `listing-globals.jsonl`: every defined listing datum, VA/extent/labels/type
  and native declarator. This is an inventory, not a set of allocated owners.
- `functions.jsonl`, `prototypes.h`: every inferred getC signature verbatim,
  database signature/source, inferred calling convention, extra-pop, return
  and parameter storage/varnodes, hidden/this parameters, and HighFunction
  global declarators. ABI metadata is authoritative only as observed inference;
  the textual prototype alone does not carry every calling-convention detail.
- `globals.jsonl`, `conflicts.jsonl`, `globals.h`: aggregate observed variants,
  explicit conflicts, and unambiguous memory-global declarations respectively.
  Unnamed register symbols such as MXCSR remain in JSON and are not emitted
  as fabricated C globals. Overlapping addresses retain their original views;
  this packet supplies no storage definitions or independent-owner assumption.
- `provenance.json`, `capture-provenance.json`, `progress.json`: finalizer and
  capture exporter/tool SHA pins, completion/errors and unchanged-program flags.

ABI inference census:3472stdcall,1301thiscall,984fastcall,15cdecl; no inferred
varargs. These are Ghidra classifications, not proof that unknown source ABI
has been recovered. There is one spelling difference against frozen getC
signatures:005a5304 getSignature emits `__CxxThrowException@8`, while getC
prints `__CxxThrowException_8`. The other5771 signatures match after whitespace
normalization. Both spellings remain explicit; no corpus rewrite occurs.

This is a declaration recovery input, not a ready MSVC header set. A native
Win32 `/Zs` probe of the unmodified `types.h` records13 errors from pointer32,
wchar_t and dependent image-offset declarations. Ghidra also prints undefined6
as unsigned long long, so native textual type output alone cannot establish
exact storage width. There are1431 frozen bodies with address-like printed
tokens absent verbatim from their HighFunction symbol names, commonly `_DAT_`
views of `DAT_` symbols. All observed gaps are saved in `summary.json`; typed
alias/partial-width/overlap lowering must use actual consumers, not guessed
globals. Compile/link/behavior acceptance and existing backlog remain open.

The complete capture succeeded before aggregation encountered one unnamed
MXCSR symbol. Finalizer-only replay corrected that handling from all saved
records: fresh=0, no repeated function decompilation. Captured records retain
their old exporter/tool identity; finalizer source/tool hashes are separate.
Finalizer mode refuses incomplete captures or changed captured Ghidra tools,
so it cannot mix old inference chunks with a new exporter run. Atomic records
live under `local/experiments/v2-declarations-179/checkpoints/<capture SHA>/`.
Normal runs use their own exporter/tool SHA directory and resume only exact
matching records. Temporary incomplete files are not completion records.

Reproduce a new capture, or finalize the existing complete capture:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2-declarations-179.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2-declarations-179.ps1 -FinalizeCapturedIdentity fe1853a85cc62e08f3311b3b93cdb7c1cfdb1d96f07886d323345308101aa57e
py -3 iterations/v2/001-original-recovery/runs/179-ghidra-declarations/audit_export.py
```

Ghidra arguments include `-process Porsche.exe -noanalysis -readOnly`.
Logs: `local/reports/179-export-full.log` and `179-export-finalize.log`;
native header probe: `local/experiments/v2-declarations-179/types_probe.log`.
`summary.json` pins every exported artifact and records coverage, ABI census,
signature/name gaps and the failing raw-header probe without hiding failures.
Next: body-scoped declaration/printed-alias and ABI lowering, then compile
and COFF dependency measurements; preserve unresolved semantics separately.

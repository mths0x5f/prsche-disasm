# Run181 — real x86 objects from the automatic C++ corpus

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query: Porsche.exe full function/decompiler catalog, followed by the pinned
Run178 C++ syntax results. Source corpus remains unmodified; no guessed function
or global-storage definitions are supplied.

All707 Run178 C++ syntax-pass candidates generated real MSVC x86 COFF objects;
zero code-generation failures. The separate automatic-candidate archive is755630
bytes. Within this subset122 external symbol names/313 object references remain
unresolved. This frontier is separate from the accepted173 game-link267/303:
the automatic subset does not contain the original entrypoint or complete startup.
Archive creation is not executable linking, a game launch, or ABI/behavior proof.

The initial code-generation pass took279.553 seconds with six compiler processes.
It reuses the pinned178 syntax results instead of repeating5772 syntax checks.
No deep original-behavior acceptance is performed here. Per-object sources,
commands, COFF symbols and hashes are recorded in summary.json; binary objects,
archive, complete compiler logs and generated TUs stay under local/experiments.
Repeated global constant names in the report are compiler COMDAT constants;
the report deliberately lists their definitions instead of suppressing them.

Run177 separately compiles the full004d3420 application-context body with explicit
unresolved effect/address seams. Its semantic binding is not replaced by this
automatic subset. Run179 exports missing type/global/prototype declarations;
Run180 lowers proven integer helpers using changed-body validation. These are
the next bulk expansion steps. Hidden register contracts, inferred prototypes,
overlapping globals, extended floats and real initialization remain open in
docs/recovery-validation-backlog.md.

Reproduce from the pinned generated Run178 inputs:
```powershell
py -3 scripts/research/audit-v2-compile-corpus.py --phase prototypes --language cpp
py -3 scripts/research/build-v2-compile-corpus.py
```
On an existing valid Run178 audit, run only the second command. No common
production rebuild, original differential suite or corpus SHA regeneration is
required for an isolated object-generation experiment.

The first command regenerates exploratory files under local; preserve historical
audit hashes before rerunning. Summary input pins are authoritative for this run.

# Run182 - incremental real C++ object build

Original Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index source: complete original corpus and frozen178/180/183 compile provenance.
Private compile experiment; accepted production/registry unchanged.

728 real x86 COFF objects in a separate candidate archive;
707 byte-identical objects reused after checking generated TUs,
recorded include dependencies and object SHA. Only21 new
compiler invocations;0 code-generation errors. Final measured build time
16.004 seconds, including archive creation and input/output pin checks.
This is incremental work, not a claim of equivalent full-rebuild speedup.

Within the subset:124 undefined names/363 object references.
Archive805092 bytes; no game EXE/startup/fidelity claim.
Original entrypoint and complete dependency graph remain open. No missing
function/global storage is replaced by a stub or guessed behavior.
Historical178/181 compiler binary SHA was not recorded: path/version match,
stronger historical identity remains explicit. Current compiler binary SHA is
pinned; subsequent deltas require it and preserve all prior dependency pins.

```powershell
py -3 scripts/research/build-v2-compile-delta.py
```

Full commands/symbols/input/source/object/archive pins are in summary.json.
Generated TUs, compiler logs and binaries stay under local/experiments.
The syntax helper/model acceptance and outstanding ABI/storage/x87/global
conflicts remain in180/183 packet READMEs and recovery-validation-backlog.md.

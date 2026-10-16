# Run 220 CLI negative validation

The frozen Run220 driver was exercised with actual 216 baseline and 217 support inputs; no compiler, native, library, link, or Ghidra command ran.
Repeated 217 support path rejected with exit 1 before outputs; tampered 217 alias target/directive rejected by actual COFF `.drectve` comparison with exit 1.
Duplicate support packet rejected with exit 1 on duplicate/self-referencing alias validation; each case used a fresh output/run path.
All three cases produced zero output files, zero run files, zero `.lib`/`.dll`, and zero `*.execution.json`; logs/native command count are explicitly recorded in `cli-validation.json`.
Support objects remain separate from function counts; `original-readonly-data` is accepted only as an explicit support kind.

# Run204 — reusable ordinary and leaf packet union

Extends frozen `audit-v2-native-union-198.py` in a new driver:
`scripts/research/audit-v2-native-union-204.py`. Accepts repeatable
`--ordinary-summary` and `--thiscall-summary`; rejects repeated paths and
overlapping compiled VAs before running native tools. The two negative CLI
checks passed with zero native commands: `cli-validation.json`.

Exact source/include/object SHA closures and cached symbol identity are checked.
Run203 has no observed compiler exit code after a metadata crash. Such a row is
selected only with explicit successful code-generation, valid actual i386 COFF,
object-only certification and zero owned errors; the driver then independently
checks the actual object and symbols. A missing exit code is never changed to zero.

The first actual combined archive/link is recorded in
[Run206](../206-frontier-and-float-union/README.md). No new compilations, source
repairs, data definitions, ABI bridges or production-registry changes are made by
this collector. Compile candidates remain separate from accepted original behavior.

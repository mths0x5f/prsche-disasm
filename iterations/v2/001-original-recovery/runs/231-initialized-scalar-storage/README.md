# 231 — three initialized writable scalar cells

One C++ data-only support object supplies exactly three current int32 native views selected in Run230. Original `Porsche.exe` SHA256: `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

- `005ccb34`: PE bytes `80000000`, initializer **128**, native symbol `?DAT_005ccb34@@3HA`; two indexed MEM4 reads.
- `005d0608`: PE bytes `01000000`, initializer **1**, native symbol `?DAT_005d0608@@3HA`; two indexed MEM4 reads and one write.
- `005e5f4c`: PE bytes `0a000000`, initializer **10**, native symbol `?DAT_005e5f4c@@3HA`; two indexed MEM4 reads.

The script independently matched all seven indexed instructions to actual PE bytes and decoded operand widths/access. All seven HIGHLOW target sites are covered; no relocation overlaps a cell and no HIGHLOW target points inside a cell. Original `.data` is readable/writable/non-executable. Four actual cached consumer COFFs require the exact signed-int mangles. Current frontier variants have no overlapping storage view; a live scan of canonical/WIP recovered source and headers found no address/name match, and the registry has no entry owner for these data addresses. These checks do not establish computed-pointer or whole-program alias ownership.

`original_scalars.cpp` uses writable `.ogw$ns`, separate from the readonly `.orig` namespace. Actual i386 COFF contains exactly 12 initialized bytes `80000000010000000a000000`, exactly the three expected external symbols, no undefined symbols, no code, and no relocations. Its SHA256 is `bd9bed80575b35cea0079176abc8c9b4c99b7bdd59126231c1c0b098c97440f7`. Native object offsets describe this object only: the original cells are nonadjacent and **no original relative-layout claim** is made.

One `/MP6` compiler batch built data1 + fixture1: measured exit **0**, **1.023017 s**, no diagnostics. Private fixture link exit **0** (0.356082 s), native execution exit **0** (0.027843 s). Exit/time/log receipts were written before result attribution. The fixture checks initial bits, distinct storage, six raw write/read patterns per cell (`0`, `1`, `7fffffff`, `80000000`, `80000001`, `ffffffff`), unchanged other cells, and restoration to 128/1/10. Actual fixture PE `.ogw` is writable and retains the exact initial bytes. Fixture SHA256: `f53e11479ba3ee5a6e3b9f3aef5432bcb08689cf0405d72046b1c2859a47abcf`.

37 input pins passed before/after mutation guards. Readonly helpers from221/226 were reused without edits. `audit.py` independently rereads PE/COFF bytes, relocations, seven decoded accesses, source/object pins and durable receipts; it does not compile or execute native code.

```powershell
py -3 scripts/research/experiment-v2-initialized-scalars-231.py
py -3 iterations/v2/001-original-recovery/runs/231-initialized-scalar-storage/audit.py
```

Collector interface: `summary.kind = original-writable-data`, support id `initialized-scalar-cells-231`, `compiled = true`, `compiler_exit_code = 0`, generated source/object/dependency hashes and actual symbols. **Zero new functions.** No union, production, or shared/frozen source changes. Future aliases, computed references, whole-data layout, lifetime and game behavior remain deferred.

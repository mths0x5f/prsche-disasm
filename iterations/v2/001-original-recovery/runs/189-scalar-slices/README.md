# Run189 — bounded scalar byte slices

Final syntax passes923 ->924: new00553a70, zero lost. Across5772 rows,5733
unchanged184 results are reused;39 changed TUs contain99 rewrites. The12-TU
pilot is cached, leaving27 checks in one `/MP6` batch,5.806 seconds, zero
attribution fallbacks. Errors53108 ->53062; p-code-category errors154 ->93;
48 error-limited functions remain explicit. No recovered-function/ABI acceptance
or original-game behavior claim is made.

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navigation starts at `research/binary-index/README.md`. Installed Ghidra12.1.3
source contracts, with complete hashes in summary.input_pins:

- `printlanguage.cc:723-730`: `_offset_size_` is decimal byte offset and byte size.
- `printc.cc:2009-2133`: partial symbols emit that artificial member when no
  named subtype resolves. The token does not retain field signedness.
- `opbehavior.cc:172-177,753-769`: COPY/PIECE/SUBPIECE operate on bitvectors.

That signedness loss prevents blanket unsigned replacement in arithmetic.
Accepted changes are62 exact CONCAT bitvector inputs,18 standalone integer
copies,15 one-byte integer zero tests and four integer constant stores. Objects
must have unique precisely sized native scalar local/parameter declarations and
proven in-object extents. Globals, pointers, booleans, unknown/hidden inputs,
array/composite objects, compound assignments and general numeric contexts are
excluded. The manifest retains519 unsupported slices with concrete reasons.
Floating objects are permitted only as explicit CONCAT bitviews; no floating
assignment or numeric conversion is lowered. Integer template traits enforce
that every generated store/copy has integer source/destination objects.

The helpers access object representation through unsigned char. Writes first
snapshot source bytes, so overlap preserves original source values and every
unmodified destination byte. Simple object/value expressions evaluate once.
No global storage, alias relationship, initialization, field signedness or ABI
is guessed. One native x86 executable passes1920 byte-oracle checks, including
integer overlap and float/double NaN bitviews without floating arithmetic.

```powershell
py -3 scripts/research/experiment-v2-scalar-slices-189.py --jobs 6
py -3 scripts/research/experiment-v2-scalar-slices-189.py --full --jobs 6
```

Output: `local/experiments/v2-scalar-slices-189/full/audit.json`. Existing184
per-row headers and source provenance are retained; changed rows add
`scalar_slice_header`/hash, actual `generated_source`, and `forced_headers: []`.
All5772 source hashes,2462 header hashes and generator hash are verified. New
reports/header/audit files use LF before hashing. Final invocation counters were
recomputed from captured batch reports after correcting inherited184 counters;
compiled source/header bytes and compiler outputs were unchanged, so no compiler
rerun was required. Raw compiler outputs and batch attribution are preserved.

Frozen audit SHA256:
`1206eb99f84a2999a948e17b0945b7c5fb5ff5a872b4293d8984ee1eadb2f1db`.
Helper SHA256:
`b2e25229e51cdfc7a318a4d77c2ed3a82416399e3eb0988109e6604c8dc53d74`.
Remaining numeric slices need exact original p-code output types/consumer traces;
unproven extents and original stack/global aliasing remain separate work. Root
owns shared plans, native-object follow-up, registry and handoff.

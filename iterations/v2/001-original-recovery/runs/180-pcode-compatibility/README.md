# Run180 — exact integer p-code compatibility experiment

Owner: pcode180. This is a compile-graph experiment, outside the recovered game
sources and function registry. Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navigation: `research/binary-index/README.md`, then the unchanged
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/decompiled.c` corpus (5772 bodies).

The helper vocabulary comes from installed Ghidra12.1.3 source, not inferred
game algorithms. `summary.json` pins complete source/header/script hashes:

- `opbehavior.cc:252-271`: zero/sign extension.
- `opbehavior.cc:324-363`: unsigned carry, signed addition/subtraction overflow.
- `opbehavior.cc:753-769`: PIECE concatenation and SUBPIECE byte truncation.
- `typeop.cc:1124-1131,1150-1157,1342-1382,2050-2057,2129-2136`:
  decimal suffixes encode input/output BYTE widths, not bit counts.
- `printc.cc:805-829,862-901`: extension/subpiece functional printing.

The isolated header implements all1..8-byte integer results. It reads/writes
the object representation on the explicitly asserted x86 little-endian target;
odd widths retain exact `undefined3/5/6/7` storage rather than becoming64-bit
values. All arithmetic uses unsigned64-bit values and bounded shifts. The
helpers evaluate each argument once. Floating bit representations may be
extracted without floating arithmetic; float10/16 remain opaque storage.
`CONCAT28` (five occurrences;10-byte result) and `SUB104` (two occurrences)
remain explicit blockers. No guessed globals, game function stubs, free
`__thiscall` substitution, corpus modification or recovered-function claim.

One native x86 executable batches3288 boundary checks and196608 exhaustive
8-bit carry/overflow checks. Expected boundary values are generated with Python
unbounded integers. All199896 checks pass. This proves the helper bitvector
contract, not decompiled game behavior or hidden register semantics.

The frozen178 C++ copied-prototype audit is reused as baseline. Exactly257
helper-using bodies recompile with unchanged MSVC x86 `/Zs /TP` flags and compiler
error limits;5515 unchanged bodies reuse pinned actual178 diagnostics. Every
reused generated source is byte-identical to178, including scalar/prototype
text. Changed sources insert the helper include immediately after the scalar
include. Nothing is forced-included globally. Per-row `generated_source`,
`forced_headers`, `compatibility_header` and cache provenance support object
builds without injecting helpers into reused sources. The merged audit still
contains all5772 bodies. Compiler path/version match178;178 did not pin its
historical compiler binary hash, so that stronger identity claim remains open.
The current binary hash is pinned. Corpus/body/source/scalar/exporter/header
hashes are checked before reuse and shared inputs again after compilation.

An early forced-include ordering attempt and the corrected all-body attempt
were aborted before completing the census. Their partial logs/sources remain
in `full-aborted-ordering-and-all-body` and `full-aborted.log`; they are excluded
from final comparison counts. The delta strategy avoids5515 redundant compiler
invocations. No end-to-end speedup is claimed from these differing experiments.

Final comparison: syntax passes707 ->728, failures5065 ->5044,21 new passes,
zero lost passes. P-code-category error diagnostics691 ->180 across67 functions;
the residual180 are169 template-deduction errors (often caused by unresolved
arguments), seven undeclared wide helpers and four surrounding syntax errors.
The header is therefore not claimed to resolve180 independent helper
implementations. Error-limited functions65 ->63 remain explicitly listed.
The measured delta runner time was136.011 seconds, including source pinning and
copying;178's93.485-second full compile time has different work/environment and
is not a speedup comparison. Native helper checks are separate from syntax
acceptance. Full per-body compiler logs retain their actual diagnostics.

```powershell
py -3 scripts/research/experiment-v2-pcode-compat.py --jobs 6
```

Detailed diagnostics, generated sources, helper header and executable stay in
`local/experiments/v2-pcode-compat-180`. The unchanged178 audit JSON schema is
preserved at `prototypes-cpp-0000/audit.json` for181 object/link follow-up.
`summary.json` is the compact versioned comparison. Header179 integration,
ABI-preserving thiscall lowering, x87 arithmetic, globals/overlaps and remaining
decompiler type conflicts are separate work. Root owns shared plans/status.

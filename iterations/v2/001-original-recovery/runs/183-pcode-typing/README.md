# Run183 — exact24-bit PIECE argument casts

Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`;
5772 original pseudo-C bodies remain unchanged. Original navigation begins at
`research/binary-index/README.md`. Run180 integer helpers stay frozen.

The169 C2672 diagnostics in65 functions do not establish169 missing scalar
overloads. Run180 already accepts independently typed signed/unsigned scalar
arguments. Actual failing examples include `CONCAT22(uStack_1c._2_2_,0x101)`
at0041d8b0 (a partial field on a scalar) and
`CONCAT44(DAT_0060c81c-param_4,param_1)` at0041e480 (an undeclared global).
`summary.json` retains all169 original diagnostic contexts/dependencies.

A narrower safe improvement is supported by the bitvector contract:
`CONCAT31((int3)(integer_expression),low)` copies the low24 bits of its first
argument regardless of signedness. The mechanical lowering is
`CONCAT31(p180_write<undefined3>(integer_expression),low)`. It also applies to
whole `(uint3)`/`(undefined3)` arguments of CONCAT13. Only expressions whose
variables have explicit scalar integer declarations and whose operations stay
integer are accepted. Each accepted span/proof and original variable types are
recorded. The tool excludes partial-field expressions, hidden registers,
unknown symbols, floats and pointers. Casts followed by additional arithmetic
are excluded. There is no global int3 definition or assumed24-bit promotion
model. Expression evaluation remains once; low24-bit packing is exact.

Source contracts: installed Ghidra12.1.3 `opbehavior.cc:753-769` PIECE/SUBPIECE,
`typeop.cc:2050-2057` suffix widths, `printc.cc:862-901` cast printing; their
complete hashes are pinned by frozen180. Additional corroboration is
`CastStrategyC::isSubpieceCast`, `cast.cc:411-432`, zero-offset integer
truncation. `cast.cc` SHA256:
`48cb0d500cf66bb22a73460c62ff923aa19fbc146ec1ef528c797a555709cca8`.
This is a mechanical compile candidate, not accepted original game behavior.

One native x86 batch passes1876 mixed signed/unsigned carrier and24-bit packing
checks. The corpus experiment rewrites69 argument casts across56 functions;
5716 translation units reuse byte-checked180 results. Only56 actual MSVC x86
syntax compilations run, with unchanged options/error limits/header bytes.
Measured delta preparation/compile/report time:22.612 seconds, native batch
separate. All5772 row source hashes are checked again after compilation.

Syntax passes728 ->733, five new and zero lost. Total error diagnostics
61236 ->61173. P-code-category diagnostics180 ->182 (C2672:169 ->171), since
removing invalid24-bit casts exposes additional unresolved argument sites;
there is no claim to have fixed the overall169-site deduction problem.
Compiler-error-limited functions remain63. New passes:
0042a3b0,00452100,004df370,00573ec0,00573f2a.

```powershell
py -3 scripts/research/experiment-v2-pcode-types-183.py --jobs 6
```

Output for object follow-up:
`local/experiments/v2-pcode-types-183/prototypes-cpp-0000/audit.json`.
Per-row `generated_source` selects either a byte-identical180 source or the
changed183 source; `forced_headers` remains empty, `compatibility_header`
retains180 provenance. Header179/global conflicts, partial fields, x87, hidden
state, CONCAT28/SUB104 and ABI remain explicit separate work. Shared game
sources, plans, registry and completed runs are untouched. Root owns integration.

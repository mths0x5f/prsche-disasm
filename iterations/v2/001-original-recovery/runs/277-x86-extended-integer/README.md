# Run277 — bounded extended integer lowering

New backend `scripts/research/x86-cpp-backend-277.py` adds generic MOVSX/MOVZX,
OR, NOT and JG/JLE/JA/JBE/JB/JAE. It mechanically inherits frozen257 lowering
and preserves its Machine257/header/helpers/runtime API byte for byte. Existing
257/262 native suites were not rerun. No original per-body algorithm was written,
native FUN alias supplied, accepted function added or union changed.

Backend SHA256, frozen before native compilation:
`7dd257f43dc304ad183f25dd483a33dd9f76f285b8a7478dd3c9762debbab42b`.
Generated header SHA256:
`8ffb1e675eaaab700612fcac316d30a98f75a21aacaca076830c6f6649aa717a`.
The inherited257 SHA remains
`fd4edaa76a75a07ded0aac11e44e63741ca67a1889bf846fdf3f843ec98d72dc`.
The unchanged helper/header text SHA and exact finite source patches are recorded
in `proof-before-compile.json`; local derived lowering is also pinned.

After coordinator approval, one 2-TU `/MP6` batch passed, exit0, in
1.0451073000440374 seconds, with zero warnings. Twenty-six synthetic native
oracles /164 bytes /70 instructions match actual COFF bytes exactly, with zero
oracle relocations. One fixture passed 30,976 cases in 0.4736104999901727 seconds:

- MOVSX/MOVZX: 16,384 cases, including register8/16→register16/32, AH/AL source
  overlapping EAX destination, partial AX/CX preservation, and byte/word memory
  sources at four unaligned addresses.
- OR/NOT AH/AX/EAX: 13,824 cases, checking full-register preservation, OR's
  defined flags and NOT's unchanged flags.
- Six new conditions: 768 cases, all16 CF/ZF/SF/OF patterns and eight GPR seed
  sets, with distinct taken/fallthrough EAX results.

Value sets include zero, one, max unsigned, max signed, min signed, min signed+1,
max unsigned−1 and two. The fixture compares all eight GPRs, defined CF/ZF/SF/OF,
ESP, returned guest PC/stop, all256 guest-stack bytes and unchanged32-byte source
memory. Only the explicit top native return address is mapped to its guest PC;
no arbitrary pointer normalization occurs. The capture hook restores host ESP
before PUSHFD. MOVSX evaluates its source first and uses unsigned modulo32
`(value^sign)-sign`; partial destinations are stored only afterward.

Unique compile-001/link-001/native-001 receipts preserve actual commands, cwd,
exit and timing before assertions. No native retry/recompile occurred. The native
artifact audit passes31 input pins. An audit-only expectation initially included
write257; the actual new generated object only needs read257, because selected
fragments read memory and write VM registers. That expectation was corrected;
no generated/native/backend artifact changed or reran.

After native validation, the exact frozen252/260 set of85 original PE bodies was
rechecked for syntax coverage. Every body's SHA matches the original Porsche.exe
SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Whole-body syntax support grows **25→29**, with56 rejected and zero baseline
regressions. New supported bodies are005a7673/00536df0 (OR),004ede20 (JA) and
005349e0 (MOVSX). The closed direct-call-chain navigation filter still yields
zero closed chains within this85-body set. This is syntax measurement, not native
execution, ABI/provider/data closure or semantic acceptance of those bodies.
It is not a count of the latest whole-game frontier.

Commands from the repository root:

```powershell
py -3 scripts/research/experiment-v2-x86-extended-integer-277.py --prepare-only
py -3 scripts/research/experiment-v2-x86-extended-integer-277.py
py -3 scripts/research/audit-v2-x86-extended-integer-277.py
py -3 scripts/research/census-v2-x86-extended-integer-277.py
py -3 scripts/research/audit-v2-x86-census-277.py
```

Generation refuses completed summaries/attempts; metadata finalization reuses
successful receipts without compiling/linking/executing again. The two audits
read artifacts only. Separate census validation passes12 pins and redecodes the
four gained whole bodies without altering already-pinned native validation.

Limits: tested source/destination combinations and finite value sets only;
OR/NOT memory forms are not natively covered here. PF/AF/undefined flags, faults,
segments, concurrency and full ISA remain unproved. SETcc, shifts and x87 are
still rejected. No game launch, full memory loader, original native signature
repair or production-function acceptance is claimed.

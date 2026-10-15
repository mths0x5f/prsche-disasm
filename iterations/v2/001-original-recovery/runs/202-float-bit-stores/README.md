# Run202 — repair raw32/float4 representation defects in00485100

The isolated Run200 object compiled numeric conversions where original
Porsche.exe instructions copy32-bit representations. Its native disassembly has
nine `__ftol3` calls for float-to-unsigned stores, plus two unsigned-to-float
conversion sequences (`cvtdq2pd` and `cvtpd2ps`). This object remains unchanged
and excluded from game/union integration.

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first evidence is the257-byte body00485100..00485200, frozen194/196/200
inputs and a single read-only202 Ghidra capture. All97 original instructions
match immutable PE bytes. The capture preserves full HighFunction operations,
Clang tokens and raw instruction pcode; no analysis or signature change occurs.
The wrapper guards the original project's79 manifest files/572766909 bytes.

The nine affected stores map to original raw MOV instructions:
0048511f/125/12b/13f/145/14b/1d7/1dd/1e5. Eight direct stores now read all four
source bytes through a temporary unsigned word before writing the destination.
The last store captures raw bits at the original producer004851e0, before the
intervening FSTP004851e3 can overwrite a potentially aliased source, then writes
those captured bits at004851e5. Every edit retains original instruction,
HighFunction STORE and Clang token witnesses.

Eight `(float)param_1[5/9]` occurrences in six statement lines also performed
numeric conversion. Original FLD/FCOMP and MOV selectors, with corresponding
HighFunction CAST operations, establish representation views instead. These
occurrences now use four-byte copies into a float object. Helpers use character
access, legal for object representations, and separate temporaries for overlap;
source NaN bits do not pass through floating value conversions for raw stores.
All other body lines, branches and arithmetic expressions remain unchanged.

One actual `/MP6` batch compiled one changed game TU and one standalone fixture
TU. The corrected game COFF SHA256 is
`e283a92d5b287cae87255284f4b8e62995f1a35cdbc79f90d40eb2adbfcc1f79`.
It has zero compiler warnings, no `__ftol3` dependency and none of the numeric
integer/float conversion instructions above. The native method symbol,
ECX receiver input, return-this value and RET8 remain unchanged. Its main body
has no CALLs. Local helper sections are emitted but unreferenced from that body.
Physical outgoing ECX is volatile in native code; complete register/caller
equivalence is not claimed.

The actual standalone executable passes1024 representation cases plus a final
count check:16 patterns, four alignments, ±0, infinities, subnormals, signed
quiet/signaling NaN payloads, overlap deltas-3..3, and capture before an aliased
four-byte overwrite representing the later FSTP result. A native MOV reference
checks raw input representations. This fixture verifies copies and alias order;
it does not execute or validate the original complete function's x87 arithmetic.

The initial capture reached and passed compilation, linking, native execution,
disassembly and SHA guards, then report formatting failed on an external
kernel32.Lib path. Its exact driver, artifacts and reached-stage record remain
under `native/captured-driver.py` and `capture-incomplete.json`. Metadata-only
finalization reused those captured bytes with zero compiler/link/native/Ghidra
commands. This distinguishes the successful native checks from the later
metadata error without repeating them.

Commands used:

```powershell
py -3 scripts/research/experiment-v2-float-bits-202.py
py -3 scripts/research/experiment-v2-float-bits-202.py --finalize-existing
py -3 scripts/research/audit-v2-float-bits-202.py
```

The first two commands refuse completed outputs. The audit is read-only and
repeatable. `proof-before-compile.json` retains all18 scoped edit witnesses;
`summary.json` records exact sources, include closure, tools, native objects,
logs and fixture identities; `validation.json` records the independent audit.
New text artifacts use LF before hashing. Frozen200/194/196, accepted registry,
production and union outputs remain unchanged.

Original x87 versus native SSE arithmetic/precision/exceptions, NaN branch
behavior, object ownership/initialization and complete body/caller fidelity
remain open. The result removes known representation errors in one candidate;
it does not establish full physics or gameplay acceptance. Next: coordinator
integration may replace the unsafe200 candidate with this guarded object while
retaining those explicit fidelity boundaries.

# Run167: original floating-point decimal output

Source: Porsche.exe SHA256
ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
Sixteen complete bodies /2665 indexed bytes:
005a3f31,005a3f92,005a4054,005a40a9,005a4150,005a4234,
005abcf9,005abd70,005abdcc,005adaae,005adacf,005adb2d,
005adb5b,005adc4f,005adf5b,005ae17b.

Index-first queries: the scientific/fixed/general roots005a3f31/005a4054/005a4150
in `research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl`
and their complete caller/callee graph in `calls.jsonl`. Exact consumers were
then checked in `research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm`.
This closes the three missing147 output boundaries with original algorithms.
Parse005ac716 and pack005abb07 are separate engines owned by170; its parser
proves scale inputs through±5200.

Confirmed: each public wrapper performs FLD m64/FSTP m64 before conversion.
The decimal engine uses original96-bit arithmetic, partial16-bit products,
normalization, sticky/tie rounding, exponent estimates and base8 selection of
power tables. Exact348-byte tables005e6380/005e64e0 include the4096 factors
at005e64d0/005e6630. Signed zero, infinities, QNAN/SNAN/IND strings, carry,
precision padding, mutable decimal byte and scientific/general selection
retain original behavior. Canonical copy/strlen/move/memset implementations
from accepted packets are compiled as real callees; no host printf conversion.

4991 cases compare recovered and actual original native x86 execution:
exact4096-byte arenas, meaningful returns, cdecl stack/nonvolatile registers,
DF, x87 control/status/tag and all eight80-bit register values. The original
image is privately mapped at30000000; only original PE HIGHLOW cells are
rebased using its relocation directory. Relative calls/branches are unchanged,
no import is replaced and no original game file is modified. The probe is
linked at10000000; fixed buffers provide identical pointer values.
FPU instruction/data pointers identify different implementations and are
excluded from semantic-state comparison; exception/status bits are retained.

Unicorn independently checks the same connected graph and every original
entry is reached. Private compile-time observers compare ordered inputs/outputs
at expand64, multiply96, extended-decimal and decimal-rounding stages; production
has no observer code. NaN FLD/FSTP quieting/payload and hardware x87 exception
differences in Unicorn are saved explicitly, including full divergent memory
and FPU observations. Actual native-original equality is required in every
case. No flags are masked to obtain equality. A second full4991-case build
without observers verifies the production configuration.

Inputs cover public precision0..512, four rounding modes,0/3/7 existing x87
stack entries, pre-existing exception/condition flags, normal/subnormal/extreme/special doubles, signed zero, component
carry/overflow/underflow/ties, text rounding and scale exponents through±5200.
Valid sufficiently large buffers and masked x87 exceptions are required.
Unmasked exceptions, invalid pointers and scale exponents beyond the original
parser's range are outside this proof. Unused canonical dependency functions
have aborting private link guards; none are traversed by the conversion graph.
No game launch or visual acceptance is claimed.

Commands from repository root:

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/167-formatter-float-output -B local/builds/v2/formatter-float-output-167 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-float-output-167 --config Release
py -3 scripts/research/verify-v2-formatter-float-output.py --probe local/builds/v2/formatter-float-output-167/Release/formatter_float_output_probe.exe --report-dir iterations/v2/001-original-recovery/runs/167-formatter-float-output
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/167-formatter-float-output -B local/builds/v2/formatter-float-output-production-167 -A Win32 -DPORSCHE_FLOAT_STAGE_TRACE=OFF
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-float-output-production-167 --config Release
py -3 scripts/research/verify-v2-formatter-float-output.py --probe local/builds/v2/formatter-float-output-production-167/Release/formatter_float_output_probe.exe --report-dir iterations/v2/001-original-recovery/runs/167-formatter-float-output --no-stage-trace --report-name production-verification.json
```

Reports pin original bodies, tables, relocation manifest digest, case results,
compiled sources and quoted transitive headers. Ready for coordinator integration;
no shared registry, common CMake or platform binding change is part of this packet.

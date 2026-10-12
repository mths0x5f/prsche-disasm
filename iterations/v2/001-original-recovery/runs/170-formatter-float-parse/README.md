# Run170 — original decimal parser and binary packer

Ready packet: ten complete original bodies,2254 bytes. Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries:005ac716/005abb07 and transitive calls/references, full original
ASM, original parser jump table005acbb7..005acbe6 and canonical147 wrappers.
Ten candidates:005ac716(1185),005abb07(364),005ab90d(73),005ab956(86),
005ab9ac(140),005aba38(27),005aba53(12),005aba5f(27),005aba7a(141),
005adb88(199). All own bodies are integer-only;167 owns shared96-bit arithmetic
and decimal power scaler. No host strtod or floating arithmetic substitutes.

Confirmed: parser skips only space/tab/LF/CR, supports D/d/E/e and conditional
implicit signed exponents, mutable decimal/ctype/width state, exact end-pointer
rollback,25 stored digits then original byte23 rounding/reduction to24,
explicit exponent saturation5201 and final±5200 checks. Shared167 power-table
extent must cover the legitimate±4096..5200 fifth octal group.

Private MSVC19.44 Win32 Release traced and production builds each pass3800
cases, with identical result fingerprints. Traced proof matches16216
intermediate original-Unicorn events: digit normalization, rounding, shifting
and scaling. Both builds execute the actual original PE at30000000 with only
HIGHLOW loader relocations and the explicit005a2eae classification callback.
The comparison includes8192-byte poisoned arenas, returns, mutable globals,
classification traces, cdecl stack/nonvolatile registers/DF, and native x87
control/status/tag/all eight80-bit values. Original Unicorn also matches
returns/memory/globals/boundaries. No numeric or FPU differences are masked.

Packing retains the original guard/tail rounding, carry, subnormal/overflow
rules,32/64-bit output order, and no writes for other output widths. Canonical
147 Words12/configurations and frozen167 arithmetic are used directly. Exact
348-byte power tables and packing configurations are checked against the PE.

The classification callback tests this caller's typed boundary and state
reloads; canonical151 already owns that implementation. It is not a new
recovery here. Readable ample buffers and canonical packing configurations
are the comparison domain. Invalid pointers and the original nonterminating
count0/all-zero direct normalization inputs are excluded. No live-game or
visual acceptance is claimed.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/170-formatter-float-parse -B local/builds/v2/formatter-float-parse-170 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-float-parse-170 --config Release
py -3 scripts/research/verify-v2-formatter-float-parse.py --probe local/builds/v2/formatter-float-parse-170/bin/Release/formatter_float_parse_probe.exe --report-dir local/reports/formatter-float-parse-170
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/170-formatter-float-parse -B local/builds/v2/formatter-float-parse-170-production -A Win32 -DPORSCHE_FLOAT_PARSE_STAGE_TRACE=OFF
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-float-parse-170-production --config Release
py -3 scripts/research/verify-v2-formatter-float-parse.py --probe local/builds/v2/formatter-float-parse-170-production/bin/Release/formatter_float_parse_probe.exe --report-dir local/reports/formatter-float-parse-170 --report-name production-verification.json --no-stage-trace
```

Root owns integration/registry/shared plans. Production source is compiled
with PORSCHE_FLOAT_PARSE_TRACE absent; only new170 files are packet edits.

# Run147 — float callback helpers and typed dispatch closure

Source: Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Nine complete function bodies: `005a3e33`, `005a3e8d`, `005a3edb`,
`005a3ef3`, `005a41e3`, `005abc9f`, `005abccc`, `005abc73`, `005abc89`.
These are callback/text/sign/dispatch/wrapper bodies. The underlying decimal
parsing, binary packing and formatting engines remain typed dependencies.

Queries: the nine VAs and their callees in `research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl`,
`calls.jsonl`, `references.jsonl`, and complete original disassembly in
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm`.
`005a0f5d` stores the callback literals. Two unpromoted entries have contiguous
original code with internal-only branches/no calls: `005a3e8d..005a3eda`
(78 bytes, terminal RET), `005a3edb..005a3ef2` (24 bytes, RET at3eef/3ef2).
Full SHA/control-flow/file-offset evidence is saved in `manual-entry-evidence.json`;
the coordinator owns shared manual-index updates.

Confirmed behavior:

- `005a3e33` inserts the mutable decimal byte and shifts the suffix in place.
  It calls lowercase on the first signed byte, skips the initial byte when
  scanning digits, and uses either direct mutable ctype-table lookup or the
  original classify boundary according to signed character-width state.
- `005a3e8d` removes zeros after the current decimal byte, retains exponent
  suffixes, and removes the decimal byte when no fractional digit remains.
- `005a3edb` retains original x87 FLD/FCOMP effects. It returns1 when C0 is
  clear, zero otherwise; this includes unordered NaN behavior and preserves
  x87 exception/status/TOP effects instead of substituting a C++ comparison.
- `005a3ef3` uses64-bit parsing for any nonzero flag,32-bit for zero, then
  copies the original ordered output DWORDs. The four parse/pack wrappers
  preserve zero parse flags,12-byte intermediate storage, end-pointer alias
  input, exact24-byte format configurations and packer return values.
- `005a41e3` dispatches e/E toscientific, f tofixed, every other conversion
  togeneral, forwarding original precision/caps arguments. This full dispatch
  body is not a recovered decimal conversion engine.

The native Win32/x86 MSVC probe is compared against original x86 execution.
Text cases compare the entire256-byte arena, callback arguments/order and
mutable width/decimal state. Wrapper cases compare source strings, all parse
flags,12-byte intermediate values, exact packing configuration bytes, final
memory and returns. Dispatch cases compare all forwarded fields and memory.
Sign cases compare return, x87 control/status/tag, TOP and all preserved80-bit
stack values, with all four rounding modes,0/1/3/7 pre-existing stack slots
and masked exceptions. All1196 cases pass:940 text/wrapper/dispatch cases
against Unicorn and256 sign cases against the actual original native code.

Unicorn omits original hardware denormal/NaN exception flags in128 sign cases.
Those discrepancies are recorded separately, with full hardware/oracle output.
The native probe executes the exact24 original bytes in a private executable
buffer, relocating only the constant-zero memory operand at `005a3ee3`.
The verifier checks that operand's original PE HIGHLOW relocation and original
zero bytes, body SHA and instruction bytes; all branch/return bytes are unchanged.
Recovered/native-original return and full FPU observations match in all256 cases.
No status bits are suppressed to make the emulated oracle agree.

Unrecovered boundaries: lowercase005a2248, classify005a2eae, parser005ac716,
packer005abb07, scientific005a3f31, fixed005a4054, general005a4150. Probe
implementations record and produce deterministic synthetic values; no host
printf/strtod approximation enters production. Unmasked FP exceptions and
invalid buffers are outside the comparison domain. No game acceptance claim.

Reproduce:

```powershell
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' -S iterations/v2/001-original-recovery/runs/147-float-helpers -B local/builds/v2/formatter-float-helpers-147 -A Win32
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' --build local/builds/v2/formatter-float-helpers-147 --config Release
py -3 scripts/research/verify-v2-formatter-float-helpers.py --probe local/builds/v2/formatter-float-helpers-147/Release/formatter_float_helpers_probe.exe --report-dir iterations/v2/001-original-recovery/runs/147-float-helpers
```

Next: register the two supplementary entries, integrate accepted helper bodies,
then trace the decimal engines and classification closure before claiming real
float conversion. Existing packets/shared registry/game data are unchanged.

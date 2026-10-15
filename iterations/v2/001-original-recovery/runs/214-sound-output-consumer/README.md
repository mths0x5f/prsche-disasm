# Run214 — restore GetCurrentPosition's output DWORD consumer

One changed game TU0058f5d0 produced a valid x86 COFF in one `/MP6` batch,
exit0, **1.0495606 seconds**, zero errors/warnings. That batch also compiled
one standalone call-boundary fixture TU. Immediate exit/timing sidecars preserve
observed results. No Ghidra, production, accepted registry or union change occurs.

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
The114-byte body has42 indexed instructions, all checked against immutable PE
bytes. Canonical exact/interior-range and WIP-source ownership preflight found0.
The frozen184 source remains unchanged, SHA256
`0c1f5ac5e5aa406a3087dca64b8e873fd99c3b05ebd429fc407f00e55c41c26f`.

The old printed getC body shifted the DirectSound buffer's address after the
call. Original0058f5e3 instead takes the local four-byte stack cell's address;
the call pushes null write-cursor, that output address and self. On success,
0058f5f8 reads `DWORD[ESP]`, followed by logical SHR1. The correction gives this
cell a uint32 view and consumes its actual returned DWORD. It retains the
original single object snapshot for both self and vtable target.

Original0058f166 passes `&006ad768` to IDirectSound::CreateSoundBuffer at slot+c.
SDK IDirectSoundBuffer places GetCurrentPosition after GetCaps, at vtable+10h:
HRESULT32 stdcall(self,DWORD*play,DWORD*write), callee cleanup12. The original
call/setup/flat stack and SDK declarations establish that exact callable type;
no argument or convention is selected from compiler errors. HRESULT!=0 and
null-device guards still return0 without consuming an unwritten output cell.

The integer tail is recovered literally: unsigned cursor SHR1, optional
unsigned DIV by the low eight bits of a DWORD load at006b48dc, modulo32
SUB/conditionalADD based on the result sign bit, modulo32 `*5*5*5*8` (=1000),
then signed CDQ/IDIV by the zeroextended WORD at006b48da. Unsigned intermediate
words plus a character-copy signed bit view avoid C++ signed-overflow UB.
No semantic meaning is assigned to the raw format fields and no zero-divisor
guard is invented. Native disassembly retains DWORD/byte/WORD loads and DIV/IDIV.
Three original RET0 paths share one native RET0 epilogue.

`WORD_006b48da_214` is a private2-byte extern view at original RAM006b48da,
overlapping `DAT_006b48d8+2`. Its address/width are explicit in the header and
proof, not inferred from its C++ name. Shared native storage/alias binding is
deferred; this packet supplies no production allocations or owner coalescing.

The actual corrected body passes36864 controlled-callback comparisons against
the original integer instruction sequence compiled as native inline assembly,
including high-bit cursor/start/wrap/multiplication overflow cases, low-byte
masking and positive16-bit divisors. Three further cases cover two nonzero
HRESULTs and the null-device guard. The controlled stdcall callback verifies
self, nonnull DWORD output and null write output, and its native RET12 is
checked. This fixture validates the call boundary/dataflow and consumer integer
tail; it is not a DirectSound/provider/game implementation or acceptance claim.
Native fixture exit0 took0.0607791 seconds.

The new COFF SHA256 is
`eee27afa6df02115c827289f86ce9fcffe06c2273abe8b84226f037ac46dd0cc`.
Its seven unresolved names are the seven external memory views; no additional
game implementation is substituted. Rows/closures are Run204 ordinary-packet
compatible and disjoint from Run215's1107 objects, giving1108 logical distinct
VAs when combined. This run does not relink that union.

```powershell
py -3 scripts/research/experiment-v2-sound-output-214.py
py -3 scripts/research/finalize-v2-sound-output-214.py
py -3 scripts/research/audit-v2-sound-output-214.py
```

The compile driver requires fresh output; the audit is read-only and repeatable.
`proof-before-compile.json` records exact source edits, PE instructions, SDK,
RAM widths and confirmed/deferred boundaries. `summary.json` retains measured
tool results,37 input/output SHA pins and the fixture identity; `validation.json`
checks the frozen source, scoped edits, COFF, memory widths and private alias.
All new text is LF before SHA. Divisor-zero fault fidelity, provider success
semantics/initialization, object lifetime/concurrency and complete outgoing
register/caller equivalence remain open. The consumer is integer-only; no x87
or full-provider work was added.

# Run229 — one nested callee recovered, one exact proof queue

One fresh i386 C++ COFF defines223's required `?FUN_00590070@@YAIH@Z`.
Selected005907b0 remains uncompiled; no guessed callback or native body is supplied.
Original Porsche SHA `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Frozen180 sources,179 declarations,223 packet,228 union and actual PE are pinned.
Exact/interior registry, recovered WIP and current compiled preflight found0 owners
for both selected VAs. No Ghidra, frozen-run, game, registry, union or production edits.

00590070 is20 instructions/58B, no CALL, one signed32 stack argument and EAX32,
two original RET0 paths. It rejects negative/index>=low16(DWORD006b48d8), reads
tableDWORD at raw006b4a04+index*12, rejects zero, then reads one BYTE at entry+8.
Original NEG AL/SBB EAX,EAX/AND AL,ee yields0 for byte0,FFFFFFEE otherwise;
invalid paths returnFFFFFFF8. Native unsigned address arithmetic retains modulo32
bits; raw-copy intrinsic produces an actual DWORD load and accepts unaligned data.
Actual native count load is DWORD then low16 mask; status load remains BYTE.

One /MP6 batch, one gameTU+one fixtureTU: exit0,1.030157s, zero warnings;
exit/time saved before parsing. One measured native consumer RET0.
Actual corrected body passed368640 comparisons against original58B in0.167125s:
10 signed index patterns,6 counts,3 irrelevant highword patterns, NULL/nonzero
entries, all256 statusbytes and four table alignments. Original reference matches
every opcode/branch byte after masking two verified native global relocations.
No fake provider is needed for this CALL-free algorithm.

005907b0 complete208 instructions/708B and caller/parser witnesses are preserved
in `005907b0-proof-queue.json`. At entry-frameE=S-0x11c,599100 receives raw output
atE+78 and writes DWORD atout+a0 (59911e): minimum contiguous span164B. getC's
short local_a4[4] and surrounding char/array locals alias that output; they cannot
be treated as independent C++ arrays. Original59094d/55 copies first handle[E+48]
into[E+40], the fourth DWORD of callback packet[E+34..E+43]. getC prints only
three packet locals. CALL[EDI] at590965 receives packet address then caller cleans4;
actual provider targets/consumed registers are not yet established. Static index
search found count006b49a2 reset0 and callback consumer slots006b49e0, without a
proven registration writer/target. This does not prove callbacks never execute.

Next bounded step: trace registration/indirect writes to006b49a2/006b49e0 slots;
capture actual target at590965 and inspect its input reads/RET. Then recover the
contiguous parser output and fourDWORD packet before native lowering, retaining
unknown pointee semantics. Do not cast the printed code* merely to compile.

`summary.json` is an ordinary227-compatible packet containing only new00590070.
`proof-before-compile.json` holds original instructions/operations and both ownership
preflights; `validation.json` is the independent read-only SHA/PE/COFF/oracle audit.
Remaining:005907b0, canonical006b48d8/006b4a04 owners/initializers (DWORD006b48d8
overlaps214's WORD006b48da), fault/register/concurrency and whole-game acceptance.

```powershell
py -3 scripts/research/audit-v2-nested-calls-229.py
```

Experiment requires fresh outputs; completed artifacts are not recompiled.

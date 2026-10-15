# Run199 — native union after two CALL-free ABI candidates

Frozen reusable-CLI capture. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Unmodified builder198 takes ordinary192(924), thiscall196(146) and
thiscall197(2) as explicit, disjoint packets: **1072 real native i386 COFF**.
No schema adapter, source repair, compilation, binding, allocation or oracle
rerun is required. Frozen197/198 and shared files remain unchanged.

1070 symbol snapshots are reused after exact source/object/include-closure
checks. The two actual197 object symbol tables are reread:0043f8a0 defines
`?invoke@Thiscall_0043f8a0@@QAEPAHPAHI@Z`,004930f0 defines
`?invoke@Thiscall_004930f0@@QAEPAIPAII@Z`; both have zero undefined symbols.
Their full197 source/header/tool closure is pinned.6540 unique input pins
pass before/after;531 platform-library identities are reused with byte
mutation guards. All selected compiled VAs are disjoint.

Actual fresh archive:1,212,002 bytes,1072 members, SHA256
`16fc8f2d8b7b5a1556ea32f3560530929366f59ddbe766f2535ba33293156554`.
One real lib.exe command takes0.474 seconds; one real diagnostic
`link.exe /DLL /NOENTRY /WHOLEARCHIVE` command takes0.043 seconds.
The complete bounded capture takes7.023 seconds. No DLL or EXE is emitted.
No parser-only finalization or native-tool repeat is needed for this packet.

Relative to198, the complete frontier is unchanged:403 raw unresolved names
with780 referring-object references;393 names after platform-library
extraction and581 LNK2001/2019 occurrences. LNK1120 independently reports393.
No names or references are added/removed. Ten CRT machine names resolve;
no unresolved names arise outside the raw candidate union.

The frontier remains145 function names,241 data names and17 other names.
All145 function VAs are outside the compiled union:36 canonical recovered
owners and109 without compiled/canonical owners. Actual classification finds
zero compiled-VA/symbol-contract mismatches. Adding197's two method bodies
does not close any of those145 exact symbols. The same241 data declarations
retain their original ownership/alias/initialization gaps; no definitions or
guessed bridges are supplied.193/194 evidence is not implicitly integrated.

```powershell
py -3 scripts/research/audit-v2-native-union-198.py --ordinary-summary iterations/v2/001-original-recovery/runs/192-scalar-slice-objects/summary.json --thiscall-summary iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/summary.json --thiscall-summary iterations/v2/001-original-recovery/runs/197-call-free-abi/summary.json --baseline-union-summary iterations/v2/001-original-recovery/runs/198-native-union/summary.json --output local/experiments/v2-native-union-199 --run iterations/v2/001-original-recovery/runs/199-native-abi-union
```

Summary/validation preserve the exact input summaries, source/object hashes,
include closures, tool commands/logs, response, archive and198 delta. New
text is LF before SHA. Generated artifacts stay in the named local experiment;
completed-output guards reject overwriting this snapshot. The next frontier
remains canonical-owner linkage under proved ABI,109 missing function bodies
and241 native data owners/views. This is a dependency diagnostic; original
behavior, game launch and final fidelity acceptance remain separate.

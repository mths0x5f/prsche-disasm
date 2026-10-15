# Run196 — bounded thiscall leaf compiler delta

Frozen isolated compile-candidate packet. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first sources are the binary index, exact179 consumer declarations,
original PE bytes/relocations and disassembly; frozen186/187 supply the
ECX/stack/RET method contract. Production, shared declarations and prior
packets remain unchanged.

The29 actual190 failures group into14 pointer-to-raw32 storage errors,
12 missing globals/printed aliases,2 partial scalar expressions and1 uint3
vocabulary error. Only19 changed TUs are compiled in one actual `/MP6`
code-generation batch:14 explicit address-representation corrections and5
complete, exact consumer-specific179 declaration additions. No full corpus,
full159 rebuild, original execution or repeated native ABI oracle is run.

Each of the14 address corrections changes only
`*param_1 = &PTR_*` to `reinterpret_cast<undefined4>(&PTR_*)` at that store.
The proof records the actual six-byte `C7 /0` MOV instruction, its imm32,
the original HIGHLOW relocation on that immediate, the exact179 table
storage VA, and straight-line register copies proving entryECX reaches
the destination. Compile assertions require pointer and undefined4 widths
of4. This restores address representation; it proves no class layout,
object lifetime or vtable dispatch contract. Existing symbol types remain
unchanged, and no data definitions or guessed pointee types are supplied.

Five declaration-only TUs are0040e5a0,0041b100,004bd3c0,00525c30 and005a0c50.
Their exact179 variants identify these consumers uniquely, although other
consumers can have conflicting types. The string variant is exactly
`char s_C_tv_mn_vu_fdesaB_rp_fe_005e5083[30]`. Each per-TU extern header
asserts exported storage byte size/alignment; no cross-consumer identity
coalescing or allocation occurs.

Result:130 guarded existing COFF objects reused,16 new COFF,146/159 selected
leaf candidates compile,13 failures remain. The19-TU compiler batch takes
4.373 seconds; total measured experiment6.833 seconds. All27 cached
relocation-free original-body byte matches remain; no new literal complete
body-byte match is claimed. These timings describe this bounded delta.
The full146-object subset has21 undefined symbol names/30 references; the
exact symbol frontier is recorded in summary.json and remains unbound.

The13 remaining VAs are00405a90,00443270,0044b800,00456d70,0045e640,
00478ea0,00484500,00485100,00485c50,004873b0,004898a0,00536120 and00540390.
The ten unmodified failures are not recompiled. The three changed
failures retain precise logs:00485100/00485c50 need printed FP aliases;
00536120 also has an int-pointer-to-raw32 store and an untyped exported
pointer target.00485100 additionally retains float-to-undefined4 conversion
warnings from unchanged pseudo-C. Declarations alone would not establish
those stores' semantic fidelity.194 owns the printed-alias evidence pilot;
partial fields and uint3 require a separate exact representation delta.

```powershell
py -3 scripts/research/experiment-v2-thiscall-leaf-delta-196.py
py -3 iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/audit.py
```

New source/header/RSP/log/JSON artifacts use LF before hashing. The summary
pins compiler/code-generator tools, complete include/input closure, sources,
original image, objects and batch log. Inputs and all130 reused objects are
checked before compilation; mutation guards run after the batch. The read-only
audit verifies allowed source changes, exact179 variants, original bytes,
HIGHLOW/store/receiver evidence, unchanged ABI contracts, all146 native i386
COFF objects and the27 cached literal byte matches. Generated artifacts stay
under `local/experiments/v2-thiscall-leaf-delta-196`. Syntax/code generation,
linking and behavioral acceptance remain separate; no executable is claimed.

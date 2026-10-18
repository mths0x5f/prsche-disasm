# Run297 — original frame action

Original `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, `00476170..00476218` (169 bytes), is restored as the existing290 typed method. Registry and accepted body ranges contain no owner at this entry. The implementation walks slots of stride0x38, checks the object pointer at+1c, calls00476710 with the current index, and then uses the possibly changed table at self+0c. It preserves the flag byte at object+4, slot+2c branch, virtual destructor(arg1)/virtual update(+1c), and forward six-DWORD REP-copy semantics including overlap. Table and count fields are reread after the same calls/writes as in the original. No semantic object names beyond the observed fields are claimed.

One game COFF defines only `FrameAction_290::invoke_00476170`;00476710 remains its one external symbol. Its ECX/one-stack-slot/RET4 contract is confirmed from the original callee. Private callback providers and original machine bytes exist only in the native fixture, never the game object.

The fixture compares the C++ method with the exact169 original bytes loaded into private executable test memory. Only the original CALL REL32 operand is changed to a controlled00476710 provider.480 cases cover zero/one/multiple elements, empty slots, flag0/1/255, destruction/update paths, table/object/count changes during callbacks, and identity/forward/backward copy overlap. Full4096-byte arena state, callback order/arguments, RET0, x86 nonvolatiles and DF=0 are compared. EAX is unspecified for the void method. This finite valid-memory comparison does not prove whole-game behavior, fault equivalence or DF=1 behavior.

Attempt001 compiled both TUs but its private fixture needed unresolved memcpy/memcmp without CRT. That failed link and receipt are preserved. Replacing those fixture calls with separately named volatile byte loops required a second MP6 batch; attempt002 compiled, linked and passed480 comparisons. This was a fixture correction, not a change to the recovered game algorithm. Sources/includes, objects, actual commands/logs/receipts and tools are pinned; repository inputs use the common immutable manifest. Audit performs no native rerun or recompilation.

```powershell
py -3 scripts/research/audit-v2-frame-action-297.py
```

Root00628960 initialization,00476710 implementation and real virtual targets remain separate work. No game EXE or visual/runtime acceptance is claimed.

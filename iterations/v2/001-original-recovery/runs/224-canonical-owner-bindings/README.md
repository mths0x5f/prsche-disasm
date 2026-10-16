# 224 — canonical owner binding census

Read-only census of exactly 36 `canonical_recovered_owner_outside_candidate_union` rows from Run216. Original: `Porsche.exe`, SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. Query: frontier VA → current registry owner → actual C++ definition/direct project headers → existing i386 COFF defined symbol; original indexed CALL/RET sites supply exclusions. No compilation, native execution, Ghidra, aliases, new bodies, storage allocation, or union changes.

All 22 owner source files have a selected actual i386 object and recorded source compiler command log. Exact entry definition symbols exist for 35 addresses. Each row in `summary.json` contains the missing FUN symbol/prototype, registry contract/proof boundary, actual definition/header lines, source/object/header hashes, native defined/undefined symbols, and original CALL/RET sites. The 102 input pins passed an end-of-census mutation guard. `validation.json` records the successful guard and actual counts. Cached object identity is established; compilation against the current full historical include closure is **not** inferred.

There are **zero immediately approved bindings and zero original leaf bodies**: every entry contains at least one CALL; all inventoried RETs pop zero argument bytes. Current native decorated definition symbols are cdecl, but original hardware input/return contracts were not newly proved by this inventory. The four matching normalized scalar categories and 31 raw location/arity candidates are navigation results, not C++ type identity or ABI acceptance. `undefined4` and uint/u32 normalize to the same category without claiming signedness or pointee semantics.

Three conditional review targets, requiring parent approval, provider/state closure and a native binding fixture:

- `005a2248`: `int __cdecl formatter_float_lower_005a2248(int)` → `?formatter_float_lower_005a2248@porsche@@YAHH@Z`; actual `local/builds/v2/001-original-recovery/formatter-text-158/formatter_text_probe.dir/Release/formatter_text.obj`. Registry explicitly cdecl; original has six CALL sites. Review this one first.
- `005366e0`: u32 cdecl(u32) → `?timed_callbacks_005366e0@porsche@@YAII@Z`; actual `local/builds/v2/001-original-recovery/formatter-timer-integration-121/startup_timing_integration_probe.dir/Release/window_runtime.obj`. One original CALL site; registry describes an original ECX/stack adapter boundary that must be checked before binding.
- `0053aa60`: u32 cdecl() → `?window_event_dequeue_0053aa60@porsche@@YAIXZ`; actual `local/builds/v2/001-original-recovery/native-window-lifecycle/native_window_lifecycle.dir/Release/window_event_queue.obj`. Three original CALL sites; registry describes an adapted ABI. Queue/global/lock provider closure remains open.

Explicit exclusions from actual owners: `00532e10` and `00534480` are partial. The latter has neither an exact entry definition nor an exact native symbol; its existing window-shutdown object does not establish a complete entry. `005a0fbf` is variadic versus the inferred fixed two slots. `00580080` and `0059f050` have canonical EAX returns versus inferred void; `005925d0` has canonical EAX versus inferred AL. Pointer/scalar, signedness, descriptor and callback differences remain explicit per row. `005a246e` matches normalized scalar categories but is a terminal process-exit provider, not a simple leaf. No exclusion is repaired with an alias or guessed declaration.

Command executed (read-only tooling; no compiler subprocess):

```powershell
py -3 scripts/research/census-v2-canonical-owner-bindings-224.py
```

Machine-readable results: `summary.json`, `validation.json`; local full owner-object inventory: `local/experiments/v2-canonical-owner-bindings-224/object-inventory.json`. The next bounded task can inspect the existing formatter-text object's provider/global closure and original consumers of `005a2248`; this run grants no bridge authorization.

# 237 — uncompiled selector preflight and canonical-owner handoff

No selector algorithm was generated or compiled. Initial recovery preflight stopped on the existing unregistered WIP canonical owner: `source/recovered/Porsche.exe/formatter_stdio.cpp`, lines27/31, declared in `porsche/formatter_stdio.hpp`. Run240 owns the replacement plan: mechanically reuse exact canonical fragments and prove the two raw-to-typed symbol contracts. This packet does not edit the abandoned root237 script, canonical files, registry or union.

Original `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. Both original selectors are35bytes; all70 bytes were independently matched against PE/indexed instructions. Signed index<20 dispatches modulo32 index+28 to CRT lock/unlock; otherwise slot2+32 dispatches to the stdcall critical-section API. Both take two DWORD cdecl slots and return with RET0. The second slot is used as address bits, without descriptor dereference in these selectors.

Known native baseline is **Run233**, not a later inferred union. Its missing symbols are `?FUN_005a3719@@YAXHH@Z` and `?FUN_005a376b@@YAXHH@Z`, referenced by `005a7706`. Canonical native symbols are:

- `?formatter_stdio_lock_index_005a3719@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z`
- `?formatter_stdio_unlock_index_005a376b@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z`

Actual cached object `local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatter_stdio.obj`, SHA256 `837e17652f2975e3a8ec3c2f2de8348c02dc53a7724140db7f5fd50790cadb07`, is uninstrumented: no trace undefined symbols. Each selector occupies its own39-byte COMDAT, with exactly two relocations to its canonical CRT lock API and stdcall lowio critical API. `summary.json` records actual bytes, section flags, relocation targets and complete object symbols.

All18 source/header pins in Run175 verification still match current files; stdio source SHA256 is `3b84985919f64b8c105841b599368f3aa6b9914635de729884244fe9ce02320c`. This preserves the existing4152-case typed-boundary proof; it does not prove a new raw-int/pointer alias. Run240 must check pointer32 representation, exact argument slots, native call cleanup and controlled boundary observations before accepting the bindings.

Whole TU is excluded from the proposed pilot: it defines eight functions plus `formatter_stdio_buffers_006afd60[2]`, requires ten external provider symbols, and overlaps the existing ordinary `005a76a1` implementation under a different native name. The two-fragment plan avoids this extra ownership/provider scope.

Real provider boundary remains open: canonical lock header and definition are both `[26]`; original FILE selectors require IDs28..47 and an independently proved48-entry/192-byte prefix. Run175 explicitly reports `production_ready=false`. The48-entry evidence is a **prefix**, not total table extent. A controlled selector fixture must not be presented as proof that the real canonical lock provider is ready.

Read-only reproduction: `py -3 iterations/v2/001-original-recovery/runs/237-crt-lock-selectors/preflight.py`. Results: `summary.json`, `validation.json`;29 pins passed mutation guard,70 original bytes matched,2 actual COMDATs inspected. Generated C++/compiler/linker/native commands: **0**. Computed aliases, whole-table extent and production integration remain deferred.

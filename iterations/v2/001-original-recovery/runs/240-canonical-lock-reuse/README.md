# 240 — exact canonical lock selectors and two proven bindings

Two native ordinary objects mechanically reuse existing unregistered canonical175 functions `formatter_stdio_lock_index_005a3719` and `formatter_stdio_unlock_index_005a376b`. Two separate directive-only support objects bind the current raw `void cdecl(int,int)` symbols to these typed `void cdecl(int32,Descriptor32*)` definitions. No alternate selector algorithm, whole stdio TU, FILE/buffer global, flush implementation or real lock provider is added.

Original `Porsche.exe` SHA256: `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. Each original body is35bytes/13instructions with two RET0 exits. Signed index<20 selects modulo32 index+28; otherwise raw slot2+32 selects the stdcall critical API, without descriptor dereference. All70 entry bytes, four complete caller bodies and eight indexed CALL sites were independently matched against PE bytes (619 bytes total). Actual PE import descriptors identify Kernel32 EnterCriticalSection at005b2078 and LeaveCriticalSection at005b206c.

`proof-before-compile.json` records canonical byte offsets/hashes for the original include prefix, `using U`/address helper and exact function definitions. The audit reconstructs each generated source from those immutable slices plus namespace wrappers and compares its actual bytes. All18 canonical175 source/header pins still match. Each actual i386 ordinary COFF defines exactly its canonical selector symbol and retains only its typed providers; no full-TU flush/buffer/trace symbol was introduced.

The actual `.drectve` support payloads are exactly:

```text
/alternatename:?FUN_005a3719@@YAXHH@Z=?formatter_stdio_lock_index_005a3719@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z
/alternatename:?FUN_005a376b@@YAXHH@Z=?formatter_stdio_unlock_index_005a376b@porsche@@YAXHPAUFormatterOriginalDescriptor32@1@@Z
```

Support objects contain no external definitions/undefineds, writable/executable payload or relocations. Compiler metadata sections remain permitted. The pointer contract is only opaque32-bit address representation, two DWORD stack slots and RET0; no Descriptor class/layout/lifetime inference or general ABI alias rule is claimed.

One actual compiler batch compiled two canonical fragments, two directives and one fixture. Measured exit **0**, **2.0717989000258967 s**. `/MP6` was requested, but `/showIncludes` emitted **D9030 and disabled parallel compilation**: this was one **serial** batch. Game objects have zero warnings. Fixture retains two **C4731** warnings for the deliberate EBP marker/restoration. The original successful compiler receipt and captured driver were preserved; root finalization used the same objects with `--resume-existing-compile`, **zero recompilations**. Current `/showIncludes` evidence contains28 independently checked header paths, each present in both row closures.

Native fixture exit0 certifies **2268 cases**:2268 typed raw calls,6804 raw-entry calls (alias, canonical, original oracle) and9072 controlled-provider observations. It checks exact alias/canonical address identity, argument dispatch, ESP before/after caller cleanup and EBX/ESI/EDI/EBP preservation across signed-boundary/random indices and wrap/high-bit pointer inputs. The actual fixture COFF contains the nonvolatile marker sequence. Each35-byte assembly test oracle matches the actual original PE body after normalizing **only** CALL REL32 bytes14..17 and absolute IAT-slot bytes30..33; relocation types/targets are checked independently. Actual native link map also assigns each raw/canonical alias pair the same address. Fixture SHA256: `5ab2710116fd739880cddd8afb276fe3b3e8e2b1cc5e253a4c0e43b2ff380b17`.

Independent read-only audit PASS:279 merged input pins, exact mechanical fragments, two ordinary COFFs, two actual directives,70 normalized oracle bytes, eight callers,18 canonical pins and28 headers. `validation.json` and `bindings/validation.json` record the result. The audit ran no compiler, linker, native executable or Ghidra, and did not edit frozen summaries, driver or sources.

Collector inputs are `summary.json` (two ordinary definitions) and `bindings/summary.json` (two directive support objects, zero functions). Ordinary summary SHA256 is `e55111c22a4f6ce2d2b23fb868635c71c7c7a3e1ae4dcbe45ad5fec0f759d27c`.

```powershell
# Historical successful root finalization of already compiled objects:
py -3 scripts/research/experiment-v2-canonical-lock-reuse-240.py --resume-existing-compile
# Read-only acceptance audit:
py -3 scripts/research/audit-v2-canonical-lock-reuse-240.py
```

**Production/provider composition remains incomplete:** canonical lock owner is still a26-entry prefix; FILE selectors require IDs28..47 and a separately proved48-entry prefix. The48-entry evidence does not establish total table extent. Controlled fixture providers do not expand or prove the real lock provider. No production/union change or full game/fault/register/provider fidelity claim is made; the verified selector ABI and the above fixture scope are explicit.

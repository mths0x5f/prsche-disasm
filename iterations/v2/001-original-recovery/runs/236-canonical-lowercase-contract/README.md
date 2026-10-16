# 236 — canonical lowercase binding feasibility

**Decision: no compile or binding in this packet.** The entry ABI matches, but the existing object is instrumented and initial ctype storage/provider composition is not closed. This is a read-only contract manifest, with no alias, storage allocation, canonical source edit, union change, native run or Ghidra export.

Original `Porsche.exe` SHA256: `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`. Query: Run233 missing `?FUN_005a2248@@YAHH@Z` → registered canonical `formatter_text.cpp` → actual cached COFF symbols → indexed entry/callers/state references and actual PE bytes/import descriptors. All 111 entry bytes and all 39 incoming indexed CALL windows match the PE. Entry reads one int32 stack slot, returns EAX, uses RET0 and preserves nonvolatile registers. Current native consumers are `0047d1c0` and `0047d210`; their actual COFFs require the exact missing int cdecl(int) symbol. Canonical target is `?formatter_float_lower_005a2248@porsche@@YAHH@Z`. No function-signature expansion is needed.

Actual cached object `local/builds/v2/001-original-recovery/formatter-text-158/formatter_text_probe.dir/Release/formatter_text.obj` has undefined `?formatter_text_read_trace@@YAXPBXII@Z` and is excluded. Its eight other undefined dependencies are the two CRT lock functions, ctype pointer, character width, locale map/type, and two atomic platform callbacks. Their actual native spellings, recursive project header closure, canonical source usages and registry proof boundaries are retained in `summary.json`.

Shared-state identities requiring one provider composition:

- `006afd80`, `006c02e4`, `006c02e8`: canonical locale uint32, writer uint32, reader int32 definitions in `formatter_text.cpp`; original readable/writable virtual-zero-fill storage. `formatter_locale.cpp`, `formatter_output.cpp` and `formatter_search.cpp` use the same canonical names where applicable. Reader address is passed to the atomic callbacks; writer path uses CRT lock19.
- `005b2258` / `005b2254`: actual PE import descriptors identify Kernel32 `InterlockedIncrement` / `InterlockedDecrement`. Canonical callback cells select the existing stdcall platform wrappers in `platform/formatter_crt_links.cpp`, which call those APIs. Raw preloader IAT bytes are import-name RVAs and must not become literal C++ function-pointer initializers.
- `005e52d0` / `005e54dc`: mutable ctype pointer from `formatter_parser.cpp`, width int32 from `formatter_float_helpers.cpp` (original initial width1). These identities must be shared by lowercase/classifier/parser/float consumers, rather than allocated again under future printed/raw names.

Run233 has **zero defined or undefined native symbol mentions for these seven addresses**. No current raw/canonical storage collision was found, and there is no existing raw-to-canonical binding to reuse. Future raw aliases need actual consumer declaration/storage proof. Selecting canonical definitions as the shared owners still requires an explicit provider/object composition; this packet installs none.

A concrete initial-data gap prevents accepting the whole original input domain: original pointer cell `005e52d0` contains `005e52da`; the valid EOF predecessor WORD at `005e52d8` is `0000`. Canonical `kInitialCtypeTable[512]` exactly matches the 512 nonnegative entries but points at its beginning, with no explicit predecessor storage. Locale-enabled `inner_case(-1)` can read pointer−2, and the classifier also accepts EOF−1. Run158's private probe supplies a 514-byte external arena, so its proof does not establish the production initializer's predecessor layout. No claim is made that incidental linker padding repairs this source-level contract. Fixing this requires a separate authorized canonical data packet, preserving original EOF+table layout and mutable pointer identity.

Whole `formatter_text.cpp` also defines canonical versions of `005a2210`, `005a2e70`, and `005a2870`, already present as ordinary COFF implementations in Run233. Their actual objects/symbols are pinned. These are distinct native names, not asserted duplicate external symbol errors; the same-original-VA ownership/object-selection policy must be reviewed before adding the whole TU.

Next bounded work: prove and restore the canonical initial EOF storage contract; choose one canonical state/provider composition including locale engines, atomics and lock19; review the three whole-TU overlaps. Only then permit an uninstrumented owner build and a native/original fixture that mutates locale/writer/readers/IAT pointers across callbacks. No zero-locale-only shortcut or host lowercase replacement is proposed.

```powershell
py -3 scripts/research/audit-v2-canonical-lowercase-236.py
```

`summary.json` contains the exact contract/evidence windows and 38 input pins; `validation.json` records the passing mutation guard and actual PE/COFF counts. No compiler/linker/native/Ghidra subprocess was executed. Computed aliases, whole-program storage ownership, loader changes and lifetime remain outside this audit.

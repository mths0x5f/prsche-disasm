# Run337 — actual game332 frontier triage

Read-only audit of261 unresolved names/286 references,171 compiled sources and
existing actual COFF objects. No compiler, linker, native fixture or raw corpus
build was executed. `summary.json` records exact decorated names, owners,
original indexed entries/caller windows, proof/source pins and object closure.

Ranked bounded candidates:

1. `formatter_search.cpp`: two transport-only bridges can close
   `compare_005ae3c0` and `render_settings_read_config_005a1e10` (two names/two
   references). All six canonical undefined symbols have current332 providers.
   Run172 production9374 cases and all22 source pins remain current. The compare
   ABI matches exactly; the renderer needs the pointer's full EAX bits as int32,
   not boolean normalization. Original0044eabe/0044eb13 call windows test EAX.
2. `timer_setup.cpp`: `startup_capacity_00565030` is an exact void(uint32)
   cdecl view (one name/reference). Run173 nine timer cases/31 pins are current.
   The already-unresolved diagnostic boundary and asynchronous scheduling limits
   remain; this is a possible alias packet, not full timer acceptance.
3. `context_effects.cpp`: `game_setup_movie_delta_004237d0` matches existing
   void(void*,uint32,uint32) (one name/reference). Run14324 cases/16 pins are
   current. Manager/selector providers remain absent; preserve context HOLD.
4. `formatter_text.cpp`: `startup_drive_character_005a2c24` could close one
   name, but is NOT READY for the full signed filename-byte domain. Run1698178
   cases/20 pins remain current; Run236's initial EOF/predecessor storage gap
   still matters because the startup caller sign-extends filename[0].
5. `formatter_stdio.cpp`: two report views could close two names/three
   references, but are NOT READY. Startup passes original005d6e3c/005d1400 format
   VAs. Binding those integers as native pointers would not relocate literals;
   fixed void versus variadic int views also need explicit transport proof.

Only four canonical Porsche TUs remain outside332: audio init, partial context
destructor, context-core candidate and RTTI. Each retains existing holds; there
is no second whole-TU intake like330. The1144-object Run274 corpus explicitly
contains compile candidates, not native acceptance, and was not imported.

Same-VA names are not sufficient: input negative/unmapped seams would recurse
if redirected to getstate; resource invalid-path is an inner error boundary;
render event005debec is a callback data cell; network text005e8e50 has competing
storage views and unresolved extent. No providers or guessed behavior are added.

```powershell
py -3 scripts/research/audit-v2-frontier-triage-337.py
```

Root authorized the first candidate as isolated Run338 ABI bindings. That packet
must preserve the existing original-function count and canonical172 ownership.

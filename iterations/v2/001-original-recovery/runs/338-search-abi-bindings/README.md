# Run338 — canonical search ABI bindings

Two transport-only bindings reuse Run172's canonical implementations already
compiled in game332. They add zero original functions, data providers or inferred
algorithms. `search_bindings_338.cpp/.hpp` supply exactly:

- `compare_005ae3c0(const char*,const char*)` forwards the identical cdecl int32
  signature to `formatter_search_compare_005ae3c0`.
- `render_settings_read_config_005a1e10(char*,const char*)` forwards both pointer
  arguments to `formatter_search_substring_005a1e10` and preserves all32 pointer
  return bits in the declared int32 result using `memcpy`. It does not normalize
  the return to a boolean.

Index-first entries005ae3c0/005a1e10 and original renderer call sites are recorded
by Run337. At0044eabe/0044eb13 the original pushes two pointer arguments, calls
005a1e10, cleans8 stack bytes and tests EAX. Current renderer consumers likewise
only test zero. The canonical owner returns the full matching pointer, including
shared005a2770 return-tail behavior proved by Run172.

Existing Run172 production proof remains current:9374 original/native cases,
all22 normalized source/header/script pins and original body-byte hashes checked.
Its9374-case fixture was not rerun. Run330 confirms canonical source ownership;
Run337 independently reads actual332 COFF and confirms all six undefined
canonical-TU contracts already have providers. No same-VA body is copied.

```powershell
py -3 scripts/research/verify-v2-search-bindings-338.py --attempt 1 --negative-controls
```

Attempt001 passed on the first batch and is immutable. Reproduction requires
a new attempt ID. `summary.json` pins the receipt in
`local/experiments/v2-search-bindings-338/001/receipt.json`. The receipt records
sources, normal CRT/import libraries, compiler/linker/backends, transitive
compiler dependencies, commands/logs, actual objects and executable hashes.
All inputs are guarded before and after authoritative compile/link/execution.

The production binding TU is compiled with `/O2`; the fixture uses `/Od` for
inspectable inline-assembly ABI capture. Actual optimized COFF has exactly two
public definitions and exactly two undefined canonical search symbols. The
pointer-bit copy is optimized without introducing a memcpy dependency.

816 controlled transport cases verify exact callee identity, one call, both
argument bit patterns, full EAX return, ESP, EBX/ESI/EDI/EBP, and guarded memory
when the canonical stub mutates distinct or aliased argument buffers. Forged
pointer payloads are never dereferenced; cases include null, high-bit and maximum
pointer/return values. Three source mutations are rejected: boolean substring
return, wrong comparison callee and reversed comparison arguments.

The controlled stubs prove ABI transport only. Original algorithms retain172
ownership/proof; locale/EOF domain and full-game holds remain unchanged. Root
owns integration335. Timer/context alias candidates from337 remain separate;
this successful two-binding batch was frozen without scope changes or reruns.

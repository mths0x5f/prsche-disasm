# Run296 — frame root storage remains HOLD

`Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39` has 27 indexed direct DWORD consumers of `00628960`, exactly matched by 27 original HIGHLOW sites and 27 raw DWORD byte patterns. There are no HIGHLOW targets inside the other three bytes. These scans provide navigation and do not establish whole-program absence of computed aliases. The four initial loaded bytes are zero; there are **no physical file bytes** for this address: it belongs to the writable `.data` virtual tail, zero-filled by the PE loader.

Initialization is explicit: `00471b70` allocates `0x3c` through `0059ef90`, calls constructor `004874a0` with the allocation in ECX, and stores returned EAX at `00471bae`. Allocation failure stores zero at `00471bb5`. Cleanup `00471c40` reads the cell, calls `00487590`, frees through `0059f050`, and clears it at `00471c6d`. None of those three function entries has an accepted registry owner. The frozen290 header only declares the typed cell; no canonical storage definition was found in recovered source. Initialization and pointee behavior remain unimplemented.

Standalone storage cannot yet be approved: `00471b72..00471b97` computes the runtime string length at mutable `00657444`, then copies it including NUL with REP MOVSD/MOVSB to `00628940`, only32 bytes before the root cell. There is no bound in this copy. Original-byte Unicorn cutpoints stop before allocation at `00471b99`: source lengths0/31 leave root canaries intact; lengths32/35/40 overwrite root bytes. These controlled inputs demonstrate the address relationship and possible memory effects, not an assertion that the game supplies such strings. Later stores overwrite the root value, but that does not prove that a separate allocation preserves the copy's original memory effects or neighboring identity.

The source buffer is mutable: `00439e25` clears it, `00439e68` passes it as the destination of `005a0fbf`, and `004b29ab` installs its address at registration cell `005d2ac8`. Next trace those writers and that registration consumer for an enforced maximum31-character value. Otherwise recover shared original layout covering the preceding buffer, root, and following buffer at `00628964`. Do not instantiate a dummy frame service or replace constructor behavior with zero initialization.

`evidence.json` records all sites, original instruction bytes, section metadata, and five complete before/after copy windows. `summary.json` uses the common immutable shared input manifest; `validation.json` records successful pin verification. No storage definition, compilation, native fixture, or game execution was added.

```powershell
py -3 scripts/research/trace-v2-frame-root-296.py # producer, once only
py -3 scripts/research/audit-v2-frame-root-296.py
```

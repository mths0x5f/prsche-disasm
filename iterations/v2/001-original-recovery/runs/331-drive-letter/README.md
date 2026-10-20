# Run331 — original drive-letter helper

Recovered `Porsche.exe` `005916a0..0059170e` (111B), SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
`drive_letter_331.cpp` implements the existing byte-return declaration in
Run327's `resource_device_327.hpp`; it adds no platform storage or API substitute.
Root owns game integration332. No shared source, registry or plans are edited here.

Index-first queries: `005916a0`, `005a2780`, `005cd1f4`, `005b221c`,
`GetFullPathNameA`, `005b2290`, `CharUpperA`, `00591760` in the v2 function,
disassembly and decompilation index and old Ghidra reference index.
`evidence.json` pins that historical owner/index snapshot and an independent
111-byte Capstone decode. No accepted registry entry or indexed containing body
owns the candidate; all five pre-existing source mentions are declarations/calls.
The canonical `formatter_search_character_005a2780` owner is reused unchanged.

The original searches for `|` before checking a null argument. A match returns
zero immediately. Otherwise null falls back to the original `"."` bytes at
`005cd1f4` (`2e00`). This is not a general null-input safety guarantee: the
canonical search itself dereferences null. `GetFullPathNameA` receives the path,
capacity261, a stack buffer and a writable pointer cell initially holding the
null search result. `CharUpperA` always runs afterward, including length0/1 and
values with the high bit set. The saved length comparison is signed32. Only when
length>1 and the post-uppercase second byte is `:` does the helper return the
post-uppercase first byte. Its return contract defines AL; upper EAX is ignored.

```powershell
py -3 scripts/research/verify-v2-drive-letter-331.py --attempt 1 --negative-controls
```

Attempt001 passed on the first batch and is immutable. A reproduction must use
a new attempt ID. `summary.json` pins its
`local/experiments/v2-drive-letter-331/001/receipt.json`. No successful fixture
was repeated for metadata. The receipt pins the original PE, all fixture/source
inputs, compiler/linker/backends, explicit normal CRT/import libraries, actual
transitive compiler dependencies, execution commands/logs and outputs. Input
guards run before and after each authoritative compile, link and execution.

The fixture copies the actual PE body into RW memory and changes it to RX only
after relocation. It patches the canonical search, original dot address and two
API IAT references; it does not rewrite instructions or branch behavior. Test
compilation renames the two Win32 imports to controlled pointer slots. A separate
unrenamed production COFF compile confirms exactly one byte-return definition
and three external symbols: canonical search, `__imp__GetFullPathNameA@16`,
`__imp__CharUpperA@4`. These are normal platform imports in production.

6,912 comparisons cover signed length boundaries (0/1/2/260/261/262/INT_MAX/
INT_MIN/UINT_MAX), low/high/NUL bytes, colon changes made by the uppercase API,
six real canonical-search path shapes at four alignments, and both controlled
null-search results. Checks compare AL, ESP, EBX/ESI/EDI/EBP, input memory with
surrounding sentinels, exact API size/argument identities, initial file-part cell,
API order, all261 output bytes transported between APIs, and input mutation
performed by the first API. The second API mutates both inspected output bytes
and returns an unrelated pointer, which the original correctly ignores.

Three mutations are rejected: unsigned length comparison, returning the wrong
post-uppercase byte and skipping uppercase after API length0. The fixture uses
the canonical search TU through a recording wrapper. That TU's unused locale
dependencies have explicit fixture-only zero cells/fail-fast functions; they
are not production providers. Null fallback uses a controlled search return
because real canonical null search faults. Host Windows path and uppercase
implementations are controlled boundaries, not newly accepted game algorithms.

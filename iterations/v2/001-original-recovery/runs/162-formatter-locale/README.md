# Run162 — CRT locale engines and codepage tables

Source Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Nine complete bodies: `005a7e05` mapping (511 indexed bytes), `005a98c2`
classification (318), `005ad2bf` bounded length (43), `005a6895` codepage
setter (429), `005a6a42` resolver (74), `005a6a8c` codepage/LCID lookup (51),
`005a6abf` reset (41), `005a6ae8` table builder (389), `005a6c6d` once-init (28).

Queries: these VAs and callers/callees in functions/calls/references; Kernel32
IAT symbols in static imports; original complete ASM. Run158 inner lowercase
`005a22b7`, uppercase `005a269b` and classifier `005a2eae` call these engines.
`005a6895 -> 005a6ae8 -> 005a7e05/005a98c2` connects the table-building cluster.
`005a6c6d` calls setter(-3). Setter uses CRT lock25 (PUSH19h at005a689e,
unlock005a6a33), proving table cell005e580c is required; coordinator owns its
canonical lock-table declaration. This packet never replaces the lock owner.

Confirmed contracts:

- Mapping probes LCMapStringW then A once. Cached mode1 selects wide conversion,
  mode2 passes to A, all other modes fail. Positive input lengths use the
  original bounded scanner, including its final byte read at the bound.
  Default codepage is captured from006afd90 when the explicit argument is0.
  MultiByteToWideChar query uses flags1/9 according to strict; fill uses1.
  Mapping flags400h select sort-key bytes with signed capacity checks and the
  queried length as result. Other flags allocate wide output then call
  WideCharToMultiByte with flags220h and null fallback/used arguments.
- Classification independently caches GetStringTypeW/A mode. A selects the
  supplied locale or canonical006afd80 when0. W queries conversion, allocates
  and zeroes exactly twice the queried count, fills with flags1, and passes
  the actual converted count to GetStringTypeW.
- Scratch buffers use MSVC stack allocation with the original unsigned
  `(2*count+3)&~3` size. Native SEH catches allocation exceptions at the two
  separate mapping sites; classifier also catches memset exceptions. Original
  filters005a7f15/7fc9/99bb return1; handlers005a7f19/7fcd/99bf clear the
  scratch pointer, restore saved ESP and flow to return0. Scope tables and
  handler gaps omitted from normal function ranges are independently pinned.
- Resolver recognizes -2 OEM, -3 ANSI, -4 current default and resets/sets
  006afd68 exactly. LCID lookup is only the four original932/936/949/950 cases.
  Setter reuses five original 48-byte presets at005e5b98..5e5c87 and mask bytes
  at005e5b90. Other codepages use GetCPInfo; failure preserves existing state
  unless a special resolver requested fallback. Reset leaves case_map untouched.
- Builder substitutes spaces for lead ranges in the byte input table, invokes
  classification/lower/upper engines, then preserves upper-before-lower
  precedence while ORing class bits and writing case mappings. GetCPInfo failure
  uses the exact original ASCII ranges. Once-init sets its flag after setter,
  including setter failure.

All nine Kernel32 services remain exact typed OS import boundaries; no host
locale/ctype approximation is used. New globals own original BSS cells and
the contiguous540-byte codepage state006c02ec..006c0507; canonical006afd80,
CRT locks and memset are reused. Native probe uses controlled OS responses,
compares their complete ordered argument/data effects, full poisoned arena,
codepage state, defined return values and original ABI/SEH chain.

For exceptions, actual native RaiseException inside the protected private
observer/memset call exercises MSVC SEH. The oracle treats OS exception dispatch
as an explicit controlled boundary, executes each original filter and handler
from the original scope table, and verifies return1 plus restored FS chain.
Successful original stack helper005a1e90 executes its real machine bytes.
This proves the recovered consumer contracts; Windows locale services and OS
exception dispatch are not reimplemented or claimed as recovered game bodies.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/162-formatter-locale -B local/builds/v2/formatter-locale-162 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-locale-162 --config Release
py -3 scripts/research/verify-v2-formatter-locale.py
```

Report pins full bodies, extra SEH ranges/scope tables, original preset/probe
bytes, globals/import identities, native PE32/MSVC, fixture inputs and quoted
include closure including the verifier and original preset include file.
The verifier asserts the complete248-byte preset include equals the original,
the initial owned cells/probe bytes are zero, and each controlled exception uses
the original active scope table entry. Native FS:[0] must match before/after each
call, including every caught exception.
The final matrix contains1421 comparisons, including34 caught exception paths.

# Original network RTTI ownership and consumers

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first: follow164 table predecessors and168rtti-evidence into
type_info vtable5c18f8/COL5c98d0 and its exact typed graph. Eight full bodies:
5a1011(41),5a103a(28),5a14b3(26),5a14cd(90),5a1527(249),5a1620(312),
5a1758(35),5a4c20(129 indexed disjoint bytes). Registry overlap checked empty.
5a103a RET4 occupies1053..1055 exactly; no trailing bytes are counted.

All four COLs20, hierarchies16, bases24, count-sized base-pointer arrays, and
type descriptors are typed native objects. Every original pointer field is
PE HIGHLOW-relocated and reproduced with a real native pointer. Exact NUL names
bound descriptor content; native alignment padding is not claimed to be original
object allocation extent. Original strcmp performs aligned DWORD/WORD reads
that can include bytes beyond the terminator, while only bytes through NUL affect
the result. The native structures provide that readable padding naturally.
Graph data uses no opaque fake RTTI byte arrays or null destructor slots.

type_info, CConClient, CConnection and CConHost descriptors each have one canonical
mutable cache+4 initialized null. Original destructor sets the native type_info
vptr, locks27, reloads the cache, conditionally frees it, unlocks27 and leaves the
cache value untouched. The deleting destructor then uses flag bit0 to release
the object and returns its original pointer. Private effects mutate cache during
lock/free to verify exact observation and ordering. Real canonical descriptor
destruction dispatches through the actual native table callback.

Cast helpers preserve complete-object constructor displacement, PMD signed
vbase-pointer tests, decorated-name identity fallback, attribute masks, contained
base scans and virtual ambiguity checks. The entry5a1366 SEH/exception path and
demangled-name cache population remain unresolved; graph recovery does not claim
complete dynamic_cast API recovery or host-compiler RTTI interoperability.
Original lock/free/release consumers are scripted only in the private probe;
production binds their existing canonical recovered symbols.

Private MSVC Win32 proof compares original x86 returns, ESP/nonvolatile ABI,
state/effect order, and all native graph fields after exact identity normalization.
Real network graphs are traversed by the recovered consumers. Synthetic graphs
exercise attributes, repeated types, contained bases, ambiguity, signed virtual
offsets, and strcmp alignments/NUL positions. rtti-evidence.json records exact
original content/hash/relocations and original field-read instructions.

Integration is root-owned:164 network_vtables.hpp must replace old unsized
RTTI byte declarations with typed declarations from rtti.hpp, and its native
owners must use `&network_rtti_...`. Old private probe byte fixtures must become
typed fixtures or link canonical data. This packet does not edit frozen/shared
files. Shared text5e8e50 and identity5b4980 extents remain unresolved.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/174-network-rtti -B local/builds/v2/network-rtti-174 -A Win32
cmake --build local/builds/v2/network-rtti-174 --config Release
py -3 scripts/research/verify-v2-network-rtti.py --report-dir iterations/v2/001-original-recovery/runs/174-network-rtti
```

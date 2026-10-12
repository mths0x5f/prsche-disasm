# Run164 — network send slots and packet queues

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first query follows Run163 slot0 words005b4968/70/78 to complete send
bodies48ad70/48b340 and purecall5a1056, then all connected queue/transport callees.

Owner: network_vtables task; shared plans/index/CMake/registry belong to root.
Private MSVC19.44 Win32 build and572 original Unicorn comparisons passed across
11 complete bodies:48ad70,48b340,5a1056,48a920,48a8d0,48a3d0,55d4a0,55c260,
55c270,560420,586fb0. Canonical529050/50e140/4937f0/4c3150 helpers are extracted
verbatim from their accepted source TUs by extract-helpers.py; no additional
production owners are introduced. No game runtime claim.

Confirmed: one-slot tables have preceding relocated RTTI words. Native table
owners use native function pointers and explicitly unresolved RTTI pointer owners.
Frozen151/155/163 and their raw constructor identities remain untouched; root
integration must replace those assignments and identity comparisons together.
The native probe installs actual owner.send addresses as sender vptrs and
dereferences their slot0. Original execution dereferences the original table
word. vtable-evidence.json pins all6 original pointer words/HIGHLOW relocations,
constructor/destructor assignments, slot0 consumers and the3 omitted complete
function ranges/SHA. Purecall executes fatal25, a proven noreturn boundary;
no fabricated returning ABI is supplied.

No additional RTTI structure or data extent is claimed. Unsized RTTI externs
have private one-byte link fixtures in the probe only. Production linkage stays
open until original RTTI storage/consumers are recovered.005e8e50 is untouched.

Comparisons include full64KiB fixture backing, exact initialized packet data,
queue ordering, callback-dependent manager/lock/index reloads, modulo32 counts,
overlapping insertion sources and output/iterator aliases. Full244-byte queue
records contain an indeterminate original stack tail after size initialized
payload bytes. Both executors exclude precisely those trailing bytes for short
packets; no byte-parity claim covers stack residue. Size240 exercises the entire
copied record. Original stack/nonvolatile-register preservation and RET bytes
are checked on returning paths. Cases also cover24-bit length/high-byte flags,
disabled member/global transports, direct/routed dispatch and fatal25.

Remaining external effects: existing lock/refill/copy boundaries and lower
transport587000/5870b0. Native table integration must update all assignments
and identity comparisons consistently. Next: root adds omitted target index
records from vtable-evidence.json, traces RTTI consumers and lower transports,
then integrates one canonical native-table owner without guessed RTTI extent.

```
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/164-network-vtables -B local/builds/v2/network-vtables-164 -A Win32
cmake --build local/builds/v2/network-vtables-164 --config Release -- /m
py -3 scripts/research/verify-v2-network-vtables.py --report-dir iterations/v2/001-original-recovery/runs/164-network-vtables
```

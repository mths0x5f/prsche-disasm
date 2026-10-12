# Network constructors and startup

Source: Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first query: remaining original vptr assignments48aa21/48aa84 and48af92/b015,
their complete parent constructors48aa10/48af80, startup48b3c0/48b450, address
queries55d5a0/55d5e0/55d6e0 and protocol/provider callees55d730/55d750/580590/5805b0/5805e0.
All12 function ranges exist in the original Ghidra index. Exact original body
hashes, source closure and comparison count are recorded in verification.json.

Both constructors store real canonical164 native table owners through
`&network_vtable_owner_*.send`, including the intermediate purecall stage.
Client packet92 and host settings52 are fully zero initialized before copies;
original string copies remain unbounded. Their input lengths must fit original
fields (client20..71 and72..91); no truncation or invented failure path is added.
Pool manager is captured before enter/refill/leave, while its lock handle is
reloaded for leave. Host worker creation retries once with zero port after
failure; both-failure query0 is covered. Query1 with both failures still reaches
null consumers in the original and is not represented as graceful handling.
Startup allocation20 failure still invokes connect(null); the private scripted
boundary observes this exact ordering without claiming actual connect handling.
Allocation8 failure stores null, and restart clears byte15 on every active path.

Worker pointers are reloaded between address-current/get/parse/equality calls.
Address-get writes directly into the first DWORD of the descriptor initialized
by address-current; this original stack alias is preserved before equality.
The original default host is exactly `porsche-entry.earacing.com`.
Address protocol mode uses unsigned `>3`; text mode uses `==1`. Text parse copies
19 bytes then terminates byte19; fallback equality compares exactly five DWORDs.
Provider parse/get callbacks are optional; compare is required and called without
a null guard. Canonical port5b4990 has a proven DWORD read/value0x24e2. Identity
5b4980 and shared text5e8e50 remain unsized external dependencies.

Private proof compiles only the new source and probe with MSVC Win32. Native
link fixtures contain actual native function pointers and normalize only vptr
identity words to original VAs. Oracle runs all12 complete original x86 bodies,
checks ESP callee cleanup/nonvolatile registers, entire object/list/pool backing,
fully initialized packet bytes, exact boundary order/arguments and return values
(void startup EAX excluded). Mutation scripts swap the manager, captured lock,
worker pointer at successive calls, and child pointer during allocation8.
Actual worker construction55c370/55aaa0, current-address55d650, connect48ac90,
allocator/lock/CRT functions and provider callbacks remain scripted effects.
No native RTTI owner or guessed extent is emitted. Unsupported query modes with
uninitialized original locals are excluded rather than normalized to zero.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/171-network-constructors -B local/builds/v2/network-constructors-171 -A Win32
cmake --build local/builds/v2/network-constructors-171 --config Release
py -3 scripts/research/verify-v2-network-constructors.py --report-dir iterations/v2/001-original-recovery/runs/171-network-constructors
```

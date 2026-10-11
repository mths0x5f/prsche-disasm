# Run141 - application shutdown and reset services

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query: 004b68f0,004a6960,004a6e30,0048dad0,0048e6f0 in the
SHA-qualified functions/calls/references indexes, followed by full original ASM.
The actual Run136 game-link report lists the corresponding app_main symbols.

Four complete bodies are recovered: audio shutdown004a6960, reset004a6e30,
network finish0048dad0 and member close0048e6f0. Shutdown preserves wrapped
32-bit SHL and signed division by100. Its00656510/18 accesses alias the last
existing Run128 audio record. Reset writes only original fields and leaves
opaque gaps unchanged. New00655d48..00655fff storage is proven PE zero-fill;
005d1738 has source initial DWORD1. The count/table at005e8bfc/005e8c00 stays
an unresolved contiguous unsized storage view: no production allocation or
table extent is guessed. Selected=-1 reads the count immediately before the
table, as the original does. Other invalid addresses retain original fault
behavior; this packet does not establish the producer's valid index domain.

Network finish preserves captured lock cells, mutable lock-handle reloads,
global pointer reloads and message ordering. Close requires a thiscall ECX
receiver: the exact native body uses fastcall(receiver,unused_edx), while the
existing zero-argument app_main facade passes the canonical network pointer.
Original004b6f60..004b6faa loads that pointer into ECX without an intervening
call. Other known callers00509170/0050a4b0 must use the explicit receiver entry.
All four callers ignore EAX; no defined return-value contract is invented.

Private MSVC Win32 probe and Unicorn run the complete original bodies,
comparing full application arena/reset span/records and both network objects,
active/buffer/pointer/lock cells and ordered effect traces. Cases cover all
gates, signed modes/counts, selected=-1, arithmetic wrap/sign, and callbacks
that replace global objects, alter lock handles and mutate audio buffers.
Original nonvolatile registers and stack are checked. Audio/device/network
effects remain typed unresolved boundaries; fixture definitions are private.
004b68f0 is only traced: object copies and its shutdown callees remain open.
No common-build/registry integration, live device/network or game acceptance
is claimed by this isolated packet.

Reproduce from repository root:

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/141-application-services-next -B local/builds/v2/application-services-next-141 -A Win32
cmake --build local/builds/v2/application-services-next-141 --config Release
py -3 scripts/research/verify-v2-application-services-next.py --report-dir iterations/v2/001-original-recovery/runs/141-application-services-next
```

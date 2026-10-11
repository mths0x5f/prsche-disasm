# Run148 - network message and list services

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first query maps app_main poll/wait/action to0048dcb0/0048e1a0/0048da60,
then inspects0048c870/0048e790 and list helpers/callers/callees/full ASM.
Poll1250bytes and wait1357bytes remain explicitly unrecovered.

Five full bodies:0048c870 packet serialization/virtual send;0048da60 locked
network action with its existing app_main facade;0048b660 unlink/recycle;
00493180 remove all matching values;0048e790 five-list cleanup. Existing
canonical network and005e4fe8 manager providers are reused; no new globals.
This closes direct Run141/145 message/cleanup boundaries and a real app_main
network action symbol. Unknown transport/OS effects remain typed externals.

The serializer writes a low-byte opcode, optional24/32-bit big-endian integers
and a nullable bounded string into a200-byte stack packet. Only0x80000000
omits integer fields. Null string omits the terminator; nonnull empty string
appends one. Broadcast sends reread sender/list state after callbacks and
follow the current node's next link after sending; every send uses the same
packet storage. No uninitialized stack tail is sent or compared.

Unlink detaches before locking, recycles through captured pool state and writes
its output iterator last, preserving aliases. Remove-matching rereads the
pointed-to match value after callbacks. Cleanup groups each list by the last
node's value, removes all matching nodes and then releases the group object.
List0 frees null groups too; later lists skip null destruction. Final exact
flag/word stores are preserved.0048c430/004904d0 and iterator004c3150 remain
typed boundaries; cleanup calls the real recovered unlink/remove-matching.

Private MSVC Win32 probe reserves a fixed fixture arena with VirtualAlloc;
this is test infrastructure only. Unicorn executes complete frozen bodies.
Comparisons cover packet bytes/length/destination/virtual receiver/order,
full fixture backing, aliased output/EAX, ESP/nonvolatile registers and
RET20/8/4. Cases include field omission, long strings/truncation, empty and
multi-target broadcasts, mutable senders/packet/next links, network pointer
reloads, duplicate/null groups, pool replacement and mutable match values.
No live send, full startup, or network acceptance is claimed.005e8bfc table
extent/owner and005e8e50 alias backlog remain unchanged.

Reproduce from repository root:

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/148-network-services -B local/builds/v2/network-services-148 -A Win32
cmake --build local/builds/v2/network-services-148 --config Release
py -3 scripts/research/verify-v2-network-services.py --report-dir iterations/v2/001-original-recovery/runs/148-network-services
```

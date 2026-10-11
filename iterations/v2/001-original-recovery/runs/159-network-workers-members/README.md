# Run159 - network worker and member services

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first queries follow Run151/155 unresolved worker/member entries,
all callers/callees, complete ASM and original data references.

Fifteen full bodies: workers `0055bfd0/0055d1b0/0055d9b0`; queue wrappers
`00580050/00580080/00580020`; queue disposal/count `005806c0/005809f0`
and extra-list disposal `0055c060`; member removal `00492770`, connection
removal `0048b5a0`, member destruction `0048a7a0`, iterator helpers
`00529050/0050e140` and insertion `004937f0`.

The workers differ in the placement of active-bit clears and in callback
pumping. Waits retain original unbounded loops and exact sleep/pump order.
Disposal checks the ownership bit and clears the lock after effects. Extra
queues use the original nonascending disposal order. Canonical IoList,
event/sleep/current-thread/timer/thread-wait/pool providers are reused.

Member removal preserves all pending/suppressed/group branches, wrapping
counters, callback removal, packet arguments, list insertion and destructor
order. The unknown group effect remains typed and its flag is reread.
Iterator end is RET4 despite two apparent pushes: the extra word is an
argument for a later call. Insert uses RET12 and reads its value after lock
leave; outputs can alias source/node/list storage. No synthetic caps, guards
or fake vtable effects are introduced.

New zero-filled storage owners are the typed worker span `006a3b60..3d2f`,
canonical 28-byte ThreadRecord at `006a3d30`, and DWORD `006a4660`. The generic
initializer `0057ffc0` establishes the two 28-byte lists at +198/+1b4 and
event at +194; prefix bytes remain opaque. All indexed span references are
recorded. Message backing at `006a3d50` is not guessed or owned.

The MSVC Win32 private probe links actual frozen callback/list/serializer/IO
sources. Unicorn runs complete original bodies and their recovered callees.
Comparisons include boundary order/arguments/intermediate state, exact sent
packet prefix, all fixture backing, callbacks, return/output aliases and
original ESP/nonvolatile registers/RET4/12. Private effects cover delayed
message arrival, mutable flags/locks/managers, group transitions and pool
growth. Relocated static fixture pointers are normalized explicitly.
Uncalled linkage dependencies abort if reached. No live worker/network or
startup acceptance is claimed.

`0048bda0`, its `005e8e50` consumer, vtable canonical relocations, poll/wait
and `005e8bfc` ownership remain explicit follow-up work.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/159-network-workers-members -B local/builds/v2/network-workers-members-159 -A Win32
cmake --build local/builds/v2/network-workers-members-159 --config Release
py -3 scripts/research/verify-v2-network-workers-members.py --report-dir iterations/v2/001-original-recovery/runs/159-network-workers-members
```

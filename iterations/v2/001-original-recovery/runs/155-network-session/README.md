# Run155 - network session teardown

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first query follows Run145 session boundaries `00492260/00491fc0`,
their callers/callees, and complete ASM. Five full bodies are recovered:
`00492260` stop, `00491fc0` destroy, shared `0048b310` connection stop,
`00493130` list clear, and `0048b250` connection-wrapper destruction.

Separate stop clears member-active before the worker call; destruction
clears it after the worker. Teardown preserves the captured first lock cell,
the later global lock-cell reload, callback removal, member-removal loops,
grouped indirect-object detachment, sequential buffer releases, nested
connection destruction, and the exact six-list final disposal order.
The wrapper reloads its nested connection after releasing the buffer.
No list caps, null guards or synthetic state resets are introduced.

Canonical session/callback owners from Run145 and manager providers are
reused. Two proven data owners are added: zero-filled pointer `00628c78`
and one-byte `.data` value `005d07d0=1`. All indexed references are included;
constructor stores at `00491de0/00491df1` establish allocation/clear use.
The original mapped image values are asserted in every oracle case.

The private MSVC Win32 probe links frozen production Run139/145/148/151
sources. Original Unicorn also runs real recovered unlink, detach, nested
connection destruction, callback removal and pooled-release callees.
Comparisons cover arguments/order/intermediate state, full fixture backing,
eight callback slots and original ESP/nonvolatile registers. Empty, null,
duplicate and mixed lists, active flags, nested objects, replacement locks,
mutable pool managers/handles, sequential buffer reloads and worker field
changes are exercised. Uncalled linker dependencies abort if reached.

`00492770` and worker bodies remain typed effects. Its private test script
removes one matching node from each requested list to drive caller loops;
this is explicit fixture behavior, not a claim about the original callee.
The existing literal vtable identities `005b4968/70` and new `005b4978`
retain a canonical-relocation backlog; consumers are not guessed. Poll/wait
and `005e8bfc/005e8e50` storage/alias questions remain open. No startup/live
network or virtual dispatch acceptance is claimed.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/155-network-session -B local/builds/v2/network-session-155 -A Win32
cmake --build local/builds/v2/network-session-155 --config Release
py -3 scripts/research/verify-v2-network-session.py --report-dir iterations/v2/001-original-recovery/runs/155-network-session
```

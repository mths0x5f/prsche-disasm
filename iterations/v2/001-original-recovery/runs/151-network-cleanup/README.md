# Run151 - network cleanup

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first query follows unresolved Run148 `0048c430/004904d0/004c3150`
and Run145 `0048c580/0048aed0`, their callers/callees and complete ASM.
All five bodies are recovered. The native probe also compiles the frozen
Run148 source so object destruction calls the real recovered `0048b660`.

`0048c430` clears matching indirect object slots while holding a captured
lock cell; it reloads the global list after entering the lock. `004c3150`
returns the supplied iterator pointer with thiscall RET4, including aliases.
`004904d0` removes all duplicate nodes for each last-node payload, frees each
nonnull payload and its buffer, preserves the residual-node loop, and
recycles the sentinel. No list length, object type or maximum count is guessed.

`0048c580` stops its worker, recycles list nodes/sentinel and releases the
wrapper, then clears the global list before destroying/releasing the current
lock cell. `0048aed0` preserves both original vtable stores and recycles into
pool offset `+0x88`, distinct from the other bodies' `+0x10` chain. Worker
effects remain explicitly typed boundaries, along with existing lock/free
effects. No production substitutions are supplied.

Two canonical pointer owners are introduced at `00628c60/64`. Original
mapped image values are asserted zero. All indexed references are recorded
in the report: constructor `0048c4d0` allocates separate four-byte wrapper
and lock cells and writes these globals; `0048c580` clears both. Existing
network/session/member/manager owners are reused without duplication.

Private MSVC Win32 fixture allocation is test infrastructure. Original
Unicorn executes full bodies and the real unlink callee. Cases compare
boundary order/arguments/intermediate state, full fixture backing, iterator
return/output aliases, original ESP/nonvolatile registers and RET4. Cases
cover empty/duplicate/null lists, worker changes, global list/lock changes,
captured pool versus replacement manager, mutable handles/buffers and the
two vtable stores. No live network or startup acceptance is claimed.

Session lifecycle `00492260/00491fc0`, poll/wait, and the unchanged
`005e8bfc/005e8e50` storage/alias backlog remain open.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/151-network-cleanup -B local/builds/v2/network-cleanup-151 -A Win32
cmake --build local/builds/v2/network-cleanup-151 --config Release
py -3 scripts/research/verify-v2-network-cleanup.py --report-dir iterations/v2/001-original-recovery/runs/151-network-cleanup
```

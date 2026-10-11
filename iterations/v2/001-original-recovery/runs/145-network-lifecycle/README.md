# Run145 - network reset and member lifecycle

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first tracing covers all references to005e8bfc/005e8c00/005e8e50,
writers0040f160/00411130, and callers/callees/full ASM of0048e9c0,
004935c0 and00560180. `storage-trace.json` preserves every index hit with ASM.

The005e8c00 table contains player/car-object pointers.00411165 clears count;
0040f25d stores at table[count] and0040f265 increments count, without a local
capacity check. The adjacent table005e8c24 does not prove an allocation bound.
No production extent/owner is invented.005e8e50 remains an explicit alias
backlog: current file-null byte,32-byte heap-label storage and renderer fallback
constant are separate implementations of shared original addresses. Their
initial/runtime-byte meaning and canonical owner remain open and unchanged.

Three complete bodies are recovered.0048e9c0 resets network state and calls the
real004935c0 member destructor and00560180 callback remover.004935c0 follows
both circular lists, resets their sentinels and recycles every node/sentinel to
the original manager+28 free-list heads+10/+14. The canonical005e4fe8 manager
provider is reused and reloaded per node; captured pool pointers and mutable
head/lock reads retain original timing.00560180 scans exactly eight slots and
clears only the first match. New00628c74/7c and006b7c20..3f owners are source
PE zero-fill. Their runtime initialization and external services stay open.

Both member bodies receive ECX and use RET0. The explicit reset entry preserves
final EAX=GetTickCount()<<5 (with32-bit wrap), while the Run141 void facade
discards it. Wait uses signed timer division toward zero. The source's invalid
null-global dereference on the B1 path is retained, without a guessed guard.

Private MSVC Win32 and Unicorn compare complete object/list/manager backing,
callback slots and pointers, ordered effect arguments and boundary-state
observations, ESP/nonvolatile registers and reset EAX. Cases cover all gates,
different global/receiver pointers, signed timers, tick wrap, empty/nonempty
lists, duplicate callbacks and callbacks mutating buffers, flags, managers,
captured pool heads/locks and session pointers. Unrecovered effects, including
0048e790 list cleanup, remain typed boundaries with private fixture controls.
No live networking or complete game startup is claimed.

Reproduce from repository root:

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/145-network-lifecycle -B local/builds/v2/network-lifecycle-145 -A Win32
cmake --build local/builds/v2/network-lifecycle-145 --config Release
py -3 scripts/research/verify-v2-network-lifecycle.py --report-dir iterations/v2/001-original-recovery/runs/145-network-lifecycle
```

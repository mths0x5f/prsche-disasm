# Run139: context pool effects

Source: Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries: `005262e0`, `004237d0`, `00441200`, `00529c20`,
`004211d0`, `0059ecb0`; then direct callees `00424000`, `0059ecd0`,
`0059eeb0`, `00529c50`. Function/call records precede complete ASM-body
inspection. The seven full bodies are `004211d0`, `004237d0`, `00441200`,
`00424000`, `005262e0`, `0059ecb0`, and `0059ecd0`.
Original inclusive ranges and body SHA pins are in verification.json.

`004237d0(block,bytes,mode)` is a pooled release, despite its inherited
`application_context_clear` identifier. It selects manager minus 140*mode
plus 0x28. The third argument is a pool mode, never a fill value. Existing
135 call arguments need no correction. `00441200(block,bytes)` selects
mode zero. Both use an unsigned size comparison against 256. Only
`00424000` has an explicit zero-byte return. These bodies have no
source-level result contract: incidental EAX is not promoted to a return.
Allocation wrappers and `004211d0` do return the allocated pointer.

`004211d0` captures the manager-derived pool before entering a lock.
It reloads the list head after refill, ignores the refill return, and
reloads the lock slot before leave. Large allocation loads the selector
from `[005e4fec]-mode*4`; the existing value accessor cannot express that
operation, so `context_selector_pointer_005e4fec` is a typed unresolved
storage accessor. The callback receives `(source,bytes,heap)` via the
current manager's +4 field. Release uses its +8 callback.

`005262e0` first recurses into node+0xc, then captures sibling+8 and range
start+0x10. It releases non-null ranges using end+0x18 minus start,
reloads the manager after release, and links the node into pool+0x18.
Sibling capture precedes range-release callbacks. Root ECX is preserved
through recursion but otherwise unused by the original body.

The private MSVC Win32 probe compares 24 cases against original x86:
null allocation/release, mode 0/1/2, sizes 1/8/32/256/257/0xffffffff,
refill ignoring its return, lock-slot/head/global-manager mutation,
zero-byte guarded release, empty recursive trees, nested child/sibling
trees, empty ranges, and callbacks changing manager/sibling fields.
Every case compares all 8192 poisoned arena bytes, the manager cell,
ordered effects, pointer returns, original stack cleanup and nonvolatile
registers. Only four initial callback-address cells are normalized to
their source identities after native execution. No arena byte is omitted.

Unresolved services remain typed: `0059eeb0` pool refill, canonical
`005322b0/005322c0` lock functions, current manager indirect callbacks,
and the storage accessors. No substitute is supplied by the recovered
source. Test doubles exist only in the probe. `00529c20/00529c50` remain
the next range-service cluster; their source pins are navigation evidence
and are excluded from the seven-function acceptance count. No partial
body enters this packet. Real game execution and visual acceptance remain
open and coordinator-owned.

Commands:

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/139-context-effects -B local/builds/v2/context-effects-139 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/context-effects-139 --config Release
py -3 scripts/research/verify-v2-context-effects.py --probe local/builds/v2/context-effects-139/bin/Release/context_effects_probe.exe --report-dir iterations/v2/001-original-recovery/runs/139-context-effects
```

Result: seven full functions; native MSVC Win32 Release build; all 24
cases match original x86. Verification records complete source closure,
the verifier, compiler identity, PE architecture, body/global SHA pins,
probe SHA, fixture hashes, and original ABI checks.

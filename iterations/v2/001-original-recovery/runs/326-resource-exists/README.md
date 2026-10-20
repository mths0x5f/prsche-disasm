# Run326 — resource exists wrapper and request sequence

Recovered original bodies: `00561b80..00561b93` (20 bytes) and
`00533f00..00533f33` (52 bytes), Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Exact body SHA values are recorded in `summary.json`. This is bounded recovery
of the two algorithms, not proof of physical filesystem behavior.

The wrapper reads canonical `resource_leaf_group_005df770` on each invocation
and forwards path/group to the request sequence. The request sequence calls
`00568260(path,group,nullptr)`, returns zero for request ID zero, otherwise calls
canonical wait00567f70 and completion00567df0 with the retained ID. The completion
DWORD is returned raw, including high-bit and negative integer representations;
wait status is ignored. Constructor00568260 remains an explicit typed boundary
returning its raw EAX. Its third argument is the request context forwarded to
accepted operation_allocate005682a0. It is not a new callback implementation.

Ownership checks preceded source creation: the registry and the indexed body
ranges/interior entries of accepted Porsche.exe owners do not overlap either
candidate. Recovered-source and run-source searches found callers/declarations
but no competing body. Wait00567f70 and completion00567df0 retain their existing
owners and declarations from files.hpp. The canonical group storage is linked
from resource_dispatch_globals.cpp, preserving the original initialized `0x64`.
There is no production provider, duplicate accepted body, or new writable data.
Accepted integration sources are only `resource_exists_326.cpp` and its header;
the native fixture remains local and is excluded from the game graph.

Original-index queries:00561b80/00533f00/00568260 and their callers/callees in
`research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/{functions,calls}.jsonl`.
The wrapper's `00561b80` DWORD load, two pushes and call/cleanup/RET establish
the ABI; `00533f0f/00533f1e/00533f24` establish constructor/wait/completion order.
The eight-byte cleanup after both wait/completion calls and ESI reuse prove the
retained request ID and ignored wait result. Existing callers consume EAX.

REA325 was independently reviewed after native execution: one fresh persistent
Ghidra session, immutable original SHA before/after, exact20/52/51-byte wrapper,
request and constructor bodies. `rea-cross-review.json` pins receipt/status and
three analysis outputs, with instruction lists and evidence IDs. Ghidra emits
`void` pseudocode for00561b80 and00568260; the actual instructions preserve EAX,
and00533f00 explicitly consumes constructor EAX. The implementation follows
those instructions and native return tests. The caller inventory for00561b80 is
partial and is not used as proof that no other caller exists.

Native attempt001 compiled all three TUs once with normal static CRT and MSVC
x86 `/Od /Oy-`; no failed attempts. Private original20/52-byte copies are linked
together in a RW slab, with checked relocation operands and calls redirected
only at the explicit constructor/wait/completion boundaries, then changed to RX.
The wrapper's global operand targets the actual canonical group storage.

**PASS:9,216 cases /175,117 checks.** Both direct request and complete wrapper
chain are compared. Each case calls twice to check that mutable group/path and
request-ID effects are observed in the right places. Inputs cover null/empty/
nested/non-ASCII path, zero/high-bit group, zero/high-bit request ID, six raw
completion values, successful/failed wait, and callback mutations. Checks include
exact ordered arguments/null context, zero-ID skipping wait/completion, raw EAX,
ESP and EBX/ESI/EDI/EBP preservation, full post-state and path-buffer guards.
Constructor/wait/completion are controlled fixture callbacks; actual canonical
wait/completion implementations are not reimplemented or newly counted here.

The immutable native receipt pins PE/body bytes, verifier, quoted dependencies,
compiler-discovered transitive headers, toolchain/compiler DLLs, explicit CRT/SDK
libraries, logs, actual COFF, all objects and executable. Inputs are guarded
against drift across compile/link/execute. Registry/index hashes capture the
pre-integration ownership baseline; the registry will naturally change when
the coordinator registers these two new owners. `summary.json` pins that native
receipt and source/header hashes, with a separate REA cross-review pin.

Fresh native reproduction (choose an unused attempt number):

```powershell
py -3 scripts/research/verify-v2-resource-exists-326.py --attempt 002
```

The final summary was assembled from immutable native001 after REA325 review;
the successful fixture was not rerun for metadata. Local receipts are under
`local/experiments/v2-resource-exists-326/attempt-001`. Source/data/PE were not
mutated during execution. Full constructor/device routing, queue/OS state,
physical file existence and game execution remain open. Coordinator owns
game-graph integration and root/iteration-plan updates.

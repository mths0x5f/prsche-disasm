# Run327 — resource device routing and open-callback evidence

Original `Porsche.exe` SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Two original bodies are recovered: `00568e90..00568eb2` (35B) and
`00591760..0059177a` (27B). Their original chain and three C++ ABI views pass
10,240 native comparisons. The distinct 276B callback `00561ce0` is evidence
only and is excluded from the recovered-body count. Root owns game integration328.

## Source, owners and exact contracts

Index-first queries: `00561ca0`, `00561ce0`, `00568e90`, `00591760`, `005916a0`,
`00568d50`, `00561be0` and `006ad750` in
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/{functions.jsonl,disassembly.asm}`
and the old Ghidra functions/references/symbols index. `evidence.json` pins the
original PE, index inputs, exact decoded instructions/body SHA256 values,
references, registry entries and containing-range checks. The independent
Capstone decode matches every existing listing instruction byte in the five
bounded regions. Both recovered VAs and the callback had no accepted registry
owner or registered containing body; all tracked run source matches were
declarations/calls in313. The canonical character search exists in
`source/recovered/Porsche.exe/formatter_search.cpp` and is reused; its missing
registry entry is not treated as permission to reimplement it.

`file_device_name_00568e90(path)` calls the existing original character search
`005a2780(path,0x7c)`. A separator match returns0. Otherwise it returns the full
EAX result from `00591760`, not merely AL. `00591760` masks its helper result to
eight bits, returns0 for zero, otherwise subtracts `0x40` in32 bits. Controlled
helper byte1 therefore yields `ffffffc1`, not `000000c1`.

`resource_device_327.cpp` supplies one full-width prefix core,
`resource_device_prefix_full_00591760`, and preserves the existing
`disk_path_device_00591760` byte-return declaration through an AL adapter. The
adapter is not another original body. The disk caller `005919a0` stores AL at
`00591a86`; the route caller forwards the full result at `00568eae`. Existing
`files.hpp`/`disk_open.hpp` declarations are reused without editing those files.

`resource_drive_letter_005916a0` remains an explicit external byte-return
boundary. The original111B helper writes AL on both return paths and calls
`GetFullPathNameA`/`CharUpperA`; upper EAX bits are not a return contract. No
Win32 path/drive behavior or state provider is invented here.

## Native verification

```powershell
py -3 scripts/research/verify-v2-resource-device-327.py --attempt 4 --negative-controls
```

Attempt004 is immutable. Use a new positive attempt ID for another run. Receipt:
`local/experiments/v2-resource-open-327/004/receipt.json`, pinned by
`summary.json`. It records current source/header/script, original PE,
canonical search TU, toolchain DLLs, explicit CRT/import libraries, actual
transitive headers, real COFF, commands, logs, objects/executables and hashes.
An initial dependency probe discovers headers before the authoritative compile;
input guards run before and after compilation/link/execution.

The fixture keeps the original route-to-prefix call. It redirects only the
unrecovered letter helper and the shared recording search entry. The latter
calls the exact canonical search TU compiled with a fixture-only symbol rename.
Tests cover all256 low-byte helper values with four different upper-EAX
patterns; full prefix EAX and legacy AL; eight path shapes at four alignments,
including separator placement and a separator after NUL. Comparisons assert
argument identity, search character, branch/call trace, EAX, ESP and EBX/ESI/EDI/
EBP preservation. Three source mutations fail: missing search/branch,
truncated full-EAX result, and subtracting `0x41` instead of `0x40`.

Attempts001–003 preserve fixture-link failures: omitted OLDNAMES import library,
then unrelated locale-comparison dependencies from the whole canonical search
TU, including the unsuccessful `/Gy /OPT:REF` attempt. Final fixture provides
only explicit test-local zero cells/fail-fast functions for those unused locale
dependencies; they are outside the exercised call graph and are not production
providers. No failure of a recovered algorithm was hidden or retried.

## Callback boundary and retained HOLD

Fresh REA325/001 used one persistent server PID189684 and unchanged SHA-identical
PE copy. Its procedure query reports `00561ce0` as `not_in_procedure`, while its
entry/last-instruction and276-byte read agree exactly with the original PE and
the local decode. This confirms a function-entry coverage gap rather than
missing instruction bytes. Both wrapper `00561ca0` and sibling `00561e00` push
the callback address at `00561cd1`/`00561e31`. Returns are `00561d79`,
`00561dc1`, `00561df3`; neighboring padding is NOP90. The bounded supplemental
navigation record is `research/binary-index/resource-open-callback-327.json`;
no global catalog rewrite/count update was made.

The proven callback ABI is cdecl `(uint32 group, void* context)` with raw
pointer EAX return. Context offsets00/08/0c are path/allocation flags/diagnostic
flag; offset04 is unread. The original snapshots the path before opening,
opens with mode1 and the incoming group, sizes at `group-1`, then reads flags
from context+08 and calls the canonical allocator. Successful allocation reads
the exact reported size at offset0, ignores the read result, closes the handle,
then reloads mutable transform cell `006ad750`. A transform receives
`(buffer,saved_path,saved_flags)`; a null result frees the original buffer,
while a nonnull result replaces the return value without a local free.

Allocation failure reloads context+0c, optionally diagnoses line210, closes
the handle, and returns0. Open failure optionally diagnoses line218 and returns0
without closing. Detailed call sites, stack slots and mutable-read timing are
in `evidence.json`. Existing owners cover open/read/size/close, allocation/free,
dispatcher00568d50, size callback00561be0, group005df770 and diagnostic cells.
Neither accepted size callback nor pointer retyping of the dispatcher supplies
this distinct open behavior.

`006ad750` is a zero-initialized4B cell with one indexed absolute read. Its
accepted storage owner, setter, complete shared layout and indirect/bulk
writers are **UNKNOWN**. A zero initial value is not proof of an immutable
callback or permission to create a loose production provider. Callback
implementation, its mutable boundary integration and real OS device/path
behavior remain **HOLD**. Next safe work is a separately coordinated original
open-wrapper/callback fixture with canonical callees and explicit transform
storage boundary; no approximation or size-leaf substitution is authorized.

Evidence reproduction (read-only PE/index; writes only327/local artifacts):

```powershell
py -3 local/experiments/v2-resource-open-327/collect.py
py -3 local/experiments/v2-resource-open-327/finalize_evidence.py
```

The first collector assertion assumed CC padding; the raw PE showed NOP90.
One attempted edit failed PowerShell quoting and left that assertion unchanged.
The final collector checks the actual90 bytes. This was corrected before
creating the supplemental index artifact. Game/visual/full-system acceptance is
not claimed by static evidence or the isolated native packet.

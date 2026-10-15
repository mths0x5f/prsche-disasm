# Run211 — two bounded direct-call declaration contracts

Frozen isolated candidates. Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Scope is only208's failed caller00565cd0→callee00590290 and caller00565e70→
callee00565ea0. Exact/interior canonical ownership and WIP definitions were
checked for all four VAs. No implementation owner exists;00565cd0's probe
boundary remains separate. Index/catalog navigation and original PE-checked
instructions establish the two call boundaries; no source signature is guessed.

The four complete indexed bodies total277 bytes.127 original instructions,
including the small nested00590070 input-seam inspection, are verified against
the immutable PE. Original00565d07 is preceded by PUSH ECX/PUSH EAX and followed
by ADD ESP,8 and TEST EAX,EAX. Callee00590290 is exactly`33c0c3`: XOR EAX,EAX;
RET0, with no consumed stack/register inputs. Both caller-supplied raw32 slots
are locally unused. Its forward declaration changes only from
`undefined4 FUN_00590290(void)` to
`undefined4 __cdecl FUN_00590290(uint,undefined4)`.

Original00565e93 receives PUSH0/PUSHEAX and is followed by ADD ESP,8/RET0.
Callee00565ea0 saves ESI/EDI then loads EDI from[ESP+0xc], exactly entry
stack+4. It reads the pointed dword at+0 and signed byte at+4; it has no other
local ESP memory read, never consumes entry stack+8, and both local exits
use RET0. EAX is returned untransformed by the caller. The declaration changes
from`undefined4 FUN_00565ea0(int*)` to
`undefined4 __cdecl FUN_00565ea0(void*,undefined4)`. The void* parameter is a
proved raw pointer32 boundary accepted for this isolated experiment; it does
not assert a pointee type, source class or object lifetime. The second raw32
slot remains explicitly unused. Existing undefined4 return representations
are retained. These are two specific caller-clean contracts, not blanket
prototype expansion or a hardware-argument recovery guess.

Only those two forward declarations change. Each full caller body after its
`/* VA */` marker remains byte-identical to208. Callees are not implemented or
compiled, no body cast is introduced, and shared/frozen files remain untouched.
One actual2-TU `/MP6` MSVC Win32 batch gives **two fresh i386 COFF**:00565cd0
and00565e70, exit0,1.122785 seconds, zero warnings. The exact exit/timing/log
capture is written before diagnostic attribution. All25 source/include/tool/
PE/provenance pins pass the before/after guards. The two-object standalone
frontier is8 undefined names/9 object references; no archive or union is built.

The read-only audit also checks actual generated COFF REL32 call relocations
for the two newly typed targets: each is an E8 CALL followed by native
ADD ESP,8. Native source/object hashes and symbol snapshots are preserved.
Nested full-body semantics, incidental volatile-register compatibility,
whole-caller fidelity and original/native execution comparison remain in the
validation backlog. Code generation is not behavioral acceptance.

```powershell
py -3 scripts/research/experiment-v2-direct-call-contracts-211.py
py -3 iterations/v2/001-original-recovery/runs/211-direct-call-contracts/audit.py
```

Artifacts are under`local/experiments/v2-direct-call-contracts-211`; fresh-output
guards preserve this snapshot. New source/RSP/log/JSON files use LF before SHA.
The next integration must retain the explicit new raw-call contracts when
binding callee owners; existing one-slot getC types are not silently treated
as matching native symbols. No production edit, compiler repeat, union rebuild
or commit is performed here.

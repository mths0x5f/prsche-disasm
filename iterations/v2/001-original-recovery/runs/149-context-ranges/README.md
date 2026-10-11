# Run149: context ranges and pool refill

Source: Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Binary-index queries: `00529c20`, `00529c50`, `004e4560`, `004d7da0`,
`0059eeb0`; callers include `005299f0`, `00525ec0`, `00423690`, and
`00431170`. Complete original ASM bodies and direct callees establish
the five recovered bodies; inclusive body ranges and hashes are pinned
in verification.json. No partial body is included.

`00529c20` copies second range before first range and forwards both
16-byte aggregates plus a ninth DWORD captured from second.words[0]
before either copy. Its incoming ninth argument is ignored. `00529c50`
walks pointers by four bytes, loading the next block only on exact end
equality. It writes no memory and has no source-level return contract.
The recovered walker retains volatile DWORD reads to prevent the compiler
from erasing that traversal. Direct walker cases cover empty, in-block,
one-boundary, and two-boundary traversal. A private PAGE_GUARD/VEH fixture
observes the actual native walker node-read addresses without changing
the recovered body. These reads match the original x86 memory-read trace.

`004e4560` is a scalar deleting destructor, returning its original ECX
object pointer. It captures start and end before callbacks, conditionally
releases a non-null nonempty range, and tests only flags bit zero for
object release via the canonical `0059f050`. `004d7da0` tests count zero
before multiplying count by 32 with wrapping x86 arithmetic. Its second
argument is an element count, despite the inherited name `flags`.

`0059eeb0` has no source-level result. Its previous pointer-return
declaration represented incidental EAX from lock leave and was corrected
by the coordinator. It captures page size after entering the selected
pool lock; if necessary, it captures the primary pool and heap selector,
enters that lock, and requests exactly 4096 bytes through the current
manager's allocation callback. Page size, independently, controls the
number of blocks: `(page_size-8)/(kind*8+8)` using unsigned arithmetic.
It reloads the selected page after the inner unlock, moves that page to
the used chain, and prepends every subdivided block. Null allocation and
zero stride receive no invented guards. Their original invalid-access
and divide-fault domains are not promoted to valid operation.

Private MSVC Win32 Release CMake builds two probes. The normal target
compiles all five bodies. The second target uses the explicit private
`CONTEXT_RANGES_EXTERNAL_WALK` boundary to record `00529c20`'s exact
nine-DWORD forwarding independently of the complete walker. Four seam
cases include callbacks mutating source aggregates and verify the saved
ninth DWORD. The remaining 34 cases use complete recovered bodies.
Every case compares all 28672 poisoned arena bytes, manager/page-size
globals, ordered callbacks, pointer returns where defined, original stack
cleanup and nonvolatile registers. Only two allocation-callback address
cells are normalized to source identities after native execution.

Refill cases cover existing/new pages, pool modes 0/1/2, kinds 0/1/3/31,
zero subdivisions, fixed request versus changed page-size global, changes
to manager/lock/free-page/selector during callbacks, and overlapping
page-link/lock fields. Destructor cases include null and empty ranges,
small/large/reversed spans, flags with only higher bits set, captured
bounds changed by lock callbacks, and an object whose storage aliases its
own released range. Array release covers count zero, 1/8/9 elements and
wrapping multiplication.

Canonical allocator, lock, copy, manager-wrapper and storage boundaries
remain typed and unresolved by this source. Private recording fixtures
do not claim their hidden semantics. No original global owner is guessed.
Common integration, game launch and visual acceptance are coordinator-owned.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/149-context-ranges -B local/builds/v2/context-ranges-149 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/context-ranges-149 --config Release
py -3 scripts/research/verify-v2-context-ranges.py --probe local/builds/v2/context-ranges-149/bin/Release/context_ranges_probe.exe --report-dir iterations/v2/001-original-recovery/runs/149-context-ranges
```

Result: five full functions, 38 native/original comparisons passed.
Report pins source closure, verifier, both probes, compiler/architecture,
original body/global spans and per-case fixtures/ABI checks.

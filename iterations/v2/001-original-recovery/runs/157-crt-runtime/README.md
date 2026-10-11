# Run157: CRT heap wrappers, global locks and TLS lifecycle

Original Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first queries followed Run152's five unresolved allocation/lock/error
entries through callers/callees and the full original disassembly. The packet
recovers 17 complete bodies (1054 original bytes): `005a3be5`, `005a3bf7`, `005a3c23`, `005a3b9d`,
`005ab4ab`, `005a4b7b`, `005a4ba4`, `005a4c05`, `005a53f5`, `005a5449`,
`005a545c`, `005a54c3`, `005a669e`, `005a66a7`, `005a8ea9`, `005aa9aa`,
`005abe90`. Individual ranges, lengths and original byte hashes are pinned
in `verification.json` with the complete compiled source/include closure.

Malloc preserves the captured new-handler mode, maximum request guard,
small-block lock9 path and 16-byte OS allocation rounding. Calloc preserves
wrapped 32-bit multiplication, the distinct rounded retry argument, mode reload,
HeapAlloc zero flag, and explicit original memset for small-block allocations.
Free uses the exact header lookup range and chooses small-block free or HeapFree
without introducing a host allocator. Header membership is unsigned subtraction
against a 1MiB window. Memset preserves alignment peel, DWORD stores and byte tail.

Global locks share the canonical `exit_registry` entry names and Run152 critical
section API boundaries. Four original 24-byte static lock objects have unique
owners at `006afd00/18/30/48`; table entries 1/17/9/13 alias those owners.
Only the proven table prefix through lock25 is declared; no adjacent unobserved
storage extent is claimed. Lazy allocation locks17, rechecks publication, frees
a losing allocation, unlocks17 and reloads the target cell before entering.
Native initial values, table aliases and all 96 zeroed static-lock bytes match
the original mapped image, including BSS initialization.

TLS initialization and lazy acquisition preserve failure paths, ordered writes,
the original opaque signal-table identity, thread ID and handle sentinel.
Lazy acquisition restores the captured GetLastError value only on returning
paths. Error getters return TLS block+8/+12. Release reads each owned pointer
fresh in original order, skips the shared signal table, frees the thread block,
then reloads the TLS index to clear its slot. It does not invent cleanup on failed
TLS publication or initialization. The signal-table contents remain unrecovered.

The private MSVC Win32 probes pass 1972 comparisons across 986 inputs against all 17 original
x86 bodies. Small-block allocate/free, Win32 APIs and fatal dispatch are recording
boundaries. Full arena bytes, padding, static critical-section bytes, lock table,
TLS/error/global state, returns and ordered boundary events are compared.
Pointer fields are normalized by relocation identity only. A private trace build
with `PORSCHE_CRT_MEMORY_TRACE=1` additionally compares 5568 ordered memset
destination writes, including address, width and value. The production build
has no trace macro and repeats every input independently. Cases include
allocation failures/retries, wrapped counts, alignment/tails, header edges,
publication races/rebinding, TLS failures, last-error restoration and cleanup
callbacks that mutate later fields/index. This does not prove live concurrency,
OS allocator parity or game launch.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/157-crt-runtime -B local/builds/v2/formatter-crt-runtime-157 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-crt-runtime-157 --config Release
py -3 scripts/research/verify-v2-formatter-crt-runtime.py --probe local/builds/v2/formatter-crt-runtime-157/Release/formatter_crt_runtime_probe.exe --report-dir iterations/v2/001-original-recovery/runs/157-crt-runtime
```

Run160 integration extends the proven canonical lock-table prefix to26 cells:
Run158 text conversion uses lock19 and original locale setter005a6895 uses
lock25 (PUSH19h at005a689e). Both cells are originally null; all104 prefix
bytes hash to201fb156260657e94de030a839494cc2ea1dde442715ea851578126f2f95dd4b.
Lazy/existing lock19 and25 plus unlock paths are compared. This is not a
claim about the full original table extent.

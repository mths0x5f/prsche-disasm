# Run152: CRT lowio initialization and descriptor lifecycle

Source: `Porsche.exe`, SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Seven complete indexed bodies: `005a953e` (444 bytes), `005ab4c6` (291),
`005ab5e9` (124), `005ab665` (127), `005ab6e4` (66), `005ab726` (95),
`005ab785` (34); total 1181 original bytes.

Navigation queries were the seven entry addresses in the Porsche function/call
index, their callers, and IAT references for GetStartupInfoA, GetFileType,
GetStdHandle, SetStdHandle, SetHandleCount and critical-section operations.
Evidence is the original disassembly and the contiguous indexed ranges whose
individual byte hashes are recorded in `verification.json`.

The implementation uses the existing canonical 64-bank table at `006c01e0`,
limit at `006c02e0`, and app type at `005e52cc`. Records have original stride36;
bank allocations are 0x480 bytes. Initialization preserves untouched bytes,
signed inherited-count clamping, the handle-array address computed from the
unclamped count, failed allocation truncation, inherited pipe flags, standard
handle type flags, and SetHandleCount's return. A null OS handle is not rejected
by a new guard. Allocation returns with the descriptor critical section held;
it does not mark the descriptor open. Attach/detach preserve flags and ignore
SetStdHandle failure exactly as the original. Detach does not call CloseHandle.
Invalid descriptor paths set errno9 and doserrno0 in the original call order.
The table is reread after relevant external boundaries, including lazy locking
and SetStdHandle.

The private MSVC Win32 probe passes 1049 original-x86/native-C++ comparisons:
returns, all allocated record bytes including poison padding, all64 table
cells, handle limit, error cells, and ordered boundary calls. Cases include
negative/zero and bank-boundary inherited counts, 2048/2050 clamping, allocation
failures, missing inheritance pointers, file-type variants, mutable inherited
payload, full descriptor exhaustion, critical-section races, invalid descriptor
IDs, standard-handle failure, and callback-driven table rebinding, including an
allocator address difference of -36 that advances to the next bank. Original
nonvolatile registers and caller stack are checked on returning paths.

Malloc, fatal dispatch, global CRT locks, per-thread error cells and Win32 calls
remain explicit recording boundaries. This verifies these seven complete bodies,
not live concurrency, live OS inheritance, the broader CRT, or game launch.
Lock/unlock inputs are allocated nonnegative descriptors because the original
entries contain no validation. The probe supplies canonical storage fixtures;
production must use the existing storage owner rather than duplicate definitions.

Reproduce from repository root:

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/152-crt-lowio -B local/builds/v2/formatter-lowio-152 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-lowio-152 --config Release
py -3 scripts/research/verify-v2-formatter-lowio.py --probe local/builds/v2/formatter-lowio-152/Release/formatter_lowio_probe.exe --report-dir iterations/v2/001-original-recovery/runs/152-crt-lowio
```

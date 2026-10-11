# Run140 — formatter bootstrap and fatal closure

Porsche.exe SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Six complete indexed bodies: `005abee8`, `005a2e22`, `005a9736`,
`005a976f`, `005a0f5d`, `005a247f`. This is an isolated recovery packet;
the common registry and build are owned by the coordinator.

Queries: `005abee8`, `005a2e22`, `005a0f5d`, `005e5788/578c/5794`
in `research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl`,
`calls.jsonl`, and `references.jsonl`, then their callers/callees in
`research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm`.
The private verifier pins original module SHA, indexed call edges, function
byte ranges/hashes and the complete disassembly hash.

Confirmed behavior:

- The nine-byte `005abee8` entry calls fatal message2. Native C++ has separate
  float/text/assignment/sign adapters for incompatible callback signatures.
  They represent one original address; their native pointer equality is not
  original-address equality. Float and text public symbols resolve Run138's
  initial-storage dependencies without executing a replacement fatal handler.
- `005a0f5d` writes six cells in original order: `578c→5a3e8d`,
  `5788→5a41e3`, `5790→5a3ef3`, `5794→5a3e33`, `5798→5a3edb`,
  `579c→5a41e3`; EAX returns the conversion function address. The missing
  three cells are owned in this packet. Their initial PE targets are `005abee8`.
  Runtime float bodies remain explicit typed unresolved dependencies.
- Fatal `005a2e22` emits the header only for mode1, emits its message, then
  calls mutable exit cell `005e52c8` with255. It has no RET after that call.
  Header `005a9736` accepts mode1 or mode0/app1, emits252, reads the optional
  hook after that emission, invokes it, and emits255. Each message rereads mode.
- Message `005a976f` scans18 entries ending at `005e6008`, then compares the
  readable zero DWORD there. Code0 therefore reaches a null text rather than
  an invented unknown-message guard. Valid messages use either GetStdHandle(-12)
  and WriteFile, or the exact program-name/error-dialog construction. Name
  lengths above59 use the final59 bytes with the first3 overwritten by `...`.
- `005a247f` forwards `(code,1,0)` to recovered `005a2490`.
  Initial error mode/hook are zero, app type is2, and exit cell targets247f.

Verification compares original x86 bodies in Unicorn with the native MSVC Win32
probe,94 cases: all18 messages in console/dialog modes, mode/app predicates, unknown
codes, all four typed initial adapters, optional hook and hook mode mutation,
path lengths0..259 including the59/60 threshold, module-name failure, writer
pointer identities/order/return, and quick-exit forwarding. Output/state/event
order match. Original return stack and callee-saved registers are checked;
incidental EAX for void bodies is not a fabricated return contract.
Initial native storage identities are checked before any test override.
Bootstrap write order is pinned by the original memory-write trace and source
assignment sequence; the native probe checks final identities and return.

Boundary limits: OS, string copy/concat/copy-n, dialog and shutdown calls are
recording fixtures. They prove call inputs/order, not those callees' recovery.
Length005a6730 executes its real recovered/original bodies in both versions.
The runtime float targets are never called. Message0/null pointers, malformed
strings and nonterminated module-name output are outside the valid domain.
No live CRT initialization, game launch or visual acceptance is claimed.

Reproduce:

```powershell
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' -S iterations/v2/001-original-recovery/runs/140-formatter-bootstrap -B local/builds/v2/formatter-bootstrap-140 -A Win32
& 'local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe' --build local/builds/v2/formatter-bootstrap-140 --config Release
py -3 scripts/research/verify-v2-formatter-bootstrap.py --probe local/builds/v2/formatter-bootstrap-140/Release/formatter_bootstrap_probe.exe --report-dir iterations/v2/001-original-recovery/runs/140-formatter-bootstrap
```

Next: bind these six bodies and new cells into the common target, recover
string005aa4e0/005aa4f0/005a28a0 and dialog005acfb9, then recover float
consumer closure and lowio005a953e. Existing runs and game data are untouched.

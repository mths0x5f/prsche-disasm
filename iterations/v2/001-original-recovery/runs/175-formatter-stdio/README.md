# Run175 — stdio printf locking and temporary buffers

Ready body packet; production integration requires the canonical lock-prefix
expansion described below. Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first queries:173 game-link005a177b diagnostic consumers; complete bodies,
callers and callees at005a177b/3719/376b/533e/53cb/76a1/36ea/373c.
Eight unregistered bodies,504 original bytes. Canonical132/157/166
owners and FILE20 storage are reused; no host printf implementation is added.

Confirmed: static FILE lock IDs28..47, inclusive pointer bounds through last
FILE start (including unaligned interior pointers), dynamic critical section
at+32, stdout/stderr temporary4096-byte buffers with embedded2-byte allocation
failure fallback, allocation counter increment before existing-buffer tests,
word/byte-preserving flag updates and exact post-write reloads.

Canonical157 lock storage is currently a26-entry proven prefix. Original
192-byte prefix through47 is independently required and all added cells are
zero. Root must expand canonical owner after reviewing its evidence;175 does
not define a duplicate lock table or edit157. Omitted exit005a36d6 is outside
this initial approved ownership, pending separate index/closure evidence.

Bodies:005a177b(65),005a36ea(47),005a3719(35),005a373c(47),
005a376b(35),005a533e(141),005a53cb(42),005a76a1(92).

Private MSVC19.44 Win32 Release passes4152 original-Unicorn cases and3375
ordered boundary snapshots. Complete640-byte FILE20 storage,16384-byte
poisoned arenas, buffer cells, counter, returns and cdecl stack/nonvolatile/DF
are compared. Cases cover signed lock indexes, exact pointer bounds,
malloc failure/reuse, flags and counter wrap, write failure/short writes,
and callbacks mutating descriptor/global state before caller reloads. Printf
receives eight actual native x86 varargs, validated at the raw-va parser call.

Canonical malloc/locks/is-character-device/write/parser are scripted typed
boundaries in this private proof; their algorithms remain with their existing
owners. No whole formatted-output composition or live-game/visual acceptance
is claimed. Root integration may execute their real composition separately.
The eight owned bodies contain no SEH or floating-point operations.

The verifier independently checks all192 prefix bytes, four HIGHLOW cells
005e57ac/57cc/57dc/57ec and original static targets006afd00/30/48/18.
It pins generic lock initialization/selection bodies and all index references.
No other canonical public data alias overlaps this prefix. The current private
report records published prefix26 and production_ready=false; integration must
rerun with --require-canonical-lock-prefix after root expands the existing
157 header/storage to at least48 entries. No total table extent is claimed.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/175-formatter-stdio -B local/builds/v2/formatter-stdio-175 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-stdio-175 --config Release
py -3 scripts/research/verify-v2-formatter-stdio.py --probe local/builds/v2/formatter-stdio-175/bin/Release/formatter_stdio_probe.exe --report-dir local/reports/formatter-stdio-175
```

Root owns shared integration/registry/plans. Only new175 files are edited.

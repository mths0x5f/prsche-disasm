# Run166 — formatter output, lowio writes and wide encoding

Root integration169: eight new complete bodies plus the canonical132
005abf35 regression /1580 original-x86 comparisons.
Private MSVC Win32 build passes. Source Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Index queries:005a9e49/005a9eae,005a9ab8/005a9b1d,005abef1,
005abf5e/005abfb7,005abf35,005a662b in functions/calls/references,
then corresponding original complete ASM and static IAT identities.
Nine complete bodies,1130 indexed bytes:005a9e49(101),005a9eae(395),
005a9ab8(101),005a9b1d(115),005abef1(68),005abf5e(89),005abfb7(105),
005abf35(41),005a662b(115). Existing formatter cleanup/parser
consumers directly require the four outer operations. These reuse canonical
152 banks/handle limits/locks,157 errno/doserrno/malloc,158 locale reader state,
147 character width and162 codepage/WideCharToMultiByte boundary.

Confirmed: unsigned handle validation; seek acceptsFFFFFFFF when GetLastError0;
seek success reloads bank before clearing bit2. Text writes expand LF to CRLF,
allow1025-byte chunks at the1024 threshold, subtract all buffered newlines
from written total even on partial write, and preserve wrapped arithmetic.
Append seek failure is ignored; flags/handle are reread afterward. Output0
uses original error5 special case, other error mapping, control-Z/device rule
and errno28 fallback. Descriptor allocation count increments before malloc;
failure uses inline+14 buffer,2-byte capacity. Wide encoding holds canonical
locale reader/lock19 protocol and rejects used-default results with errno42.

Mapper005a662b reuses all45 original error pairs at005e5a20..005e5b87,
including the duplicate error6 whose first entry wins, then unsigned fallback
ranges19..36→13,188..202→8,else22. New allocation count006afcf8 starts0;
all other state/OS identities have canonical owners. The include is asserted
byte-for-byte against the original360 bytes.

Verification compares defined EAX, including descriptor/error pointer returns,
complete65536-byte poisoned arena, all ordered API/CRT/atomic/lock effects,
exact WriteFile payloads and wide input arguments, descriptor/global effects,
and original nonvolatile registers/cdecl cleanup. Swapped banks alter both
handles and text/device flags, proving required reloads after append and OS
calls. Cases cover chunk1025, partial/failed writes, special error5, device
control-Z, all error table entries, allocation/reader wrap and cached decrement
callbacks despite callback mutation. Forced large DWORD written values are
controlled import responses used to verify signed comparisons/wrap, not claims
about actual WriteFile behavior. The report pins bodies, original data/import
identities, native PE32/MSVC, fixture inputs and quoted transitive include closure.

Hypotheses: none connected as approximations. Canonical152/157 callees and six
Kernel32 imports remain controlled recording boundaries in this packet; their
production composition/native OS execution is not proved by this private probe.
Root169 retains005abf35 solely in formatter_cleanup.cpp, exports its typed
declaration and calls it directly from this private probe. /Gy + /OPT:REF
leave the unused cleanup consumer outside this isolated probe; its three
unused stream/invalid-record globals have private null link-fixture cells. No second
implementation or second registry entry is created. Register eight new bodies;
SetFilePointer binding/common build/actual game-link are verified by169.
No shared files, frozen162 files, signal-table contents or game data changed.

```powershell
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/166-formatter-output -B local/builds/v2/formatter-output-166 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/formatter-output-166 --config Release
py -3 scripts/research/verify-v2-formatter-output.py
```

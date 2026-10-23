# Run366: original frame initialization and callbacks

Four new bodies (136 bytes) recovered:00572640..00572667,00572670..00572676,
00572680..00572686 and00572690..005726e1. Source is Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
The first unconditional00536e69 startup call now has a concrete provider;
production integration now compiles195 TUs/8 projects:214 unresolved names/221
references,no EXE. One name closes with no new dependency. Shared acceptance is
recorded in validation.json.

Index navigation used exact addresses/cell operands in existing indexed assembly,
catalog entries, declarations and consumers. The three omitted callback bodies
are complete contiguous indexed instructions ending RET and equal raw PE bytes.
`research/binary-index/supplemental/frame-callbacks-366.jsonl` records these bodies
and the previously omitted6-byte005727b0 JMP[005debe8] reader discovered through
the full PE HIGHLOW scan. The reader is oracle/navigation only and is not a new
C++ provider or recovery count. REA362 frameinit evidence is reused; partial365
was not retried or called auditedPASS.

`state-evidence.json` pins initial layout, ownership, ABI and relocation sites.
New005deab8 file data is zero,006a644c is loader-zeroed virtual.data, and all
three callback cells originally contain005367b0. Opaque uintptr_t cells hold
native canonical/function addresses rather than original VAs. Existing renderer,
display, gate and364 cursor x/y storage are extern only.00572640 copies all three
limits, returns copied z in EAX; INC/DEC preserve modulo2^32 counter behavior and
leave EAX undefined.00572690 uses width/height, zeros bounds and counter, enables
the existing gate and installs decrement/increment/copy addresses.

Shared native attempt003 PASS:60 original/C++ cases and1080 return/state checks
at each of /Od and /O2 (120 comparisons total), with four detected mutations.
Checks cover initial production cells before overrides, raw callback defaults
before native relocation, high-bit values, all copied fields/used return,
wraparound counters, callback target identity, original tail-jump transport,
and staged init/decrement/increment/copy state. There are no function calls
inside the four original bodies; chain invocations are explicitly fixture setup.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/366-frame-init/native-config.json --attempt 3
```

Receipt: `local/experiments/v2-frame-init-native-366/003/receipt.json`.
Attempt001 passed normal comparisons but stopped because ExitProcess did not
flush the differential marker.002 passed; its arithmetic mutation merged two
identical functions under ICF and was first detected by identity.003 changes
only that mutation to +=2 and detects counter state directly; accepted production
and fixture source are unchanged from002. All attempts are retained.

No e0/e4 production reader, direct caller of005727b0, concurrency or computed
alias proof is claimed. The fixture invokes exact known targets through their
individual signatures; no homogeneous callback ABI is invented. Full startup,
actual callback execution, display, input and gameplay acceptance remain open.
No changes to361 ABI declarations, immutable originals or root integration files.

# Run376: original global-flags heap maximum

New original entry00569a90..00569aca (59 bytes) is supplied through the existing
typed startup_sequence_value_00569a90 facade. It delegates to canonical
application_heap_measure_00569ad0 with the existing374 flags005deb60; no scan,
arena or production state is duplicated. Root owns production integration.

Source is Porsche.exe SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index/registry queries00569a90,00569ad0,005deb60 and006b4f20 find the new59-byte
body and accepted342 helper. The new original bytes[5:59] exactly equal canonical
00569ad0 bytes[4:58]; only loading flags from global memory versus the stack
argument differs. All indexed instructions equal raw PE bytes. The accepted342
source hash and original native receipt are reused and recorded in evidence.

The original selects heaps[flags&15], follows sentinel.free_next at root+32 and
each free-list link at block+16, and compares signed sizes. It tests magic4253
only after a size exceeds the current maximum. Equal, zero and negative tagged
records can therefore be skipped. It returns the selected record's reread size,
or zero if the first qualifying record is a sentinel. There is no added null,
corruption, locking or termination policy.

Shared native attempt002 passes1280 cases at each of /Od and /O2 (2560 total)
and detects three mutations of heap selection/result transport. Cases cover all
16 root indices, high-bit flags, immediate termination, signed extremes, ignored
equal/negative/zero sentinels, maxima order and seeded chains. EAX, ESP and all
nonvolatile registers are checked; complete flags/root/heap/block bytes must stay
unchanged. The actual342 implementation is linked into the fixture.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/376-heap-largest/native-config.json --attempt 2
```

Receipt: `local/experiments/v2-heap-largest-native-376/002/receipt.json`.
Attempt001's unrelated owner-TU link dependencies remain preserved; no native
comparison ran there.002 uses explicitly controlled extern roots/flags, with
production owners pinned rather than linking unrelated consumers or fake calls.

`evidence.json` pins raw005deb60 zero initialization, loader-zeroed006b4f20[16],
and the actual accepted374 heap.obj/render_descriptor.obj COFF definitions:
unique .bss symbols,64 and4 bytes, all zero. Their production source owners remain
heap.cpp and374. Fixture storage is checked against these initial values before
any override. All fixture links point to declared native64-byte heaps and24-byte
free blocks; raw original VAs are relocated, never dereferenced as host pointers.

Source/config/fixture are frozen after PASS. Finite valid mapped chains are the
accepted domain. Malformed/nonterminating chains, concurrent mutation and full
allocator/renderer/startup/game composition remain open.

# Run341: original queue cleanup and heap destruction

Two bodies (196 PE bytes) reuse the canonical Run340 state and existing heap/
lock/fill owners. Queue cleanup preserves chain reversal, next-before-callback,
per-free manager reload, dangling head fields and the final lock reload. Heap
destruction masks its ID, clears the captured header/slot and returns0/1.

Native attempt001:61 cases at /Od and /O2 (122 total), seven detected mutations.
State/callees are controlled fixture boundaries; full allocator composition and
arbitrary pointer/index domains remain open. The preparatory evidence's missed
fill owner is corrected: Run312/321 already supplies heap_fill_0053c290.
Game intake/audit is shared with Run342 in [Run344](../344-heap-dependencies-integration/README.md).

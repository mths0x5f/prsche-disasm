# Run369: original handler-registration sort

Restores005a112b quicksort340B,005a127f shortsort78B and005a12cd byte-swap44B
from the SHA-pinned original Porsche.exe. Registry had no owner; accepted window
registration calls005a112b directly. Index/assembly/pseudocode agree on the
8-record cutoff, midpoint pivot, bidirectional partition, signed byte-difference
comparison and deferred larger partition. The original30-entry stacks remain.
Byte swaps retain ascending overlap behavior; no host qsort/std::sort is used.

Native002 passes2687 cases at each/Od and/O2 (5374 total), four mutations detected.
The fixture executes all462 contiguous original bytes, retaining internal relative
calls. It compares all arena/guard bytes and exact comparator argument/order traces,
including INT_MIN/INT_MAX returns, duplicates/payloads, 0/1/2/7/8/9/16/31/64/128
records, widths1/2/3/4/8/13/31, three alignments and six patterns. Separate shortsort,
zero-width/null-empty and overlapping/equal-address swap cases are included.
Attempt001 stopped at a missing fixture initializer_list include, not a body
mismatch. Source/fixture/config are frozen after002; integration belongs to370.

Original module SHA256:ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
Index query:005a112b/005a127f/005a12cd plus window_handler_register0053a800 callers.
Receipt:local/experiments/v2-original-sort-native-369/002/receipt.json.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/369-original-sort/native-config.json --attempt 2
```

Invalid spans, wrapping address ranges, inconsistent/mutating comparators, stack
capacity violations and concurrency remain unaccepted; no new safety guards are
inserted. Complete game/window startup is not established by this bounded proof.

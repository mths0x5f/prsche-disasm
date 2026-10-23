# Run372: async callback and request queues

Recovers original callback00563bd0 (93B), enqueue00563c30 (64B),
dequeue00563c70 (68B), dispatch00563cc0 (105B): four VAs/330 bytes.
Porsche.exe SHA256 is
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
[evidence.json](evidence.json) records index queries, complete-body/raw-PE
equality, all11 HIGHLOW operands, exact callers and state ownership. Existing
361 pool globals and canonical heap enter/leave/free providers are reused.

`AsyncQueueView` explicitly accesses the separately owned head/tail slots:
incoming006a5bc8/cc are DWORDs, free006a5bd0/d4 are native pointers. It is a
documented C++ adapter for the original adjacent-DWORD queue ABI, not a binary
alias or claim of C++ object contiguity. No new state owner exists. Callback
keeps the existing two-argument cdecl scheduler ABI, ignores inputs and returns0;
enqueue/dispatch have no EAX consumer in indexed callers.

State0 callback saves the full ID before calling record[5], then stores its
saved low byte even if the callback changed the record. Other states dispatch:
capture state under lock, change only1 to2, release lock, and only for prior1
free unsigned record[4]>1, mask the current ID, clear word6 and recycle.
Enqueue reloads the global lock for leave. Dequeue captures it after enter and
before the head write, retains the removed link and stale tail. Other record
words are untouched except for controlled external endpoint side effects.

Native003 PASS at `/Od` and `/O2`: 6,723 comparisons/329,642,145 checks per
variant, all11 semantic mutations detected. Raw complete bodies run at preserved
relative offsets with counted global/endpoint relocations. Explicit original
queue arrays map to typed C++ slots; both sides compare all arena bytes and
ordered lock/callback/free snapshots, queues, used returns, empty/single/multi
lists, stale tails, nonzero states, resource sentinels, callback injection and
mutating endpoints. A local lock-as-head dequeue case isolates unlock capture.
Real361 production state is linked and checked zero before fixture reset.

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/372-async-callbacks/native-config.json --attempt 003
```

Attempt003 is immutable; reuse its
[receipt](../../../../../local/experiments/v2-async-callbacks-native-372/003/receipt.json)
for unchanged inputs. Attempt001 passed both variants but lacked a flushed
mutation failure marker;002 detected that mutation, then Win32 installer name
heuristics rejected a mutation EXE containing `dispatch`/`patch` (error740).
003 uses neutral mutation labels. No production semantic change was needed.

Root owns registry/CMake/game integration and shared audit. This proof establishes
bounded callback/list behavior, not arbitrary malformed aliases, invalid pointers,
cyclic queues, live concurrency, scheduler/allocator composition, a linked game,
startup/display or gameplay acceptance. Passed source/proof inputs are frozen.

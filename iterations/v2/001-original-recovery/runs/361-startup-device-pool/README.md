# Run 361: startup DirectInput and async request pool

Status: integrated after bounded original/native proof. Fresh build001 compiles
193 C++ TUs/8 projects:215 unresolved names/222 references,no EXE or game execution.
Two startup names close; ten previously hidden child dependencies become visible.
Native proofs total138 comparisons/nine mutations; shared audit in validation.json.

Source: SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`
`Porsche.exe`. The binary-index query for `00536e50`, `00563ad0`, their
callers and children points to `research/v2/binaries/Porsche.exe-ddd748fdbe6d/`
and audited REA362/001. `source/recovered/functions.json` records these two
VAs as unresolved dependencies of the accepted startup caller, with no current
body owner. Both new bodies remain in this run folder.

* `00563ad0..00563bca` (251 bytes) allocates 44-byte cells, initializes
  `006a5bc0..006a5be8`, creates the canonical heap lock, and registers the
  `00563bd0` callback. Original `00563bd0` stays external. Native pool004:
  51 comparisons and 642201 byte checks on each of `/Od` and `/O2`; all six
  mutations detected. Fixture checks production BSS before setting any test
  sentinel and SHA-pins full PE strings `005bcf5c`, `005bcf68`, `005bcfa0`
  and `005bcfb4`. The diagnostic file at `005bcfa0` is retained as an opaque
  original VA in C++; native diagnostics compare its exact value. Count zero
  and allocation failure have no original guard; native
  fixture bounds the allocator to a valid arena.
* `00536e50..00537017` (456 bytes) sets up the DirectInput mouse, display
  bounds and callback. Assembly operands at `00536eb6` and `00536ecd` select
  raw data `005bf9a0` for CreateDevice and `005bf8c0` for QueryInterface.
  SHA-pinned PE bytes are respectively `602b1d6fa0d5cf11bfc7444553540000`
  and `82e644592ec9cf11bfc7444553540000`; fixture checks these bytes before
  relocation. `0053700f` loads initialized DWORD `0069e0a0` into EAX, exposed
  by a value-returning core plus the void startup facade. The property result
  writes the known overlapping cursor x word before GetCursorPos; y remains
  opaque until the API writes it. Native device005:
  18 comparisons and 19323 checks on each optimization level; all three
  mutations detected, including a swapped GUID and wrong return. The fixture
  also SHA-pins and checks raw axis GUIDs `005bf8f0..005bf91f`, all seven
  16-byte object entries `0056e950..0056e9bf`, and the 24-byte format at
  `0056e9c0` before substituting host pointers.

Original `.data` virtual range `005cb000..006c1537` extends beyond its
file-backed range ending at `005e6fff`; both state groups are in PE zero-fill.
No matching definitions were found under current production `source/`, and
the fixture asserts the new definitions' zero state before resets.

Device fixture covers success, COM stage errors, an existing device, and a
`GetCursorPos` failure paired with `ScreenToClient` failure. When GetCursorPos
does not write a point but ScreenToClient succeeds, original stack data can
include the overlapping property-success word and an uninitialized coordinate.
That branch is **HOLD**, as are actual DirectInput/OS acceptance and unrecovered
children `00572690`, `005370c0`, `005727c0`, `00537070`, `0056e940`.
The fixture's COM and Win32 endpoints prove bounded transport, not live input.

Receipts:
`local/experiments/v2-startup-device-pool-native-361/004/receipt.json` and
`local/experiments/v2-startup-device-native-361/005/receipt.json`.
Commands (use new attempt numbers for changed inputs):

```powershell
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/361-startup-device-pool/native-config.json --attempt 004
py -3 scripts/research/verify-v2-native-batch.py --config iterations/v2/001-original-recovery/runs/361-startup-device-pool/device-native-config.json --attempt 005
```

Next: finish the original frame-initialization blocker and mouse-state children
as a coherent startup continuation; trace the held cursor failure separately.
Linked EXE, actual display and menu remain unachieved.

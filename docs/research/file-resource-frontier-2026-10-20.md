# Resource-file recovery frontier after Run332

Original Porsche.exe SHA-256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries:00561b80,00533f00,00568260,005682a0,00561ca0,00561ce0,00568e90,
00591760,005916a0,005a2780 in the original Ghidra and v2 binary indices.
Fresh REA325 and333 dossiers are receipt-pinned; inferred prototypes are checked
against actual instructions/consumers rather than treated as ABI proof.

Run328 connected exists/request00561b80/00533f00 and route/prefix00568e90/
00591760 (four VAs134B),19456 native cases. Run332 adds constructor00568260
(51B) and drive-letter005916a0(111B),20736 fresh cases/six mutations. Constructor
preserves full DWORD group transport while the canonical allocator reads its
low byte. Existing formatter_search.cpp is connected whole, once: its six
support contracts already have providers.172/327 proof is reused; no duplicated
original body/provider. Actual171-TU game build:261 names/286 refs, noEXE.

Next334: open wrapper00561ca0(63B) and callback00561ce0(276B).335 game intake
follows native acceptance. These bodies can be recovered with006ad750 declared
extern and left unresolved. Storage ownership is separate from the proven
consumer algorithm; no placeholder production cell is permitted.

- Wrapper context: path+0, flags+8, value1+12; +4 stays uninitialized. Calls
  canonical device route and dispatcher00568d50 using distinct callback00561ce0.
  It is not a typed alias of size leaf00561ba0/callback00561be0.
- Callback saves path before open; flags are read after sizing; diagnostic
  flag is reread after allocation. Read return is ignored; close precedes a
  fresh transform-cell read. Only a null transform result frees the original.
-00561d59/5a/5b push flags/path/buffer,00561d5c CALL EAX,00561d60 ADD ESP,0xc;
  full EAX is treated as pointer/null. Consumer contract is
  `void* (__cdecl*)(void*, const char*, uint32_t)` in a4-byte x86 cell.
- Existing ResourceLeafAtomicCallback returns int32, so preserve raw pointer
  bits through a compatible int32 transport callback. Do not cast incompatible
  function-pointer types or add an initializer to the unread context field.
- Native fixtures must compare complete339B wrapper/callback paths, branch/
  argument order, mutable context/cell timing, raw returns, memory guards and
  ESP/nonvolatile preservation. Controlled transform storage stays test-only.

Supplemental callback navigation:
`research/binary-index/resource-open-callback-327.json`. It covers276B/three
RET sites and two address-taking callers, while REA still lacks the function
entry. Global catalog counts remain unchanged.006ad750 setters/containing
storage/HIGHLOW aliases require tracing before defining any storage provider.

Canonical filesystem/queue/concurrency composition, real Win32 path/error
behavior, ctype/locale domains, root/arena/context296/301/303 and full-game/
visual acceptance remain open. Bounded consumers do not close those holds.

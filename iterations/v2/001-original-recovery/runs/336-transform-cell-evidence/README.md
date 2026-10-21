# Run336 — transform cell006ad750 storage evidence

**Evidence-only; storage remains HOLD. No production provider is proposed.**
This packet does not define the cell or accept a complete shared layout. It
supports Run334's bounded consumer contract while keeping ownership, aliases
and writer coverage explicitly unresolved.

## Confirmed evidence

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index-first search used the Ghidra references/symbols and the v2 disassembly,
then independent section/relocation/raw-byte parsing of the original PE.
All25 indexed PE paths,24 distinct hashes, were checked against the static
inventory hashes before scanning. The separate NE module is outside this PE
scan. Existing analysis-coverage limitations are retained in `evidence.json`.

The consumer at00561d49 is `a1 50 d7 6a 00`, MOV EAX,[006ad750]. Its relocated
DWORD operand starts00561d4a. A full scan of all56,746 Porsche HIGHLOW entries
finds only that one target. A byte-alignment-independent search of the whole
file finds exactly one literal VA006ad750: the same operand. There is no other
literal address-taking, initializer or direct setter candidate for this exact
address in the scanned original. This statement does not cover computed
addresses or overlapping/bulk stores.

Across the25 PE paths, only Porsche.exe and nfs5.exe contain that VA literal.
The separate nfs5.exe variant SHA
`c318af393d4c2b7071a820ca3d69e956bbd94769b6e5c2e3e49f498ecbc94906`
has the same indexed read at00561d49, but no HIGHLOW entries. Its numeric match
is not a setter or an inter-module alias of Porsche.exe. No scanned PE contains
the little-endian DWORD literal RVA002ad750. Base-plus-offset arithmetic,
runtime relocation/patching and split immediates remain outside that result.

006ad750 lies at offset000e2750 in Porsche's readable/writable `.data` section:
VA005cb000, raw size0001c000, virtual size000f6538. It is in the virtual zero-fill
tail `[005e7000,006c1538)`, not file-backed data. Its initial four bytes are zero
from image mapping. There is no relocation whose storage site is006ad750, no
main-EXE export directory and no main-EXE TLS directory. These facts establish
initial image state, not permanent immutability or absence of DLL/CRT/runtime
writers.

## Adjacent cells and alias limits

All75 HIGHLOW targets into `[006ad700,006ad780)` resolve to existing indexed
instruction spans; this bounded relocation neighborhood has no instruction
coverage gap. The nearest labels are006ad744/748/74c/750/754/758. Direct neighbor
writes at00587ffb,00587bff/00587e63,00589922/00589929 and0058cd26/0058cd2d target
the other DWORDs, not the transform slot. Their instruction widths do not
overlap006ad750. Labels and adjacency do not prove independent storage objects
or a shared struct layout.

There are address-taking consumers at+10/+14/+18: PUSH006ad760 at0058e663 and
0058ec6a, PUSH006ad764 at0058e736 and0058ed37, PUSH006ad768 at0058f166. These feed
00597f70 or indirect vtable calls. They do not pass006ad750 directly. A complete
callee/alias/bulk-write analysis is not claimed, so these observations do not
authorize detaching the transform slot from its original surrounding memory.

An additional whole-file nearby-literal check found one non-relocated apparent
006ad703 at0052a814. It crosses the two indexed instructions `03 d7` ADD EDX,EDI
and `6a 00` PUSH0; it is not an address operand. This illustrates why raw matches
are only navigation candidates. The nearest absolute operands at006ad74c are
indexed DWORD accesses to that neighbor, not overlapping writes to006ad750.

## Consumer contract versus unknown storage

Run327's original callback evidence is reused without rerunning native tests or
REA: after close00533da0 returns,00561d49 reloads the cell,00561d51 tests it and
00561d5c calls it when nonzero. The caller pushes saved flags, saved path and
buffer, then cleans12 bytes. The proven consumer view is a four-byte pointer
to `void* __cdecl(void* buffer,const char* path,uint32 flags)`. Transform-null
frees the original allocation; a replacement pointer becomes the result.
The cell may change during earlier callbacks, so the late reload matters.

This contract does not identify an allocation/storage owner, setter, complete
initialization sequence, surrounding aggregate, address-taken aliases or all
indirect writers. Current active source search finds Run334's extern declaration
and read, with no production definition. A loose zero-initialized variable would
turn unknown state into an assumed provider and is not authorized by this scan.

## Next concrete trace

Instrument the original from main-image mapping before application/DLL/CRT
initialization, using actual loaded image base plus RVA002ad750. Watch all
writes to that aligned four-byte region through startup and resource-open flows.
For each write record instruction/module/thread, old/new DWORD, call stack,
containing write extent and source address/value. This catches direct, computed
and bulk writes that literal/index scans cannot rule out.

Correlate with consumer breakpoints at loaded base+00161d49 and+00161d5c. At the
indirect call record the loaded transform pointer and the exact three arguments;
trace its last writer and any shared memory aggregate before proposing a storage
owner. A sample with no writes proves only those exercised flows, not immutable
zero or complete program ownership. Main entry is005a2d1a, but starting only at
entry is insufficient to exclude earlier external initialization.

No new REA batch is needed merely to repeat known direct references. A future
batch should follow a concrete runtime writer/base-pointer candidate; a context
query alone cannot close the alias/writer gap. Provider/layout acceptance remains
separate from the bounded consumer implementation in Run334.

## Read-only verification

`evidence.json` pins the PE inventory, all scanned original files, relevant index
inputs, Run327 consumer evidence and the collector/auditor. It records complete
module matches, neighborhood relocations with decoded indexed instructions,
adjacent references, section data and explicit limitations. Hashes are checked
again after collection. The audit re-derives this evidence without executing or
mutating any original binary:

```powershell
py -3 scripts/research/audit-v2-transform-cell-336.py
```

The initial capture used `--capture`; existing evidence is not overwritten.
No game/native/REA session was started, no production source/storage changed,
and no full-game/visual acceptance is claimed.

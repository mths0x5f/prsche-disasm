# Run329 — original request constructor00568260

One original body: `00568260..00568292`,51 bytes, from Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
`summary.json` pins its exact body SHA, source/header, immutable native receipt,
COFF and executable. This packet closes Run326's constructor contract only;
it does not accept physical filesystem/queue behavior or a full game.

## Original evidence and owners

Index-first queries covered00568260, callers00533f00 and its four callees in
`research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/{functions,calls}.jsonl`.
REA325/001 supplies the fresh51-byte constructor dossier; its receipt, analysis
hash and evidence ID are pinned in the native record. Inferred `void` pseudocode
is rejected: the actual last call's EAX survives ADD ESP/POP/RET, and00533f00
consumes it as request ID. Registry body/interior overlap checks and recovered/
run-source searches found no accepted constructor body before implementation.

The algorithm is C++: route the saved path through00568e90; allocate type6 with
group/context/full device DWORD; call name005684e0 with the returned pointer
and saved path; call queue00568200 with that same pointer; return raw queue EAX.
It does not return the allocation pointer or normalize queue EAX to bool. There
is no local null-allocation guard; the original still calls name and queue.

Canonical route00568e90, allocator005682a0, name005684e0 and queue00568200 keep
their accepted names/types and owners. Run326's constructor declaration is
reused. Only `resource_constructor_329.cpp` and its header are accepted sources;
no global data, storage provider or replacement callee body is introduced.

## Group transport and platform ABI

At0056826c/00568276 the constructor loads/pushes the full DWORD group argument.
The accepted allocator declares its effective group as uint8_t and the original
consumer at00568309 is `8a 4c 24 18`, MOV CL,byte ptr[ESP+18h]. A normal C++
uint8_t call could zero the other24 bits before pushing, changing the original
physical argument slot seen by a controlled callee.

The internal `allocate_with_group_word` adapter explicitly pushes device,
context, full group DWORD and type6, calls the canonical allocator symbol and
cleans16 bytes. It does not retype a function pointer or alter the allocator
contract. It is x86/MSVC platform transport, not another original function.
The fixture's canonical byte-signature allocator uses a naked jump to a wide
recording hook, so original and recovered code expose the actual32-bit slot.
The effective low byte is also checked. Truncating the adapter's group push
is a detected negative control. Other platforms require their own explicit ABI
transport; this packet does not claim such portability.

Fresh REA333/001 allocator analysis independently confirms the236-byte
`005682a0..0056838b` owner and the byte load/store at00568309/00568315. Cold and
warm normalized dossiers agree, and the source SHA remains unchanged. The
separate `rea333-cross-review.json` pins those outputs/status/receipt and is
pinned by the summary. No native rerun or new allocator acceptance is claimed.

## Native proof

Attempt001 compiled the production source, fixture and three local mutant
source copies in one normal-CRT MSVC x86 `/Od /Oy-` batch. There were no failed
attempts and no successful reruns. The sole C4324 warning concerns fixture
State alignment padding; the whole state is zeroed before each comparison.
The original PE51-byte oracle is copied into private RW memory, four verified
CALL displacements are redirected to explicit fixture boundaries, then memory
is changed to RX with an instruction-cache flush.

**13,824 cases /124,431 checks PASS;3/3 mutations detected.** The four callees
are controlled recording callbacks. Cases cover four group DWORDs including
nonzero upper bits, four full-width device results, six raw queue results,
null and two distinct allocation pointers, null/empty/non-ASCII paths, null/
normal/aliased/opaque contexts and callback-mutation combinations. The callback
sequence and exact argument pointers/words, raw EAX, ESP and EBX/ESI/EDI/EBP,
full post-state and guards around path/context/both operations are compared.
Naming changes the future allocation selection and operation fields to prove
that queue receives the retained allocation pointer. Route/allocation/queue
callbacks also mutate path/context/state in matching order.

Mutant sources exist only in the local attempt: upper group bits discarded,
queue result normalized to bool, and a null-allocation early return added.
All three must differ from the original; they do not enter the game graph.
The null case proves the constructor's call sequence under controlled callees,
not graceful failure of actual name/queue implementations that may dereference
that pointer. No host filesystem substitution or fatal-path approximation is
present in production.

The receipt pins original PE/body/group-consumer bytes, REA325 evidence,
source/header/verifier and transitive compiler dependencies, toolchain DLLs,
explicit static CRT/SDK libraries, logs, all objects and EXE. Hash guards run
across compile/link/execute. COFF exposes exactly constructor00568260 and four
canonical callee references; the internal adapter adds no original VA or data.
Ownership-registry/index pins record the pre-integration baseline.

```powershell
py -3 scripts/research/verify-v2-resource-constructor-329.py --attempt 002
```

Choose an unused attempt number;001 is immutable. Native artifacts:
`local/experiments/v2-resource-constructor-329/attempt-001/`. Real callee state,
physical backend behavior, non-x86 ABI transport and full-game acceptance remain
bounded/unproven. Coordinator owns integration332 and shared plans.

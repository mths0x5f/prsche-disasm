# Supplemental candidate navigation index

`heap-live-callbacks-342.jsonl` records three previously unindexed Porsche.exe
callback entries at 00556680, 00569ad0 and 005aef20. Each entry is backed by
the original live-manager HIGHLOW relocation, exact PE bytes and a complete
decoded span ending in RET. Run342 native differential proof and supported
input domains are in `iterations/v2/001-original-recovery/runs/342-heap-live-callbacks/evidence.json`;
this file supplies navigation evidence.

`heap-consumers-271.jsonl` preserves four omitted heap-consumer **candidate** spans
from original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Run270 supplies the source evidence; Run271 rechecks all 510 PE bytes and167
instructions. Each record uses `candidate_entry_va`, `entry_status: unproved`
and `recovery_status: navigation-only`. There is deliberately no `entry_va` field.
Do not import these records as authoritative functions or accepted implementations.

Candidate ranges:005697d0..005697e6,00569a40..00569a6a,00569b10..00569b3b,
0056a1f0..0056a37f. Exact instruction bytes, hashes, nearby boundaries and known
raw incoming CALL candidates are included. No indexed incoming entry references
or relocated entry pointers are known. RET/NOP padding, closed CFG and indexed
twins support navigation, not an executable entry/liveness claim.

Table operand roles are PUSH address, indexed DWORD reads and CMP immediate.
These records do not prove allocation extent, authorize heap storage/coalescing,
repair native ABI contracts or supply a provider. **Run267 HOLD remains.**
The existing manual-functions.jsonl and full corpus remain byte-for-byte unchanged.

Next trace: establish raw incoming CALL boundaries0056a1c1/0056a483 and their
entry/control-flow context; examine0053c290 fill-dispatch consumers as needed.
The first three candidates have no known incoming direct/relocated entry evidence.

Generate once: `py -3 scripts/research/index-v2-heap-candidates-271.py`.
Read-only validation: `py -3 scripts/research/index-v2-heap-candidates-271.py --validate`.
No compiler, native execution or Ghidra is invoked; seven tamper/promotion guards
protect the candidate boundary. Run271 README/summary/validation contain provenance.

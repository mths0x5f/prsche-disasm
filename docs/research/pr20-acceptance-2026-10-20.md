# PR20 acceptance: research-only x86 lowering

Reviewed [PR20](https://github.com/xfynx/prsche-disasm/pull/20), head
`1bfa0145f7dcc78f4f525cf6046694bb48888cd1`, including its description and discussion.
It resubmits the experimental lowering tool rejected in PR2. The user authorized
finishing the corrections and merging. The original PR snapshot and the local
repair proposal remain separate under `local/experiments/pr20-review`.

During integration the author rebased onto Run321, producing head
`5e269baf5ca8750720fd64b51882e99b9b669bfc`. All five PR file blobs were compared
byte-for-byte with the reviewed head and are identical. The rebased head was
merged without rewriting published history; the already-tested maintainer
corrections were retained. No test rerun was needed for this identical input.

The new SSE/MMX lowering replaces the earlier silent no-ops, and the original
PR's native fixture passed108 fragments/110592 cases. Review nevertheless found
four observable errors absent from that input set:

- Ten-byte FLD/FSTP memory operands were silently treated as eight-byte values.
- Unordered FCOM did not set C0/C2/C3 or invalid-operation IE.
- FABS preserved the sign of negative zero.
- FSQRT computed a host result without propagating guest x87 exception/control
  state; a following FNSTSW could observe the wrong status.

The merge fixes the tested FCOM and FABS behavior, rejects unsupported ten-byte
loads/stores, and explicitly rejects FSQRT until its state model is restored.
The main verifier proves the expected rejection separately, preserves the original
fragment IDs, derives its skipped index dynamically and fails on wrong case totals.
Fresh output directories preserve attempts. The original documentation's mixed
61/108-fragment and complete-ISA claims were replaced with bounded English scope.

Final verification:

- **107 supported fragments /109568 native cases, zero mismatches**; one FSQRT
  fragment explicitly rejected. This is not108 supported fragments.
- **14 generated-code edge cases** compare FABS and FCOMPP/FNSTSW with hardware,
  including signed zero and quiet NaNs; three additional checks require rejected
  ten-byte FLD/FSTP and FSQRT.
- Full syntax census: **5674 accepted /5694 evaluated,20 rejected**. Thunks and
  multi-range functions are excluded. No claim that5674 bodies compile or run.

Commands, source hashes, frozen-base hashes, original PE/catalog, generated native
artifacts, toolchain and edge receipt are pinned in
[the validation record](pr20-validation-2026-10-20.json). Neither successful
fragments nor the census establish arbitrary x87 precision, traps, MMX/ST aliasing,
alignment-fault or non-temporal memory-order behavior. These limitations are
explicit in [the tool documentation](x86-full-isa-lowering.md).

Only research scripts and documentation are imported by this PR. The production
game remains at Run321:166 TUs compiled,266 unresolved names/295 references,
no EXE. Future original-function recovery must still use original source evidence
and meaningful native comparisons; generated C++ is a candidate, not acceptance.

# Run349: original CRT tokenizer

Original005a30ee (164 PE bytes) uses the accepted formatter_crt_thread_005a545c
provider and its+0x18 continuation. It builds a32-byte delimiter bitset including
NUL, skips leading delimiters, splits the mutable buffer and stores continuation.
There is no host strtok or second TLS storage.

Native003 passes19 original-versus-C++ cases at both /Od and /O2 (38 total),
with seven detected mutations. The fixture compares ABI, complete buffer and TLS
state, provider count, high bytes, changed delimiter sets and continued scans.
Null input with null saved continuation dereferences in the original and remains
outside bounded proof. Real CRT concurrency and full parser/game composition
remain unvalidated.

Fresh build001 compiles183 C++ TUs/8 projects:250 unresolved names/267 references,
noEXE/game execution. Tokenizer closes with no new dependency; actual COFF has
one existing CRT thread owner. Shared465-input audit PASS. REA350/002 confirms the
body in one six-query formatting session; accepted348 proof is not rerun.

```powershell
py -3 scripts/research/audit-v2-native-game-batch.py --config iterations/v2/001-original-recovery/runs/349-crt-tokenizer/acceptance.json
```

Next351 binds both heap lock names to their existing original providers after
pointer/ABI comparison. The startup report raw-VA/variadic mismatch remains HOLD.

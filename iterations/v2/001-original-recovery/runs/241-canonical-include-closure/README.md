# Run241 ? canonical include closure

New collector241 preserves frozen227 and adds ordered include_directories backed by a pinned successful compiler_execution_receipt and exact compiler_command. Quoted includes resolve in the current directory, then recorded /I roots; each resolved file must be pinned. Legacy packets retain their existing closure.
A binding-summary.json packet can use validation.binding_summary_sha256; ordinary summary.json retains validation.summary_sha256.
Pure guard tests PASS: py -3 scripts/research/test_v2_union_includes_241.py. Windows sandbox denied temporary-directory child access on first run; the same tests passed outside the sandbox. No native compiler/link/game execution in this packet. Actual canonical/source/support integration is in243.

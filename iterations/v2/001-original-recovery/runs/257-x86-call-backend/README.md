# Run257 — reusable static x86-to-C++ CALL/stack backend

The experimental [backend](../../../../../../scripts/research/x86-cpp-backend-257.py)
lowers instruction bytes to static C++ statements and labels. It adds PUSH/POP,
ADD/SUB, CALL, direct/indirect dispatch, RET cleanup, byte/word register views,
and an instruction budget to the Run246 subset. No native-code fallback is used.
Original game bodies and native equivalence are checked separately in Run258.

CALL writes the original return PC to the guest stack. The translated callee must
return that PC before the caller continues. MissingEntry, BadReturn and
BudgetExhausted stop explicitly. PUSH reads its source before changing ESP;
POP changes ESP before evaluating a memory destination. Every lowered instruction
consumes the shared budget.

Verification: four guard groups pass, including 19 fail-closed rejection cases,
stack ordering, subregister masks and instruction-boundary checks. Exact source
pins and timing are in [summary.json](summary.json).

```powershell
py -3 scripts/research/test_v2_x86_backend_257.py
```

Only CF/ZF/SF/OF are modeled. PF/AF, undefined flags, x87/SSE, exceptions,
imports, callbacks and a guest memory loader remain open. Memory and dispatch
are supplied by the isolated fixture. Recursive C++ calls also consume the host
stack; the instruction budget is not a complete recursion/fault model. Unsupported
instructions and 16-bit stack/control operations fail before compilation.
No accepted function count or production build changes in this run.

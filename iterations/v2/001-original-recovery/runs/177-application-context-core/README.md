# Run177 - complete application-context compile candidate

Original Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Ownership:004d3420 only. Accepted128/129/149 and all canonical/shared files untouched.

The full004d3420..004d55ac body is emitted as direct C++:2575 original instruction
sites covering8589 bytes, with contiguous bytes checked against the SHA-pinned PE.
Native MSVC Win32 compilation succeeds without warnings/errors. This is a compile
candidate, not accepted behavioral recovery, linked game production, or a startup
proof. No callee effects or address owners are supplied as guessed/stub definitions.

Index-first query004d3420 and its caller/callee graph finds408 direct calls to134
unique targets plus10 virtual calls. Both caller spans and final RET12 are pinned.
ECX is the accepted0x180 caller-owned context; stack args are name,stream,mode.
The source retains raw byte/DWORD views and original branches rather than trusting
the decompiler's displaced locals/unaff_retaddr. It has no PC dispatcher, runtime
instruction decoder, original-byte execution, or guessed semantic helper rewrite.

Stack analysis reaches every original instruction with zero merge conflicts and
zero final depth using actual direct-callee RET/tail cleanups. A cdecl-only hypothesis
fails at69 merges. Shadow storage preserves the original local/argument lifetimes;
source locals remain uninitialized. Original nonvolatile save slots reserve space;
native C++ ABI owns actual caller-register preservation. Partial byte writes avoid
reading unknown upper register bits. Algebraic zero/all-ones idioms avoid undefined
C++ reads while preserving their original result and consumed condition codes.

Typed machine contracts remain external:134 named per-callee effects can mutate
EAX/ECX/EDX, flags and pointed memory;10 named virtual seams additionally receive the
loaded target identity. argument_stack points to source argument zero (calleeESP+4).
52 address-view providers require pure, stable aliases of original data/code views,
with no inferred extent/storage. Canonical semantic adapters and owner bindings are
still open. COFF exposes these196 unresolved symbols plus3 MSVC runtime symbols.

Flags/x87 audit covers all418 call sites. No arithmetic condition code reaches a
body consumer before the next call; DF is live at60 seams and native x87 at5 seams.
CF/ZF/SF/OF/DF remain explicit mutable state. PF/AF have no body consumers; callee
input contracts still require separate tracing. All59 REPNE scans have an independently
checked preceding ECX=ffffffff definition and no interior branch entry. Native FLD
and FSTP execute on live hardware x87 state; no floating host-format replacement or
rounding normalization is supplied. Native/original x87 and callback proof is pending.

Constructor004d7e70 stores vtable005b6888. Raw PE CFG carving identifies omitted
slot54 target004d7fd0 (493B,RET4),slot6c004e0880 (14B,RET0),slot78004e09a0
(21B,RET0). Their complete carved ranges/returns are navigation evidence only in
virtual-target-evidence.json; no shared-index edit or body-recovery claim is made.

Reproduce:
```
py -3 scripts/research/analyze-v2-application-context-core.py
py -3 scripts/research/generate-v2-application-context-core.py
local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/177-application-context-core -B local/builds/v2/application-context-core-177 -A Win32
local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/application-context-core-177 --config Release
local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/dumpbin.exe /symbols local/builds/v2/application-context-core-177/application_context_core_candidate.dir/Release/application_context_core_candidate.obj
py -3 scripts/research/audit-v2-application-context-core.py
```
Build log goes to local/reports/v2-application-context-core-177-build.log; dumpbin
output goes to local/reports/v2-application-context-core-177-coff-symbols.txt. Audit
pins actual x86 COFF, complete source/input closure, original coverage and all open
contracts. Next step: implement proven canonical callee/global adapters, then run
branch-batched original/native state/callback/x87 comparisons before any promotion.

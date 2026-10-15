# Run207 — four original-guided callable consumers

One actual MSVC x86 `/MP6` batch compiled00540480,005404e0,00554530 and0058f1f0
into four new COFF objects, exit0, **1.7150646 seconds**, zero errors/warnings.
The observed process exit/timing are saved immediately in `logs/execution.json`;
no measured values are reconstructed or inferred from object existence.
No Ghidra, native execution, union build, production or registry edit occurs.

Original Porsche.exe SHA256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries: writes/consumers of006bd97c/006bd918/006bd984/006ad760, THRASH
export strings, loader CALL/assignment bytes, renderer export RETs, DSOUND IAT
ordinal1 and SDK IUnknown Release. The four VAs have no canonical owner and
are disjoint from frozen Run206's native candidate union.

Original00540480 and005404e0 push two raw32 arguments and call pointers at
006bd97c and006bd918. No caller stack adjustment follows; wrappers end inRET0.
00554530 calls getstate(10), saves its raw EAX inESI, calls setstate(10,1), saves
that EAX inEDI, calls setstate(10,ESI), and returnsEDI. Its stack balance proves
callee cleanup4/8; the EAX consumers establish raw32 returns. Native code retains
the three-call order, second-result return, callee cleanup and outerRET0.

Porsche00574fa0 binds006bd97c to `_THRASH_setstate@8` and006bd984 to
`_THRASH_getstate@4`, then aliases006bd918 to006bd97c. Loader/table save/restore
witnesses are retained. The three shipped renderer DLLs export those exact
entries; all local RET sites consume8/4 respectively. Every instruction in
the six exported bodies matches its immutable module PE bytes. Getstate's
omitted catalog entry fallback00574f80 is retained as exact indexed instructions
`XOR EAX,EAX; RET4`; this is evidence only, not an added recovered owner.

The selected functions therefore use per-consumer callable extern views with
raw32 stdcall arguments/EAX returns. No storage is defined and no arbitrary
function-pointer cast is used for those globals. Callback semantic state/value
types remain unknown. The new callable data symbols carry their proven type
decoration; later storage integration must retain these contracts explicitly.

For0058f1f0, the object at006ad760 is the output slot of original DSOUND
ordinal1/DirectSoundCreate setup. Original0058f1fe/200/201 loads its vtable,
pushes the object and calls vtable+8 without caller adjustment. Local SDK
IDirectSound/IUnknown declarations establish third-slot Release as stdcall,
one pointer32 argument and ULONG32 result. The only body edit replaces the
unproven no-argument `code **` view with that named callable type; its existing
object argument, target address expression, branch and subsequent zeroing are
unchanged. Native code calls the same slot with callee cleanup4 and returns0.

Three complete bodies are byte-identical to frozen203; the fourth changes only
that exact callable type. Headers assert pointer/word widths and contain externs
and typedefs only. All frozen203 sources/headers/objects remain unchanged.
Actual include closures and54 source/tool/resource/SDK/output SHA pins pass
before/after. The independent audit checks1042 original instructions:
39 selected-consumer,2 fallback,52 loader/object-creation and949 renderer-export
instructions; it also checks native stack cleanup/RET and source scope.

The standalone four-object frontier is six names/seven object references:
the three THRASH callback slots, the DirectSound object slot, and direct
dependencies0058eba0/005983b0. There are no implementations or allocations for
these dependencies in this packet. Summary rows are ordinary-packet compatible
with Run204, including actual exit0, objects/source/closure and COFF symbols.

```powershell
py -3 scripts/research/experiment-v2-pointer-calls-207.py
py -3 scripts/research/audit-v2-pointer-calls-207.py
```

The compile driver requires fresh output; the audit is read-only and repeatable.
`proof-before-compile.json` contains addresses, module SHA pins, actual original
instructions, export/SDK evidence and confirmed/hypothesis boundaries.
`summary.json` and `validation.json` retain measured native results. All new
text uses LF before hashing. Runtime provider behavior, object ownership,
complete caller/volatile-register equivalence and original hardware fidelity
remain open; inferred179 model names are not treated as ABI proof.

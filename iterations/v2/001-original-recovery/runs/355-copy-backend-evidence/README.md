# Run355: original optimized copy evidence

One shared REA session001 collects five original dossiers: dispatcher005323e0,
scalar005b0000 and missing backends005b0100/005b02c0/005b0480. The actual methods
are x87 FILD/FISTP, MMX MOVQ and SSE MOVUPS/MOVNTPS respectively. Session labels
are lookup identifiers; evidence records methods by original opcode and address.
No implementation or native acceptance is implied by decompilation.

The backends have no calls or global reads. Forward chunked load/store order
matters for overlap. The MMX body omits EMMS and its dispatcher cleans afterward;
the SSE body omits SFENCE. Native work354 must compare memory and CPU-state
boundaries, preserving those facts rather than substituting memcpy/memmove.

```powershell
py -3 scripts/research/audit-v2-rea-session.py --config iterations/v2/001-original-recovery/runs/355-copy-backend-evidence/rea-queries.json --attempt 001
```

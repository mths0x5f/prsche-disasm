# Run 238 ? data-owner cluster inventory

- Frontier233 has 305 data names at 302 unique original VAs: 299 singleton VAs and 3 multi-mangle overlap clusters; no fourth/fifth cluster exists in this scoped frontier.
- Rank 1 `006b4b20`: `?DAT_006b4b20@@3EA` + `?DAT_006b4b20@@3PAIA`, one-byte indexed view; consumers `00537b40,00537e30,0053cbc0,00562eb0,00571f90,00572f90`; pointer/byte conflict needs exact consumer tracing.
- Rank 2 `0060c95c`: signed/unsigned 4-byte mangles `...3HA`/`...3IA`; consumers `0041e2b0,0041e540,0041e590,004204f0`; exact same 4-byte span is the cleanest batching candidate.
- Rank 3 `006ad760`: `...3HA`/`...3PAHA`, same 4-byte span; consumers `0058f1f0,0058f5d0`; pointer/integer conflict remains open.
- Prior owners `005b242c,005b24a8,005e25d0,005e25d4,005ccb34,005d0608,005e5f4c` were excluded; no storage/type/layout/code inference or allocation permission.
- Next step for each cluster is exact indexed consumer read/write/address-taking trace; this report is navigation only.

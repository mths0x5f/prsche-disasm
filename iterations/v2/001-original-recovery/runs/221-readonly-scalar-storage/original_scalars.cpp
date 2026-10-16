// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
// Exact four-byte original .rdata cells. No runtime initialization or relocations.
// Formal DAT byte views must bind to these same cells if added later.
#pragma section(".orig$fc", read)
__declspec(allocate(".orig$fc")) float _DAT_005b242c = 100.0f;
__declspec(allocate(".orig$fc")) float _DAT_005b24a8 = 1.0f;
static_assert(sizeof(float) == 4 && alignof(float) == 4, "original float4 representation");

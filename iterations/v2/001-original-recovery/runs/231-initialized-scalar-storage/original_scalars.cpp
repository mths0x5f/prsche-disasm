// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Three independent original initialized int32 cells; no relative-layout claim.
#pragma section(".ogw$ns", read, write)
__declspec(allocate(".ogw$ns")) int DAT_005ccb34 = 128;
__declspec(allocate(".ogw$ns")) int DAT_005d0608 = 1;
__declspec(allocate(".ogw$ns")) int DAT_005e5f4c = 10;
static_assert(sizeof(int) == 4, "original int32 cells");

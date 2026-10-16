// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// One original writable virtual-zero-fill DWORD; signed and unsigned views share it.
#pragma section(".ogw$sv", read, write)
__declspec(allocate(".ogw$sv")) int DAT_0060c95c = 0;
static_assert(sizeof(int) == 4 && sizeof(unsigned int) == 4, "original DWORD views");

// Original Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
// Two adjacent original writable words, initially zero. No runtime initializer.
// Keep the signed/unsigned views and their original four-byte separation.
#pragma section(".ogw$sc", read, write)
__declspec(allocate(".ogw$sc")) int DAT_005e25d0 = 0;
__declspec(allocate(".ogw$sc")) unsigned int DAT_005e25d4 = 0;
static_assert(sizeof(int) == 4 && sizeof(unsigned int) == 4, "original words");

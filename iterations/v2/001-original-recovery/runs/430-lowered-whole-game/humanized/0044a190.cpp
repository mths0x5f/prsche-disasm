/* 0044a190: Stores bit 9 of its argument into the global byte at 0x00619761. */
#define flag_00619761 (*(unsigned char *)0x00619761)

void __cdecl store_bit9_0044a190(unsigned long value)
{
    flag_00619761 = (unsigned char)((value >> 9) & 1);
}

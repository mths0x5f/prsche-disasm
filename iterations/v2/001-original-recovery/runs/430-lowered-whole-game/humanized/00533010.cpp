/* 00533010: Returns byte [index] of the table at 0x005de028. */
#define table_005de028 ((unsigned char *)0x005de028)

unsigned long __cdecl table_get_005de028_00533010(unsigned long index)
{
    return table_005de028[index];
}

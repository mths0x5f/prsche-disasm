/* 00535340: entry `index` of the 14-entry dword table at 0x5de574, or -1 when out of range. */
#define t_005de574_00535340 ((unsigned long *)0x005de574)

unsigned long table_00535340(unsigned long index)
{
    if (index < 0xe)
        return t_005de574_00535340[index];
    return (unsigned long)-1;
}

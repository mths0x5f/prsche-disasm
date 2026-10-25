/* 00535360: entry n (0..6) of the dword table at 005de5ac, else zero. */
#define table_005de5ac ((unsigned long *)0x005de5ac)

unsigned long __cdecl table_entry_00535360(long index)
{
    if (index < 0 || (unsigned long)index >= 7)
        return 0;
    return table_005de5ac[index];
}

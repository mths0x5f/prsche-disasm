/* 00566d60: entry n (0..15) of the dword table at 006b7740, else zero. */
#define table_006b7740 ((unsigned long *)0x006b7740)

unsigned long __cdecl table_entry_00566d60(long index)
{
    if (index >= 0x10 || index < 0)
        return 0;
    return table_006b7740[index];
}

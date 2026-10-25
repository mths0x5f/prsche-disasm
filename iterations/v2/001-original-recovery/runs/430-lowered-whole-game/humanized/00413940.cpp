/* 00413940: bit 0 of table entry (global 0x606ac8 & 0x1f) of the dword table at 0x5e954c. */
#define g_00606ac8_00413940 (*(unsigned long *)0x00606ac8)
#define t_005e954c_00413940 ((unsigned long *)0x005e954c)

unsigned long test_00413940()
{
    return t_005e954c_00413940[g_00606ac8_00413940 & 0x1f] & 1;
}

/* 004e0780: maps 0 to 0, 1 to the global at 005d9b48 and any other value to itself. */
#define special_005d9b48 (*(unsigned long *)0x005d9b48)

unsigned long __cdecl map_value_004e0780(unsigned long v)
{
    if (v == 0)
        return 0;
    if (v == 1)
        return special_005d9b48;
    return v;
}

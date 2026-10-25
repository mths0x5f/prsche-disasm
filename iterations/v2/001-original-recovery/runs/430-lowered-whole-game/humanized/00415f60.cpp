/* 00415f60: calls 005323e0(arg2, &table[arg1], 4) with table at 00608b14. */
#define call_005323e0_from_00415f60 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005323e0)

unsigned long __cdecl call_table_00415f60(unsigned long index, unsigned long b)
{
    return call_005323e0_from_00415f60(b, 0x00608b14 + index * 4, 4);
}

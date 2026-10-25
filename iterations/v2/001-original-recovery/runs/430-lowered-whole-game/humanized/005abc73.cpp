/* 005abc73: calls 005abb07 with the two arguments and the constant 0x5e6128. */
#define call_005abb07_from_005abc73 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005abb07)

unsigned long __cdecl call_with_table_005abc73(unsigned long a, unsigned long b)
{
    return call_005abb07_from_005abc73(a, b, 0x5e6128);
}

/* 005a3192: calls 005a31a9 with the three arguments and a trailing zero. */
#define call_005a31a9_from_005a3192 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long, unsigned long))0x005a31a9)

unsigned long __cdecl call_zero_005a3192(unsigned long a, unsigned long b, unsigned long c)
{
    return call_005a31a9_from_005a3192(a, b, c, 0);
}

/* 00412190: calls 00533360 with the global at 0x5e9410 when the global at 0x5e940c is not zero. */
#define callee_00533360_00412190 ((unsigned long (__cdecl *)(unsigned long))0x00533360)
#define g_005e940c_00412190 (*(unsigned long *)0x005e940c)
#define g_005e9410_00412190 (*(unsigned long *)0x005e9410)

unsigned long call_00412190()
{
    unsigned long r = g_005e940c_00412190;
    if (r != 0)
        r = callee_00533360_00412190(g_005e9410_00412190);
    return r;
}

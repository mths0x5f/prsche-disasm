/* 00412cd0: calls 00533480 with the global at 0x5e9410 when the global at 0x5e940c is not zero. */
#define callee_00533480_00412cd0 ((unsigned long (__cdecl *)(unsigned long))0x00533480)
#define g_005e940c_00412cd0 (*(unsigned long *)0x005e940c)
#define g_005e9410_00412cd0 (*(unsigned long *)0x005e9410)

unsigned long call_00412cd0()
{
    unsigned long r = g_005e940c_00412cd0;
    if (r != 0)
        r = callee_00533480_00412cd0(g_005e9410_00412cd0);
    return r;
}

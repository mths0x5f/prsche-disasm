/* 0052f810: calls 0052f830(a, b, 0). */
#define callee_0052f830_0052f810 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x0052f830)

unsigned long forward_0052f810(unsigned long a, unsigned long b)
{
    return callee_0052f830_0052f810(a, b, 0);
}

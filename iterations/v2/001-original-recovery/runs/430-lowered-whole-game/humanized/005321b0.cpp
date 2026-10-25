/* 005321b0: calls 0056e4a0(a, b). */
#define callee_0056e4a0_005321b0 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x0056e4a0)

unsigned long forward_005321b0(unsigned long a, unsigned long b)
{
    return callee_0056e4a0_005321b0(a, b);
}

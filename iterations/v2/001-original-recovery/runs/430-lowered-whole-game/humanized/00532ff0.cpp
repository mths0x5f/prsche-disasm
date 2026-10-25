/* 00532ff0: calls 0053c290(a, 0, b). */
#define callee_0053c290_00532ff0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x0053c290)

unsigned long forward_00532ff0(unsigned long a, unsigned long b)
{
    return callee_0053c290_00532ff0(a, 0, b);
}

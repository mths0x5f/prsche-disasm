/* 00532910: calls 0056e8d1(a, b). */
#define callee_0056e8d1_00532910 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x0056e8d1)

unsigned long forward_00532910(unsigned long a, unsigned long b)
{
    return callee_0056e8d1_00532910(a, b);
}

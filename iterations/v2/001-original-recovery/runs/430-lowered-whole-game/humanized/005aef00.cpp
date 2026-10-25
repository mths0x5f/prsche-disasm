/* 005aef00: calls 005aed60(a, b, 0). */
#define callee_005aed60_005aef00 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005aed60)

unsigned long forward_005aef00(unsigned long a, unsigned long b)
{
    return callee_005aed60_005aef00(a, b, 0);
}

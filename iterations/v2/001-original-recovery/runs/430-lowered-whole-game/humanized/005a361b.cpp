/* 005a361b: calls 005a35ea(a, b, 0x40). */
#define callee_005a35ea_005a361b ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005a35ea)

unsigned long forward_005a361b(unsigned long a, unsigned long b)
{
    return callee_005a35ea_005a361b(a, b, 0x40);
}

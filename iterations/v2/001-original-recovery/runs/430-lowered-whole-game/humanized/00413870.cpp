/* 00413870: calls 00415f60(argument, 0x5e9664). */
#define callee_00415f60_00413870 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00415f60)

unsigned long forward_00413870(unsigned long a)
{
    return callee_00415f60_00413870(a, 0x005e9664);
}

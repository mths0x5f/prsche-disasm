/* 00571470: calls 005713a0(a, b). */
#define callee_005713a0_00571470 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005713a0)

unsigned long forward_00571470(unsigned long a, unsigned long b)
{
    return callee_005713a0_00571470(a, b);
}

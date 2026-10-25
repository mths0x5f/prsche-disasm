/* 005563b0: forwards its three arguments to 00556370 (b, a, c). */
#define call_00556370_from_005563b0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x00556370)

unsigned long __cdecl forward_005563b0(unsigned long a, unsigned long b, unsigned long c)
{
    return call_00556370_from_005563b0(b, a, c);
}

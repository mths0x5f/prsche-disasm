/* 005695a0: forwards its three arguments to 00562340 (a, b, c). */
#define call_00562340_from_005695a0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x00562340)

unsigned long __cdecl forward_005695a0(unsigned long a, unsigned long b, unsigned long c)
{
    return call_00562340_from_005695a0(a, b, c);
}

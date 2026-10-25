/* 00531f70: forwards its three arguments to 00531ca0 (a, b, c). */
#define call_00531ca0_from_00531f70 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x00531ca0)

unsigned long __cdecl forward_00531f70(unsigned long a, unsigned long b, unsigned long c)
{
    return call_00531ca0_from_00531f70(a, b, c);
}

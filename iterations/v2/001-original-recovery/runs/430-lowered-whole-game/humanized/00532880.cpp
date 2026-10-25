/* 00532880: forwards its three arguments to 0056e8f5 (a, b, c). */
#define call_0056e8f5_from_00532880 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x0056e8f5)

unsigned long __cdecl forward_00532880(unsigned long a, unsigned long b, unsigned long c)
{
    return call_0056e8f5_from_00532880(a, b, c);
}

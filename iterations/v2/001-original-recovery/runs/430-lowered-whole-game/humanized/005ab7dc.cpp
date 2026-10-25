/* 005ab7dc: calls 005ab7a7 with the second argument stripped of bit 19. */
#define call_005ab7a7_from_005ab7dc ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005ab7a7)

unsigned long __cdecl call_masked_005ab7dc(unsigned long a, unsigned long b)
{
    return call_005ab7a7_from_005ab7dc(a, b & 0xfff7ffff);
}

/* 00557380: Passes its argument on to the function at 0x005a2400. */
#define callee_005a2400 ((unsigned long (__cdecl *)(unsigned long))0x005a2400)

unsigned long __cdecl forward_5a2400_00557380(unsigned long value)
{
    return callee_005a2400(value);
}

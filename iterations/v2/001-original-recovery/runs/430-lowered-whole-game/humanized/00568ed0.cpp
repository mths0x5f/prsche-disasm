/* 00568ed0: Passes its argument on to the function at 0x00592490. */
#define callee_00592490 ((unsigned long (__cdecl *)(unsigned long))0x00592490)

unsigned long __cdecl forward_592490_00568ed0(unsigned long value)
{
    return callee_00592490(value);
}

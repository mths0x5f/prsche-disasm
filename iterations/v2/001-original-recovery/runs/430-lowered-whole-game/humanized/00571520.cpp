/* 00571520: Passes its argument on to the function at 0x00571490. */
#define callee_00571490 ((unsigned long (__cdecl *)(unsigned long))0x00571490)

unsigned long __cdecl forward_571490_00571520(unsigned long value)
{
    return callee_00571490(value);
}

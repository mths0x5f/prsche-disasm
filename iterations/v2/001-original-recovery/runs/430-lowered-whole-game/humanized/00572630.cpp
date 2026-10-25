/* 00572630: Passes its argument on to the function at 0x00531f90. */
#define callee_00531f90 ((unsigned long (__cdecl *)(unsigned long))0x00531f90)

unsigned long __cdecl forward_531f90_00572630(unsigned long value)
{
    return callee_00531f90(value);
}

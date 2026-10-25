/* 0056dae0: Passes its argument on to the function at 0x00531f90 (stdcall wrapper). */
#define callee_00531f90 ((unsigned long (__cdecl *)(unsigned long))0x00531f90)

unsigned long __stdcall forward_531f90_0056dae0(unsigned long value)
{
    return callee_00531f90(value);
}

/* 004c31b0: generated from the original by humanize-generate-430.py (straight-line code). */
U __stdcall function_004c31b0(U a0, U a1)
{
    U t1 = *(unsigned long *)(a1 + 0x4u);
    U t2 = *(unsigned long *)a1;
    *(unsigned long *)t1 = (unsigned long)t2;
    *(unsigned long *)(t2 + 0x4u) = (unsigned long)t1;
    U t3 = ((U (__cdecl *)(void))0x0059ecd0u)();
    *(unsigned long *)a0 = (unsigned long)t2;
    return a0;
}

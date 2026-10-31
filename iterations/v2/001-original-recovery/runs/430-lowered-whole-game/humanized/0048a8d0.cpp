/* 0048a8d0: generated from the original by humanize-generate-430.py (straight-line code). */
U __stdcall function_0048a8d0(U a0, U a1)
{
    U t1 = *(unsigned long *)(a1 + 0x4u);
    U t2 = *(unsigned long *)a1;
    *(unsigned long *)t1 = (unsigned long)t2;
    *(unsigned long *)(t2 + 0x4u) = (unsigned long)t1;
    U t3 = *(unsigned long *)0x005e4fe8u;
    U t4 = *(unsigned long *)(t3 + 0x28u);
    U t5 = (t3 + 0x28u);
    U t6 = ((U (__cdecl *)(void))0x005322b0u)();
    U t7 = *(unsigned long *)(t5 + 0x88u);
    *(unsigned long *)(a1 + 0x4u) = (unsigned long)t7;
    *(unsigned long *)(t5 + 0x88u) = (unsigned long)a1;
    U t8 = *(unsigned long *)t5;
    U t9 = ((U (__cdecl *)(void))0x005322c0u)();
    *(unsigned long *)a0 = (unsigned long)t2;
    return a0;
}

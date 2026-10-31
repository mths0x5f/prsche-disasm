/* 00523980: generated from the original by humanize-generate-430.py (straight-line code). */
struct Object_00523980 {
    U function_00523980(U a0, U a1);
};

U Object_00523980::function_00523980(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((U (__cdecl *)(U, U))0x00523c40u)(a0, a1);
    U t2 = (0u & 0xffffff00u) | ((U)((t1 & t1) != 0u) & 0xffu);
    *(unsigned long *)self = (unsigned long)t1;
    U t3 = (t1 & 0xffffff00u) | ((t2 & 0xffu) & 0xffu);
    return t3;
}

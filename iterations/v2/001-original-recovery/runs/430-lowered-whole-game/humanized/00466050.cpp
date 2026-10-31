/* 00466050: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0059f1d0_00466050 {
    U call(U, U);
};

/* the original 0059f1d0 (thiscall) */
__declspec(naked) U Call_0059f1d0_00466050::call(U, U)
{
    __asm mov eax, 0x0059f1d0
    __asm jmp eax
}

U __cdecl function_00466050(U a0, U a1)
{
    U t1 = *(unsigned long *)0x0062810cu;
    *(unsigned long *)(t1 + 0x28u) = (unsigned long)a0;
    U t2 = *(unsigned long *)0x0062810cu;
    *(unsigned long *)(t2 + 0x30u) = (unsigned long)a1;
    U t3 = *(unsigned long *)0x0062810cu;
    *(unsigned long *)(t3 + 0x40u) = (unsigned long)0x0u;
    U t4 = *(unsigned long *)0x0062810cu;
    *(unsigned long *)(t4 + 0x38u) = (unsigned long)0x6af400u;
    U t5 = *(unsigned long *)0x0062810cu;
    U t6 = ((Call_0059f1d0_00466050 *)t5)->call(0x2u, 0x2u);
    return t6;
}

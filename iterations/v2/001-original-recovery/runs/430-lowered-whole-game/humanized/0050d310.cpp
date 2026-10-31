/* 0050d310: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004d2100_0050d310 {
    U call(U, U, U);
};

/* the original 004d2100 (thiscall) */
__declspec(naked) U Call_004d2100_0050d310::call(U, U, U)
{
    __asm mov eax, 0x004d2100
    __asm jmp eax
}

U __cdecl function_0050d310(void)
{
    U t1 = *(unsigned long *)0x0065b928u;
    U t2 = ((Call_004d2100_0050d310 *)t1)->call(0x5cc804u, 0x0u, 0x1u);
    return t2;
}
